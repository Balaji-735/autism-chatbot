# Deployment Script for Autism Chatbot
# This script helps you deploy the frontend to Vercel

Write-Host "=== Autism Chatbot Deployment Helper ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend")) {
    Write-Host "Error: frontend directory not found. Please run this from the project root." -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Installing Vercel CLI..." -ForegroundColor Yellow
npm install -g vercel

Write-Host ""
Write-Host "Step 2: Deploying Frontend to Vercel..." -ForegroundColor Yellow
Write-Host "You will be prompted to:" -ForegroundColor Cyan
Write-Host "  1. Login to Vercel (or create account)" -ForegroundColor Cyan
Write-Host "  2. Link your project" -ForegroundColor Cyan
Write-Host "  3. Configure settings" -ForegroundColor Cyan
Write-Host ""

cd frontend
vercel

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host "1. After deployment, note your Vercel URL" -ForegroundColor Cyan
Write-Host "2. Deploy backend to Railway or Render (see DEPLOYMENT.md)" -ForegroundColor Cyan
Write-Host "3. Update NEXT_PUBLIC_API_URL in Vercel dashboard with your backend URL" -ForegroundColor Cyan
Write-Host "4. Update CORS in api_server.py with your Vercel URL" -ForegroundColor Cyan

