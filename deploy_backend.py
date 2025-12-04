#!/usr/bin/env python3
"""
Backend Deployment Script
This script helps deploy the backend to Render.com
"""

import requests
import json
import os
import sys

RENDER_API_URL = "https://api.render.com/v1"
FRONTEND_URL = "https://frontend-30f3yggta-balajiajai0407-6612s-projects.vercel.app"

def deploy_to_render():
    """
    Deploy backend to Render using their API
    Requires RENDER_API_KEY environment variable
    """
    api_key = os.getenv("RENDER_API_KEY")
    
    if not api_key:
        print("=" * 60)
        print("Render API Key not found!")
        print("=" * 60)
        print("\nTo deploy automatically, you need a Render API key:")
        print("1. Go to: https://dashboard.render.com/account/api-keys")
        print("2. Create a new API key")
        print("3. Set it as environment variable:")
        print("   $env:RENDER_API_KEY='your-api-key'  # PowerShell")
        print("   export RENDER_API_KEY='your-api-key'  # Bash")
        print("\nAlternatively, use the web interface:")
        print("1. Go to: https://dashboard.render.com")
        print("2. Click 'New +' -> 'Blueprint'")
        print("3. Connect your GitHub repository")
        print("4. Render will auto-detect render.yaml and deploy!")
        print("=" * 60)
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Deploying to Render...")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    # This would require more API calls to create service
    # For now, guide user to web interface
    print("\nFor automated deployment, please use the web interface:")
    print("https://dashboard.render.com -> New -> Blueprint")
    
    return True

if __name__ == "__main__":
    print("Backend Deployment Helper")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("api_server.py"):
        print("Error: api_server.py not found. Run from project root.")
        sys.exit(1)
    
    if not os.path.exists("render.yaml"):
        print("Error: render.yaml not found.")
        sys.exit(1)
    
    deploy_to_render()

