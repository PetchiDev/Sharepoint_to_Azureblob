# Test Sync Script
# Tests the manual sync endpoint

# Parameters - UPDATE THESE
$FunctionAppName = "func-attorney-sync"
$FunctionKey = "your-function-key-here"  # Get from Azure Portal → Function → Function Keys

$SyncUrl = "https://$FunctionAppName.azurewebsites.net/api/sync?code=$FunctionKey"

Write-Host "Testing manual sync endpoint..." -ForegroundColor Cyan
Write-Host "URL: $SyncUrl" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $SyncUrl -Method Get
    
    Write-Host "✅ Sync completed successfully!" -ForegroundColor Green
    Write-Host "`nResults:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 5 | Write-Host
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "`nResponse:" -ForegroundColor Yellow
    $_.Exception.Response | Write-Host
}

Write-Host "`n✅ Test complete!" -ForegroundColor Green
