# Simple PowerShell HTTP Server for Credit Risk App
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:3000/")

Write-Host "🚀 Starting Credit Risk App Server..." -ForegroundColor Green

try {
    $listener.Start()
    Write-Host "✅ Server running at http://localhost:3000" -ForegroundColor Green
    Write-Host "📋 Your AMS560 Project is live!" -ForegroundColor Cyan
    Write-Host "🔄 Press Ctrl+C to stop" -ForegroundColor Yellow

    $htmlContent = Get-Content "credit_risk_app.html" -Raw

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $response = $context.Response
        
        $response.ContentType = "text/html"
        $response.StatusCode = 200
        
        $buffer = [System.Text.Encoding]::UTF8.GetBytes($htmlContent)
        $response.ContentLength64 = $buffer.Length
        $response.OutputStream.Write($buffer, 0, $buffer.Length)
        $response.OutputStream.Close()
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
} finally {
    if ($listener.IsListening) {
        $listener.Stop()
    }
}