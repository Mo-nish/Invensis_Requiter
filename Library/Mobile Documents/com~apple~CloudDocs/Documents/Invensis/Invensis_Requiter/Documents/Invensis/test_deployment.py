#!/usr/bin/env python3
"""
Test script to verify deployment is working
"""

import requests
import time

def test_deployment():
    base_url = "https://invensis-requiter.onrender.com"
    
    print("🧪 Testing Render Deployment...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Message: {data.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Debug simple
    try:
        response = requests.get(f"{base_url}/debug/simple", timeout=10)
        print(f"✅ Debug simple: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Debug simple failed: {e}")
    
    # Test 4: Manager dashboard (should redirect to login)
    try:
        response = requests.get(f"{base_url}/manager/dashboard", timeout=10, allow_redirects=False)
        print(f"✅ Manager dashboard: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Correctly redirects to login (expected)")
        elif response.status_code == 500:
            print("   ❌ Still showing 500 error!")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Manager dashboard failed: {e}")
    
    print("=" * 50)
    print("✅ Deployment test completed!")

if __name__ == "__main__":
    test_deployment()
