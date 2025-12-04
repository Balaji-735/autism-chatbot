#!/usr/bin/env python3
"""
Automated Render Deployment Script
Deploys backend to Render.com using their API
"""

import requests
import json
import os
import sys
import time

RENDER_API_BASE = "https://api.render.com/v1"
FRONTEND_URL = "https://frontend-30f3yggta-balajiajai0407-6612s-projects.vercel.app"

def get_api_key():
    """Get Render API key from environment or prompt"""
    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        print("=" * 70)
        print("RENDER API KEY REQUIRED")
        print("=" * 70)
        print("\nTo deploy automatically, you need a Render API key.")
        print("1. Go to: https://dashboard.render.com/account/api-keys")
        print("2. Create a new API key")
        print("3. Run this command:")
        print("   $env:RENDER_API_KEY='your-api-key-here'")
        print("   python auto_deploy_render.py")
        print("\nAlternatively, use the web interface (no API key needed):")
        print("1. Go to: https://dashboard.render.com")
        print("2. Click 'New +' -> 'Blueprint'")
        print("3. Connect GitHub and select your repo")
        print("4. Render will auto-detect render.yaml and deploy!")
        print("=" * 70)
        return None
    return api_key

def deploy_to_render(api_key):
    """Deploy to Render using API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # First, get the owner ID
    print("Fetching account information...")
    try:
        resp = requests.get(f"{RENDER_API_BASE}/owners", headers=headers)
        resp.raise_for_status()
        owners = resp.json()
        if not owners:
            print("Error: No owners found. Please check your API key.")
            return False
        
        owner_id = owners[0].get("id") or owners[0].get("owner", {}).get("id")
        print(f"Found owner: {owner_id}")
        
        # Create a new service
        print("\nCreating Render service...")
        service_data = {
            "type": "web_service",
            "name": "autism-chatbot-backend",
            "ownerId": owner_id,
            "repo": "",  # Will be set via GitHub connection
            "branch": "master",
            "rootDir": ".",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn api_server:app --host 0.0.0.0 --port $PORT",
            "planId": "starter",  # Free tier
            "envVars": [
                {
                    "key": "PORT",
                    "value": "8000"
                },
                {
                    "key": "CORS_ORIGINS",
                    "value": FRONTEND_URL
                }
            ]
        }
        
        print("Note: Full API deployment requires GitHub repo connection.")
        print("For now, please use the web interface:")
        print("https://dashboard.render.com -> New -> Blueprint")
        print("Then connect your GitHub repository.")
        
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Automated Render Backend Deployment")
    print("=" * 70)
    
    api_key = get_api_key()
    if not api_key:
        sys.exit(1)
    
    success = deploy_to_render(api_key)
    if success:
        print("\nDeployment initiated successfully!")
    else:
        print("\nPlease use the web interface for deployment.")
        sys.exit(1)

