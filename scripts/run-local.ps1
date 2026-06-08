# AlertSense local dev (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $Root "..")

Write-Host "Installing Python deps..."
py -m pip install -r backend/requirements.txt

Write-Host "Installing frontend deps..."
Set-Location frontend
npm install
Set-Location ..

Write-Host "Freeing port 8081 if busy..."
Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "Starting backend on :8081 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$((Get-Location).Path)'; py -m uvicorn backend.main:app --reload --port 8081"

Write-Host "Starting frontend on :5173 ..."
Set-Location frontend
npm run dev
