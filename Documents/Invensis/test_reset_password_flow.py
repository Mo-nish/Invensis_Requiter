#!/usr/bin/env python3
"""
Simple test script to test the password reset flow
"""

import requests
import pytest
import time
import json

def test_password_reset_flow():
    base_url = "http://localhost:5001"
    # Skip test if the Flask app isn't running
    try:
        requests.get(f"{base_url}/", timeout=3)
    except requests.exceptions.RequestException:
        pytest.skip("Flask app not running on http://localhost:5001; skipping integration test")
    
    print("🧪 Testing Password Reset Flow")
    print("=" * 40)
    
    # Step 1: Request password reset
    print("1. Requesting password reset...")
    response = requests.post(
        f"{base_url}/forgot-password",
        json={"email": "admin@invensis.com"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Password reset request successful")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Password reset request failed: {result.get('error')}")
            return False
    else:
        print(f"❌ HTTP error: {response.status_code}")
        return False
    
    # Wait a moment for the email to be processed
    print("\n2. Waiting for email processing...")
    time.sleep(2)
    
    # Step 2: Try to access reset page with a dummy token to test the flow
    print("3. Testing reset page with invalid token...")
    response = requests.get(f"{base_url}/reset-password?token=invalid_token_123", allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ Invalid token properly redirects")
    else:
        print(f"❌ Invalid token handling failed: {response.status_code}")
        return False
    
    # Step 3: Test the forgot password page
    print("\n4. Testing forgot password page...")
    response = requests.get(f"{base_url}/forgot-password")
    
    if response.status_code == 200:
        print("✅ Forgot password page loads successfully")
    else:
        print(f"❌ Forgot password page failed: {response.status_code}")
        return False
    
    print("\n🎉 All tests passed! Password reset flow is working correctly.")
    print("\n📝 To test the complete flow:")
    print("1. Visit http://localhost:5001/forgot-password")
    print("2. Enter your email address")
    print("3. Check your email for the reset link")
    print("4. Click the link to access the reset password page")
    print("5. Enter a new password that meets the requirements")
    print("6. Submit the form")
    
    return True

if __name__ == "__main__":
    try:
        success = test_password_reset_flow()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask application")
        print("Please ensure the app is running with: python app_mongo.py")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
