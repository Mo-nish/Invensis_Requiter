#!/usr/bin/env python3
"""
Simple test script to test the password reset flow
"""

import requests
import time
import json

def test_password_reset_flow():
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Password Reset Flow")
    print("=" * 40)
    
    # Step 1: Request password reset
    print("1. Requesting password reset...")
    response = requests.post(
        f"{base_url}/forgot-password",
        json={"email": "admin@invensis.com"},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    assert result.get('success'), f"Password reset request failed: {result.get('error')}"
    print("✅ Password reset request successful")
    print(f"   Message: {result.get('message')}")
    
    # Wait a moment for the email to be processed
    print("\n2. Waiting for email processing...")
    time.sleep(2)
    
    # Step 2: Try to access reset page with a dummy token to test the flow
    print("3. Testing reset page with invalid token...")
    response = requests.get(f"{base_url}/reset-password?token=invalid_token_123", allow_redirects=False)
    
    assert response.status_code == 302, f"Invalid token should redirect (302), got {response.status_code}"
    print("✅ Invalid token properly redirects")
    
    # Step 3: Test the forgot password page
    print("\n4. Testing forgot password page...")
    response = requests.get(f"{base_url}/forgot-password")
    
    assert response.status_code == 200, f"Forgot password page should load (200), got {response.status_code}"
    print("✅ Forgot password page loads successfully")
    
    print("\n🎉 All tests passed! Password reset flow is working correctly.")
    print("\n📝 To test the complete flow:")
    print("1. Visit http://localhost:5001/forgot-password")
    print("2. Enter your email address")
    print("3. Check your email for the reset link")
    print("4. Click the link to access the reset password page")
    print("5. Enter a new password that meets the requirements")
    print("6. Submit the form")

if __name__ == "__main__":
    try:
        test_password_reset_flow()
        exit(0)
    except AssertionError as e:
        print(f"❌ Test assertion failed: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask application")
        print("Please ensure the app is running with: python app_mongo.py")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
