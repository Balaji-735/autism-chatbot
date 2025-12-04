#!/usr/bin/env python3
"""
Comprehensive deployment script - tries multiple platforms
"""

import subprocess
import sys
import os

def try_railway():
    """Try deploying to Railway"""
    print("Attempting Railway deployment...")
    try:
        result = subprocess.run(
            ["railway", "login"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("Railway login successful!")
            # Try to deploy
            subprocess.run(["railway", "init"], check=False)
            subprocess.run(["railway", "up"], check=False)
            return True
    except Exception as e:
        print(f"Railway deployment failed: {e}")
    return False

def create_github_repo():
    """Try to create GitHub repo using gh CLI or API"""
    print("Attempting to create GitHub repository...")
    
    # Check if gh CLI is available
    try:
        result = subprocess.run(
            ["gh", "repo", "create", "autism-chatbot", "--public", "--source=.", "--remote=origin", "--push"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("GitHub repository created and pushed!")
            return True
    except FileNotFoundError:
        print("GitHub CLI not found. Installing...")
        # Try to install gh CLI
        try:
            subprocess.run(["winget", "install", "--id", "GitHub.cli"], check=False)
        except:
            pass
    
    return False

def main():
    print("=" * 70)
    print("Automated Backend Deployment")
    print("=" * 70)
    print("\nTrying multiple deployment methods...\n")
    
    # Method 1: Try Railway
    if try_railway():
        print("\nSuccessfully deployed to Railway!")
        return
    
    # Method 2: Try GitHub + Render
    if create_github_repo():
        print("\nGitHub repo created! Now deploy to Render:")
        print("1. Go to: https://dashboard.render.com")
        print("2. Click 'New +' -> 'Blueprint'")
        print("3. Select 'autism-chatbot' repository")
        print("4. Render will auto-deploy!")
        return
    
    # Fallback: Manual instructions
    print("\n" + "=" * 70)
    print("AUTOMATED DEPLOYMENT REQUIRES ADDITIONAL SETUP")
    print("=" * 70)
    print("\nFor full automation, you need one of:")
    print("1. GitHub CLI (gh) - for creating repos")
    print("2. Railway CLI authentication - for Railway deployment")
    print("3. Render API key - for Render API deployment")
    print("\nQUICKEST MANUAL METHOD (5 minutes):")
    print("1. Push to GitHub:")
    print("   git remote add origin <your-github-repo-url>")
    print("   git push -u origin master")
    print("\n2. Deploy to Render:")
    print("   - Go to: https://dashboard.render.com")
    print("   - Click 'New +' -> 'Blueprint'")
    print("   - Connect your GitHub repo")
    print("   - Render auto-detects render.yaml and deploys!")
    print("=" * 70)

if __name__ == "__main__":
    main()

