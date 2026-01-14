import azure.functions as func
import logging
import os
import json
import requests
from datetime import datetime
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

def get_env_var(name):
    val = os.environ.get(name)
    if not val:
        logging.error(f"Environment variable {name} is MISSING!")
    return val

def get_access_token():
    tenant_id = get_env_var("TENANT_ID")
    client_id = get_env_var("CLIENT_ID")
    client_secret = get_env_var("CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        raise Exception("Missing authentication credentials (TENANT_ID, CLIENT_ID, or CLIENT_SECRET)")

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=data)
    if not response.ok:
        logging.error(f"Token request failed: {response.status_code} - {response.text}")
        response.raise_for_status()
    return response.json().get("access_token")

def get_drive_details():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get Site ID
    sharepoint_site = get_env_var("SHAREPOINT_SITE")
    site_path = get_env_var("SITE_PATH")
    site_url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site}:{site_path}"
    site_res = requests.get(site_url, headers=headers)
    site_res.raise_for_status()
    site_id = site_res.json().get("id")
    
    # 2. Get Drive ID (Document Library)
    list_name = get_env_var("LIST_NAME")
    drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    drives_res = requests.get(drives_url, headers=headers)
    drives_res.raise_for_status()
    drives = drives_res.json().get("value", [])
    
    # Look for drive by name (default is 'Documents')
    drive = next((d for d in drives if d["name"] == list_name), drives[0] if drives else None)
    
    if not drive:
        raise Exception(f"Document Library '{LIST_NAME}' not found.")
        
    return drive["id"]

def sync_files_logic():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    drive_id = get_drive_details()
    
    # 3. List items in drive root
    items_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    items_res = requests.get(items_url, headers=headers)
    items_res.raise_for_status()
    items = items_res.json().get("value", [])
    
    synced_files = []
    storage_connection_string = get_env_var("STORAGE_CONNECTION_STRING")
    container_name = get_env_var("CONTAINER_NAME")
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    
    for item in items:
        if "file" in item:
            file_name = item["name"]
            file_id = item["id"]
            
            logging.info(f"Syncing file: {file_name}")
            
            # 4. Download file content
            content_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content"
            content_res = requests.get(content_url, headers=headers)
            content_res.raise_for_status()
            
            # 5. Upload to Blob Storage
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
            blob_client.upload_blob(content_res.content, overwrite=True)
            
            synced_files.append(file_name)
            
    return synced_files

@app.route(route="webhook", auth_level=func.AuthLevel.ANONYMOUS)
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('SharePoint Webhook triggered.')

    # 1. Validation Handshake
    validation_token = req.params.get('validationToken') or req.params.get('validationtoken')
    if validation_token:
        logging.info(f'Validation handshake successful: {validation_token}')
        return func.HttpResponse(validation_token, status_code=200, mimetype="text/plain")

    if req.method == "GET":
        return func.HttpResponse("Handshake listener active", status_code=200)
    # 2. Handle Notifications
    try:
        req_body = req.get_json()
        logging.info(f"Notification received: {req_body}")
        
        notifications = req_body.get('value', [])
        webhook_client_state = get_env_var("WEBHOOK_CLIENT_STATE")
        for notification in notifications:
            received_client_state = notification.get('clientState')
            logging.info(f"Received clientState: {received_client_state}, Expected: {webhook_client_state}")
            
            if received_client_state and received_client_state != webhook_client_state:
                logging.warning(f"Invalid client state received. Sync skipped.")
                continue
            
            # Trigger sync
            logging.info("Client state valid or not provided. Starting sync...")
            sync_files_logic()
            
        return func.HttpResponse("Accepted", status_code=202)
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return func.HttpResponse("Error", status_code=500)

@app.route(route="sync", auth_level=func.AuthLevel.FUNCTION)
def sync(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Manual Sync triggered.')
    try:
        results = sync_files_logic()
        return func.HttpResponse(
            json.dumps({"status": "success", "files_synced": results}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Sync failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Healthy", status_code=200)
