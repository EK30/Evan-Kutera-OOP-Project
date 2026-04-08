param(
    [string]$HostUrl = "http://127.0.0.1:5000",
    [string]$ItemName = "Demo-Laptop"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

function Resolve-PythonCommand {
    if (Test-Path ".\.venv\Scripts\python.exe") {
        return ".\.venv\Scripts\python.exe"
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return $py.Source
    }

    throw "Python was not found. Activate your virtual environment or install Python."
}

function Invoke-ApiJson {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Body = $null
    )

    $jsonBody = if ($Body) { $Body | ConvertTo-Json -Depth 5 } else { $null }
    $response = Invoke-WebRequest `
        -Method $Method `
        -Uri $Uri `
        -Body $jsonBody `
        -ContentType "application/json" `
        -SkipHttpErrorCheck

    $payload = $null
    if ($response.Content) {
        try {
            $payload = $response.Content | ConvertFrom-Json
        } catch {
            $payload = $response.Content
        }
    }

    return [pscustomobject]@{
        StatusCode = [int]$response.StatusCode
        Payload = $payload
    }
}

$pythonCmd = Resolve-PythonCommand
Write-Host "Using Python command: $pythonCmd" -ForegroundColor Cyan

Write-Host "`n[1/4] Running full unit tests..." -ForegroundColor Yellow
& $pythonCmd -m unittest discover inventory_system/tests
if ($LASTEXITCODE -ne 0) {
    throw "Unit tests failed. Fix tests before demo rehearsal."
}
Write-Host "Tests passed." -ForegroundColor Green

$apiOutLog = Join-Path $root "api_rehearsal.out.log"
$apiErrLog = Join-Path $root "api_rehearsal.err.log"
$apiProcess = $null

try {
    Write-Host "`n[2/4] Starting Flask API..." -ForegroundColor Yellow
    $apiProcess = Start-Process `
        -FilePath $pythonCmd `
        -ArgumentList "-m", "inventory_system.api.app" `
        -WorkingDirectory $root `
        -RedirectStandardOutput $apiOutLog `
        -RedirectStandardError $apiErrLog `
        -PassThru

    $healthUrl = "$HostUrl/health"
    $healthy = $false
    for ($i = 0; $i -lt 25; $i++) {
        Start-Sleep -Milliseconds 400
        try {
            $health = Invoke-ApiJson -Method "GET" -Uri $healthUrl
            if ($health.StatusCode -eq 200) {
                $healthy = $true
                break
            }
        } catch {
            # API may still be booting.
        }
    }

    if (-not $healthy) {
        throw "API did not become healthy at $healthUrl."
    }
    Write-Host "API health check passed." -ForegroundColor Green

    Write-Host "`n[3/4] Running demo API scenario..." -ForegroundColor Yellow
    $null = Invoke-ApiJson -Method "POST" -Uri "$HostUrl/items" -Body @{
        category   = "general"
        name       = $ItemName
        quantity   = 2
        department = "IT"
        location   = "SET 101"
    }

    $checkout1 = Invoke-ApiJson -Method "POST" -Uri "$HostUrl/items/$ItemName/checkout" -Body @{
        user     = "Student One"
        due_date = "2026-05-01"
    }

    $checkout2 = Invoke-ApiJson -Method "POST" -Uri "$HostUrl/items/$ItemName/checkout" -Body @{
        user     = "Student Two"
        due_date = "2026-05-02"
    }

    $checkout3 = Invoke-ApiJson -Method "POST" -Uri "$HostUrl/items/$ItemName/checkout" -Body @{
        user     = "Student Three"
        due_date = "2026-05-03"
    }

    $checkin = Invoke-ApiJson -Method "POST" -Uri "$HostUrl/items/$ItemName/checkin"
    $finalItem = Invoke-ApiJson -Method "GET" -Uri "$HostUrl/items/$ItemName"

    if ($checkout1.StatusCode -ne 200 -or $checkout2.StatusCode -ne 200) {
        throw "Expected first two checkouts to succeed."
    }
    if ($checkout3.StatusCode -ne 400) {
        throw "Expected third checkout to fail with 400 when out of stock."
    }
    if ($checkin.StatusCode -ne 200) {
        throw "Expected check-in to succeed."
    }
    if ($finalItem.Payload.quantity -ne 1) {
        throw "Expected quantity to be 1 after one check-in."
    }

    Write-Host "Scenario passed:" -ForegroundColor Green
    Write-Host "  Checkout #1: $($checkout1.StatusCode)"
    Write-Host "  Checkout #2: $($checkout2.StatusCode)"
    Write-Host "  Checkout #3 (expected fail): $($checkout3.StatusCode)"
    Write-Host "  Check-in: $($checkin.StatusCode)"
    Write-Host "  Final quantity: $($finalItem.Payload.quantity)"

    Write-Host "`n[4/4] Rehearsal complete. Logs:" -ForegroundColor Yellow
    Write-Host "  $apiOutLog"
    Write-Host "  $apiErrLog"
}
finally {
    if ($apiProcess -and -not $apiProcess.HasExited) {
        Stop-Process -Id $apiProcess.Id -Force
    }
}
