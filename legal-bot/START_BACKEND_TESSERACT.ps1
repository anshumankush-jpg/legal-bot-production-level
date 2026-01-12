# Start Backend with Tesseract OCR Enabled

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STARTING BACKEND WITH TESSERACT OCR" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Add Tesseract to PATH
$env:Path += ";C:\Program Files\Tesseract-OCR"
Write-Host "✅ Tesseract added to PATH" -ForegroundColor Green

# Navigate to backend
Set-Location -Path "C:\Users\anshu\Downloads\assiii\backend"

# Start backend
Write-Host "🚀 Starting backend server..." -ForegroundColor Yellow
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
