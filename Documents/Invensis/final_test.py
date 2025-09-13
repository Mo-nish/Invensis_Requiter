#!/usr/bin/env python3
"""
Final comprehensive test for the Invensis Hiring Portal
"""

import requests
import time

def test_application():
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Invensis Hiring Portal...")
    print("=" * 50)
    
    # Test 1: Homepage
    print("1. Testing Homepage...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Homepage accessible")
        else:
            print(f"   ❌ Homepage error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Homepage error: {e}")
    
    # Test 2: Admin Login Page
    print("\n2. Testing Admin Login Page...")
    try:
        response = requests.get(f"{base_url}/admin/login")
        if response.status_code == 200:
            print("   ✅ Admin login page accessible")
        else:
            print(f"   ❌ Admin login error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
    
    # Test 3: Admin Login (POST)
    print("\n3. Testing Admin Login...")
    try:
        login_data = {
            'email': 'p.monishreddy19@gmail.com',
            'password': 'Monish@007'
        }
        response = requests.post(f"{base_url}/admin/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("   ✅ Admin login successful (redirecting to dashboard)")
        else:
            print(f"   ❌ Admin login failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
    
    # Test 4: General Login Page
    print("\n4. Testing General Login Page...")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("   ✅ General login page accessible")
        else:
            print(f"   ❌ General login error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ General login error: {e}")
    
    # Test 5: Registration Page
    print("\n5. Testing Registration Page...")
    try:
        response = requests.get(f"{base_url}/register")
        if response.status_code == 200:
            print("   ✅ Registration page accessible")
        else:
            print(f"   ❌ Registration error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\n📱 Application URLs:")
    print(f"   Homepage: {base_url}")
    print(f"   Admin Login: {base_url}/admin/login")
    print(f"   General Login: {base_url}/login")
    print(f"   Registration: {base_url}/register")
    print("\n🔑 Admin Credentials:")
    print("   Email: p.monishreddy19@gmail.com")
    print("   Password: Monish@007")

if __name__ == "__main__":
    test_application() 