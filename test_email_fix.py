#!/usr/bin/env python3
"""
Test script to verify email functionality is working
"""

import requests
import json

def test_email_functionality():
    """Test if email sending is working in production"""
    
    print("🧪 Testing Email Functionality...")
    print("=" * 50)
    
    # Test 1: Check if admin dashboard loads
    print("1. Testing Admin Dashboard Access...")
    try:
        response = requests.get("https://invensis-requiter.onrender.com/admin/dashboard", timeout=30)
        if response.status_code == 200:
            print("✅ Admin dashboard loads successfully")
        else:
            print(f"❌ Admin dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin dashboard error: {str(e)}")
    
    # Test 2: Check if contact support works
    print("\n2. Testing Contact Support...")
    try:
        response = requests.get("https://invensis-requiter.onrender.com/contact-support", timeout=30)
        if response.status_code == 200:
            print("✅ Contact support page loads successfully")
        else:
            print(f"❌ Contact support failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Contact support error: {str(e)}")
    
    # Test 3: Test email sending endpoint
    print("\n3. Testing Email Sending Endpoint...")
    try:
        test_data = {
            "email": "test@example.com",
            "subject": "Test Email",
            "message": "This is a test email to verify functionality"
        }
        
        response = requests.post(
            "https://invensis-requiter.onrender.com/send-contact-email",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Email sending endpoint works")
            else:
                print(f"❌ Email sending failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Email endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Email endpoint error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Email Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Login to admin dashboard")
    print("2. Add a new HR email (pramod.p@invensis-tech.com)")
    print("3. Check if invitation email is sent")
    print("4. Assign a candidate to a manager")
    print("5. Check if assignment email is sent")

if __name__ == "__main__":
    test_email_functionality()
