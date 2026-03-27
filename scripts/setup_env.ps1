param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment (.venv)..."
& $Python -m venv .venv

Write-Host "Upgrading pip..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "Installing dependencies..."
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Environment setup complete."
Write-Host "Activate with: .\.venv\Scripts\Activate.ps1"
