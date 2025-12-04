# Automated Backend Deployment Script
# Opens Render deployment page with instructions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Deployment Automation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if code is committed
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Committing remaining changes..." -ForegroundColor Yellow
    git add .
    git commit -m "Ready for deployment" -q
}

# Check if remote exists
$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "No GitHub remote found." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To deploy automatically, you need to:" -ForegroundColor Cyan
    Write-Host "1. Create a GitHub repository" -ForegroundColor White
    Write-Host "2. Add it as remote: git remote add origin <your-repo-url>" -ForegroundColor White
    Write-Host "3. Push: git push -u origin master" -ForegroundColor White
    Write-Host ""
    Write-Host "Opening GitHub repository creation page..." -ForegroundColor Green
    Start-Process "https://github.com/new"
    Write-Host ""
    Write-Host "After creating the repo, run this script again!" -ForegroundColor Yellow
    exit
}

Write-Host "GitHub remote found: $remote" -ForegroundColor Green
Write-Host ""

# Check if pushed
$localCommits = git rev-list --count HEAD 2>$null
$remoteCommits = git rev-list --count origin/master 2>$null

if ($localCommits -gt $remoteCommits) {
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    git push -u origin master 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    } else {
        Write-Host "Push failed. Please push manually." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "Opening Render deployment page..." -ForegroundColor Green
Write-Host "Render will auto-detect render.yaml and deploy automatically!" -ForegroundColor Cyan
Write-Host ""

# Open Render Blueprint page
Start-Process "https://dashboard.render.com/blueprints/new"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Instructions:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Sign in to Render (if not already)" -ForegroundColor White
Write-Host "2. Click 'Connect GitHub account' (if needed)" -ForegroundColor White
Write-Host "3. Select your repository from the list" -ForegroundColor White
Write-Host "4. Click 'Apply' - Render will auto-detect render.yaml!" -ForegroundColor White
Write-Host ""
Write-Host "Your backend will be deployed automatically!" -ForegroundColor Green
Write-Host "URL will be: https://autism-chatbot-backend.onrender.com" -ForegroundColor Cyan
Write-Host ""

