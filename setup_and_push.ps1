# Complete setup script for GitHub and Vercel deployment
# Run this script after creating the GitHub repository

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Archive Page Scraper - GitHub Setup" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if repository exists
Write-Host "Step 1: Checking Git status..." -ForegroundColor Green
git status

Write-Host "`nStep 2: Setting up remote..." -ForegroundColor Green
$remoteUrl = "https://github.com/DevelopRB/archive-page-scraper.git"

# Remove existing remote if any
git remote remove origin 2>$null

# Add remote
git remote add origin $remoteUrl
Write-Host "Remote added: $remoteUrl" -ForegroundColor Green

Write-Host "`nStep 3: Ensuring main branch..." -ForegroundColor Green
git branch -M main

Write-Host "`nStep 4: Pushing to GitHub..." -ForegroundColor Green
Write-Host "You will be prompted for GitHub credentials." -ForegroundColor Yellow
Write-Host "Username: DevelopRB" -ForegroundColor Cyan
Write-Host "Password: Use Personal Access Token (not your GitHub password)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Get token from: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Press Enter to continue with push (or Ctrl+C to cancel)"
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: https://github.com/DevelopRB/archive-page-scraper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://vercel.com/dashboard" -ForegroundColor White
    Write-Host "2. Click 'Add New...' -> 'Project'" -ForegroundColor White
    Write-Host "3. Import your GitHub repository" -ForegroundColor White
    Write-Host "4. Click 'Deploy'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Push failed. Common issues:" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Repository doesn't exist:" -ForegroundColor Yellow
    Write-Host "   Create it at: https://github.com/new" -ForegroundColor White
    Write-Host "   Name: archive-page-scraper" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Authentication failed:" -ForegroundColor Yellow
    Write-Host "   - Use Personal Access Token (not password)" -ForegroundColor White
    Write-Host "   - Get token: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "   - Select 'repo' scope" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Try SSH instead:" -ForegroundColor Yellow
    Write-Host "   git remote set-url origin git@github.com:DevelopRB/archive-page-scraper.git" -ForegroundColor White
    Write-Host ""
}

