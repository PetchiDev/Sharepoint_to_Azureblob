# SharePoint to Azure Blob Sync: Prerequisites & Technical Setup

This document outlines the necessary prerequisites and configurations required for the client to set up and run the SharePoint to Azure Blob Storage synchronization system.

## 1. Azure Environment Prerequisites
The following resources must be created in the client's Azure subscription:

### A. Resource Group
- **Name**: `rg-attorney-sync` (or preferred name)
- **Location**: Preferred region (e.g., `East US`)

### B. Azure Storage Account
- **Name**: `stattorneysync` (must be globally unique)
- **Account Kind**: StorageV2 (General Purpose v2)
- **Access Tier**: Hot
- **Requirement**: Create a **Container** named `attorneys` (or as configured in environment variables).

### C. Azure Function App
- **Name**: `func-attorney-sync`
- **Runtime Stack**: Python 3.11
- **Operating System**: Linux
- **Plan Type**: Consumption (Serverless) - *This ensures the service is cost-effective (Free tier compatible).*

---

## 2. SharePoint Configuration
The application connects to a SharePoint site to monitor changes and download files.

### A. Document Library Setup
- **Name**: `Attorney_Documents` (or your document library name).
- **Structure**: Ensure this **Document Library** contains the files you wish to sync to Azure Blob Storage.

### B. Access Permissions
The application requires "read-only" access to the specified SharePoint site and its document libraries.

---

## 3. Azure AD App Registration (Identity)
An App Registration is required to authenticate the Azure Function with Microsoft Graph API.

### A. Create App Registration
1. Navigate to **Azure Active Directory** -> **App registrations** -> **New registration**.
2. **Name**: `SP-to-Blob-Sync-App`
3. **Supported account types**: "Accounts in this organizational directory only (Single tenant)".

### B. API Permissions (Microsoft Graph)
Add the following **Application Permissions**:
- `Sites.Read.All`: Required to resolve SharePoint site IDs.
- `Files.Read.All`: Required to download file content from document libraries.
- **IMPORTANT**: An administrator must click **"Grant admin consent for [Tenant Name]"** after adding these permissions.

### C. Authentication Credentials
Generate and copy the following for the implementation team:
- **Application (client) ID**
- **Directory (tenant) ID**
- **Client Secret**: Create a new secret under "Certificates & secrets". *Note the secret value immediately as it will be hidden later.*

---

## 4. Required Configuration (Environment Variables)
The following key-value pairs must be added to the **Azure Function App -> Configuration -> Application settings**:

| Key | Description | Example |
| :--- | :--- | :--- |
| `TENANT_ID` | Azure AD Directory ID | `00000000-0000-0000-0000-000000000000` |
| `CLIENT_ID` | Azure AD Application ID | `00000000-0000-0000-0000-000000000000` |
| `CLIENT_SECRET` | Azure AD Application Secret | `...secret...` |
| `SHAREPOINT_SITE` | SharePoint Domain | `tenant.sharepoint.com` |
| `SITE_PATH` | Path to the SharePoint site | `/sites/CompanyPortal` |
| `LIST_NAME` | Name of the SharePoint Document Library | `Attorney_Documents` |
| `STORAGE_CONNECTION_STRING` | Azure Storage Connection String | `DefaultEndpointsProtocol=https;...` |
| `CONTAINER_NAME` | Blob Container Name | `attorneys` |
| `WEBHOOK_CLIENT_STATE` | Secret key for webhook validation | `your-secure-secret-key` |

---

## 5. Local Setup Tooling (For Deployment/Maintenance)
- **Visual Studio Code** with "Azure Functions" extension.
- **Python 3.11**
- **PnP PowerShell Module** (Only if manual webhook registration is preferred):
  ```powershell
  Install-Module PnP.PowerShell
  ```

---

## Contact Support
For any technical queries regarding these prerequisites, please contact the development team.
