import os
import requests
import json

# Load local.settings.json or use environment variables
settings_path = 'local.settings.json'
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f).get('Values', {})
else:
    settings = os.environ

TENANT_ID = settings.get("TENANT_ID")
CLIENT_ID = settings.get("CLIENT_ID")
CLIENT_SECRET = settings.get("CLIENT_SECRET")
SHAREPOINT_SITE = settings.get("SHAREPOINT_SITE")
SITE_PATH = settings.get("SITE_PATH")
LIST_NAME = settings.get("LIST_NAME") # Library name, e.g., 'Documents'
WEBHOOK_URL = f"https://func-attorney-sync-h5aja9a6d8hyf4a3.centralus-01.azurewebsites.net/api/webhook"
CLIENT_STATE = settings.get("WEBHOOK_CLIENT_STATE", "MySecureWebhook2024Key!Attorney#App")

def get_access_token():
    print("Getting access token...")
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json().get("access_token")

def register_webhook():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Get Site ID
    print(f"Fetching Site ID for {SITE_PATH}...")
    site_url = f"https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_SITE}:{SITE_PATH}"
    site_res = requests.get(site_url, headers=headers)
    site_res.raise_for_status()
    site_id = site_res.json().get("id")
    
    # 2. Get Drive ID (Document Library)
    print(f"Fetching Drive ID for '{LIST_NAME}'...")
    drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    drives_res = requests.get(drives_url, headers=headers)
    drives_res.raise_for_status()
    drives = drives_res.json().get("value", [])
    
    drive = next((d for d in drives if d["name"] == LIST_NAME), drives[0] if drives else None)
    if not drive:
        print(f"Error: Library '{LIST_NAME}' not found.")
        return
    drive_id = drive["id"]

    # 3. Create Subscription (Webhook)
    print(f"Registering webhook for Drive ID: {drive_id}...")
    sub_url = "https://graph.microsoft.com/v1.0/subscriptions"
    
    from datetime import datetime, timedelta, timezone
    expiration = (datetime.now(timezone.utc) + timedelta(days=29)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    payload = {
        "changeType": "updated",
        "notificationUrl": WEBHOOK_URL,
        "resource": f"drives/{drive_id}/root",
        "expirationDateTime": expiration,
        "clientState": CLIENT_STATE
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    res = requests.post(sub_url, headers=headers, json=payload)
    
    if res.status_code == 201:
        print("✅ Webhook registered successfully for Document Library!")
        print(json.dumps(res.json(), indent=2))
    else:
        print(f"❌ Error registering webhook: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("Error: Please ensure credentials are set in local.settings.json")
    else:
        try:
            register_webhook()
        except Exception as e:
            print(f"An error occurred: {e}")
