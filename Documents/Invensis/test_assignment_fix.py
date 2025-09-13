#!/usr/bin/env python3
"""
Test script to verify assignment functionality is working
"""

import requests
import json

def test_assignment():
    print("🧪 Testing Assignment Functionality...")
    print("=" * 50)
    
    # Test data
    test_data = {
        'candidate_id': '68944296f0b3e0d347cf1bf9',  # Use a real candidate ID
        'manager_email': 'test.manager@invensis.com',
        'interview_time': '2025-08-10T14:00'
    }
    
    try:
        # Test the assignment endpoint
        response = requests.post(
            'http://localhost:5001/hr/assign_candidate',
            data=test_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📋 Response Data: {data}")
                
                if data.get('success'):
                    print("✅ Assignment successful!")
                else:
                    print(f"❌ Assignment failed: {data.get('message', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print("❌ Response is not JSON")
                print(f"📄 Response text: {response.text}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing assignment: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Login to the application")
    print("2. Go to HR Dashboard")
    print("3. Try assigning a candidate")
    print("4. Check if the modal shows email input (not dropdown)")
    print("5. Verify the assignment works without 'Candidate not found' error")

if __name__ == "__main__":
    test_assignment() 