#!/usr/bin/env powershell
# =============================================================
#  RUN.ps1 — Start AISU Project (Frontend + Backend)
# =============================================================

Write-Host "`n"
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AISU Project Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "login.html")) {
    Write-Host "❌ Error: login.html not found" -ForegroundColor Red
    Write-Host "Make sure you're running this from the project root directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Project directory confirmed`n" -ForegroundColor Green

# Start frontend web server in background
Write-Host "[1/2] Starting Frontend Web Server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 8000" -WindowStyle Normal

Start-Sleep -Seconds 2

# Start backend
Write-Host "[2/2] Starting Backend on port 5000...`n" -ForegroundColor Yellow

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AISU Backend v2.1" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Frontend: http://localhost:8000" -ForegroundColor Green
Write-Host "✓ Backend:  http://localhost:5000" -ForegroundColor Green
Write-Host "✓ Login:    http://localhost:8000/login.html" -ForegroundColor Green
Write-Host ""

Set-Location backend
& python app.py
