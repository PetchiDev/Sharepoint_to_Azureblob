# SharePoint Webhook Registration Script
# Run this once after deploying your Azure Function

# Parameters - UPDATE THESE
$SiteUrl = "https://kryptossupport.sharepoint.com/sites/CompanyPortal"
$ListName = "Detailed_Dummy_List"
$WebhookUrl = "https://func-attorney-sync.azurewebsites.net/api/webhook"
$ClientState = "attorney-sync-secret-key"

# Install PnP PowerShell if not already installed
if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    Write-Host "Installing PnP.PowerShell module..." -ForegroundColor Yellow
    Install-Module -Name PnP.PowerShell -Force -Scope CurrentUser
}

# Import module
Import-Module PnP.PowerShell

# Connect to SharePoint
Write-Host "Connecting to SharePoint..." -ForegroundColor Cyan
Connect-PnPOnline -Url $SiteUrl -Interactive

# Check existing webhooks
Write-Host "Checking existing webhooks..." -ForegroundColor Cyan
$existingWebhooks = Get-PnPWebhookSubscriptions -List $ListName

if ($existingWebhooks) {
    Write-Host "Found existing webhooks:" -ForegroundColor Yellow
    $existingWebhooks | Format-Table -Property Id, NotificationUrl, ExpirationDateTime
    
    $response = Read-Host "Do you want to delete existing webhooks and create new one? (Y/N)"
    if ($response -eq 'Y') {
        foreach ($webhook in $existingWebhooks) {
            Write-Host "Deleting webhook $($webhook.Id)..." -ForegroundColor Yellow
            Remove-PnPWebhookSubscription -List $ListName -Identity $webhook.Id -Force
        }
    }
}

# Register new webhook
Write-Host "Registering new webhook..." -ForegroundColor Cyan
$expirationDate = (Get-Date).AddMonths(5)

try {
    $webhook = Add-PnPWebhookSubscription `
        -List $ListName `
        -NotificationUrl $WebhookUrl `
        -ExpirationDate $expirationDate `
        -ClientState $ClientState
    
    Write-Host "✅ Webhook registered successfully!" -ForegroundColor Green
    Write-Host "Webhook ID: $($webhook.Id)" -ForegroundColor Green
    Write-Host "Notification URL: $($webhook.NotificationUrl)" -ForegroundColor Green
    Write-Host "Expiration: $($webhook.ExpirationDateTime)" -ForegroundColor Green
    Write-Host "`n⚠️ Remember: Webhook will expire on $expirationDate" -ForegroundColor Yellow
    Write-Host "The auto-renewal function will handle this automatically." -ForegroundColor Yellow
    
}
catch {
    Write-Host "❌ Error registering webhook: $_" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. Function app is deployed and running" -ForegroundColor Yellow
    Write-Host "2. Webhook URL is accessible" -ForegroundColor Yellow
    Write-Host "3. You have permissions to create webhooks" -ForegroundColor Yellow
}

# Disconnect
Disconnect-PnPOnline
Write-Host "`n✅ Done!" -ForegroundColor Green
