# SharePoint to Azure Blob Storage Sync

Event-driven sync system that automatically syncs attorney details from SharePoint to Azure Blob Storage using webhooks.

## Features
- ✅ Real-time sync via SharePoint webhooks (5-10 sec latency)
- ✅ Daily backup sync as safety net
- ✅ Automatic webhook renewal (every 5 months)
- ✅ Efficient JSON storage format
- ✅ 100% FREE on Azure free tier
- ✅ Production-ready with error handling

## Architecture
```
SharePoint List → Webhook → Azure Function → Azure Blob Storage
```

## Prerequisites
1. Azure subscription (free tier)
2. SharePoint site with attorney list
3. Azure AD app registration with Sites.Read.All permission
4. VS Code with Azure Functions extension (for deployment)

## SharePoint List Schema
Create a list named **"Attorney Details"** with the following columns:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Title** | Single line of text | Full Name of the Attorney (Mandatory) |
| **BarNumber** | Single line of text | Unique Bar Registration Number |
| **PracticeArea** | Choice | e.g., Corporate, Litigation, Criminal, IP |
| **Email** | Single line of text | Work Email Address |
| **Phone** | Single line of text | Contact Number |
| **OfficeLocation** | Single line of text | City or Office Branch |
| **Bio**| Multiple lines of text | Professional Summary |
| **Status** | Choice | Active / Inactive |

## Setup Instructions

### 1. Azure Resources
```bash
# Create resource group
az group create --name rg-attorney-sync --location centralindia

# Create storage account
az storage account create --name stattorneysync --resource-group rg-attorney-sync --location centralindia --sku Standard_LRS

# Create function app
az functionapp create --name func-attorney-sync --resource-group rg-attorney-sync --storage-account stattorneysync --runtime python --runtime-version 3.11 --os-type Linux --consumption-plan-location centralindia
```

### 2. Environment Variables
Set these in Azure Portal → Function App → Configuration:
```
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
SHAREPOINT_SITE=kryptossupport.sharepoint.com
SITE_PATH=/sites/CompanyPortal
LIST_NAME=Detailed_Dummy_List
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
CONTAINER_NAME=attorneys
WEBHOOK_CLIENT_STATE=your-secret-key
```

### 3. Deploy Function
```bash
# Using VS Code
1. Open project folder
2. Press Ctrl+Shift+P
3. Select 'Azure Functions: Deploy to Function App'
4. Select your function app

# Or using Azure CLI
func azure functionapp publish func-attorney-sync
```

### 4. Register Webhook
```powershell
Install-Module -Name PnP.PowerShell
Connect-PnPOnline -Url 'https://kryptossupport.sharepoint.com/sites/CompanyPortal' -Interactive

$webhookUrl = 'https://func-attorney-sync.azurewebsites.net/api/webhook'
Add-PnPWebhookSubscription -List 'Detailed_Dummy_List' -NotificationUrl $webhookUrl -ExpirationDate (Get-Date).AddMonths(5) -ClientState 'your-secret-key'
```

## Endpoints

### Webhook (Auto-triggered)
- **URL**: `https://func-attorney-sync.azurewebsites.net/api/webhook`
- **Method**: POST
- **Auth**: Anonymous (SharePoint validates via clientState)
- **Purpose**: Receives SharePoint change notifications

### Manual Sync
- **URL**: `https://func-attorney-sync.azurewebsites.net/api/sync?code={key}`
- **Method**: GET/POST
- **Auth**: Function key
- **Purpose**: Manual bulk sync

### Health Check
- **URL**: `https://func-attorney-sync.azurewebsites.net/api/health`
- **Method**: GET
- **Auth**: Anonymous
- **Purpose**: Verify function app is running

## Monitoring

1. **Azure Portal**
   - Function App → Monitor → View execution logs
   - Check success/failure rates

2. **Storage Explorer**
   - Verify JSON files in `attorneys` container
   - Check file format and content

3. **Cost Analysis**
   - Azure Portal → Cost Management
   - Should show ₹0 for free tier usage

## Troubleshooting

### Webhook not triggering
```powershell
# Check webhook status
Get-PnPWebhookSubscriptions -List 'Attorney Details'

# If expired, re-register
Add-PnPWebhookSubscription -List 'Attorney Details' -NotificationUrl $webhookUrl -ExpirationDate (Get-Date).AddMonths(5) -ClientState 'your-secret-key'
```

### Authentication errors
- Verify TENANT_ID, CLIENT_ID, CLIENT_SECRET
- Ensure admin consent granted for API permissions
- Check app registration not expired

### Blob upload fails
- Verify STORAGE_CONNECTION_STRING
- Check container exists
- Ensure storage account not locked

## Cost Estimate
- **Azure Functions**: ₹0 (FREE - under 1M executions)
- **Blob Storage**: ₹0 (FREE - under 5GB)
- **Total**: ₹0/month

## License
MIT

## Support
For issues, contact your Azure administrator or refer to Microsoft documentation.
