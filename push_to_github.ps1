# PowerShell script to push to GitHub
# Run this AFTER creating the repository on GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if remote exists
$remoteExists = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Adding remote origin..." -ForegroundColor Green
    git remote add origin https://github.com/DevelopRB/archive-page-scraper.git
}

# Ensure we're on main branch
Write-Host "Checking branch..." -ForegroundColor Green
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host "You may be prompted for GitHub credentials." -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step: Deploy to Vercel" -ForegroundColor Yellow
    Write-Host "Go to: https://vercel.com/dashboard" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR: Push failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "1. Repository doesn't exist - Create it at: https://github.com/new" -ForegroundColor White
    Write-Host "2. Authentication failed - Use Personal Access Token" -ForegroundColor White
    Write-Host "3. Check repository URL is correct" -ForegroundColor White
}

