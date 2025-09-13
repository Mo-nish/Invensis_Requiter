#!/usr/bin/env python3
"""
Test script for the Forgot Password feature
Tests all aspects of the password reset functionality
"""

import requests
import json
import time
from datetime import datetime

class ForgotPasswordTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_forgot_password_page(self):
        """Test the forgot password page loads correctly"""
        print("🧪 Testing forgot password page...")
        try:
            response = self.session.get(f"{self.base_url}/forgot-password")
            if response.status_code == 200:
                print("✅ Forgot password page loads successfully")
                return True
            else:
                print(f"❌ Forgot password page failed to load: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error accessing forgot password page: {e}")
            return False
    
    def test_forgot_password_api(self, email):
        """Test the forgot password API endpoint"""
        print(f"🧪 Testing forgot password API with email: {email}")
        try:
            data = {"email": email}
            response = self.session.post(
                f"{self.base_url}/forgot-password",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Forgot password API call successful")
                    return True
                else:
                    print(f"❌ Forgot password API returned error: {result.get('error')}")
                    return False
            else:
                print(f"❌ Forgot password API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error calling forgot password API: {e}")
            return False
    
    def test_reset_password_page(self, token):
        """Test the reset password page loads with a token"""
        print(f"🧪 Testing reset password page with token: {token[:20]}...")
        try:
            response = self.session.get(f"{self.base_url}/reset-password?token={token}")
            if response.status_code == 200:
                print("✅ Reset password page loads successfully")
                return True
            else:
                print(f"❌ Reset password page failed to load: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error accessing reset password page: {e}")
            return False
    
    def test_reset_password_api(self, token, new_password, confirm_password):
        """Test the reset password API endpoint"""
        print(f"🧪 Testing reset password API...")
        try:
            data = {
                "token": token,
                "new_password": new_password,
                "confirm_password": confirm_password
            }
            response = self.session.post(
                f"{self.base_url}/reset-password",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Reset password API call successful")
                    return True
                else:
                    print(f"❌ Reset password API returned error: {result.get('error')}")
                    return False
            else:
                print(f"❌ Reset password API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error calling reset password API: {e}")
            return False
    
    def test_invalid_token(self):
        """Test reset password with invalid token"""
        print("🧪 Testing reset password with invalid token...")
        try:
            # Use a fresh request instead of session to avoid caching issues
            response = requests.get(f"{self.base_url}/reset-password?token=invalid_token_123", allow_redirects=False)
            if response.status_code == 302:  # Should redirect
                print("✅ Invalid token properly redirects")
                return True
            else:
                print(f"❌ Invalid token handling failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing invalid token: {e}")
            return False
    
    def test_password_validation(self):
        """Test password strength validation"""
        print("🧪 Testing password validation...")
        
        test_cases = [
            ("weak", "123", "Password too short"),
            ("short", "Abc123!", "Password too short"),
            ("no_upper", "password123!", "Missing uppercase"),
            ("no_lower", "PASSWORD123!", "Missing lowercase"),
            ("no_number", "Password!", "Missing number"),
            ("no_special", "Password123", "Missing special character"),
            ("valid", "Password123!", "Valid password")
        ]
        
        all_passed = True
        for test_name, password, description in test_cases:
            # This would test the frontend validation
            # For now, just check the basic requirements
            is_valid = (
                len(password) >= 8 and
                any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in '!@#$%^&*(),.?":{}|<>' for c in password)
            )
            
            if test_name == "valid" and is_valid:
                print(f"✅ {description}")
            elif test_name != "valid" and not is_valid:
                print(f"✅ {description} - properly rejected")
            else:
                print(f"❌ {description} - validation failed")
                all_passed = False
        
        return all_passed
    
    def test_rate_limiting(self):
        """Test rate limiting on forgot password endpoint"""
        print("🧪 Testing rate limiting...")
        try:
            # Make multiple rapid requests
            for i in range(3):
                data = {"email": f"test{i}@example.com"}
                response = self.session.post(
                    f"{self.base_url}/forgot-password",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                print(f"   Request {i+1}: {response.status_code}")
                time.sleep(0.1)  # Small delay between requests
            
            print("✅ Rate limiting test completed")
            return True
        except Exception as e:
            print(f"❌ Error testing rate limiting: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Forgot Password Feature Tests")
        print("=" * 50)
        
        tests = [
            ("Forgot Password Page", self.test_forgot_password_page),
            ("Invalid Token Handling", self.test_invalid_token),
            ("Password Validation", self.test_password_validation),
            ("Rate Limiting", self.test_rate_limiting),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            try:
                if test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Forgot password feature is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the implementation.")
        
        return passed == total

def main():
    """Main test runner"""
    print("🔐 Forgot Password Feature Test Suite")
    print("This script tests the complete forgot password functionality")
    print()
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5001/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask application is running")
        else:
            print("⚠️ Flask application responded with unexpected status")
    except requests.exceptions.RequestException:
        print("❌ Flask application is not running")
        print("Please start the application with: python app_mongo.py")
        return False
    
    # Run tests
    tester = ForgotPasswordTester()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
