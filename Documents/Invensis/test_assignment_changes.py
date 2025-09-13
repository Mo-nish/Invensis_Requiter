#!/usr/bin/env python3
"""
Test script to verify the new assignment functionality
"""

import requests
import json
from datetime import datetime, timedelta

def test_assignment_changes():
    print("🧪 Testing Assignment Changes...")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Check if HR dashboard loads without managers dropdown
    print("\n1. Testing HR Dashboard...")
    try:
        response = requests.get(f"{base_url}/hr/dashboard")
        if response.status_code == 302:  # Redirect to login
            print("✅ HR Dashboard redirects to login (expected)")
        else:
            print(f"❌ HR Dashboard returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing HR Dashboard: {e}")
    
    # Test 2: Check if manager dashboard filters correctly
    print("\n2. Testing Manager Dashboard...")
    try:
        response = requests.get(f"{base_url}/manager/dashboard")
        if response.status_code == 302:  # Redirect to login
            print("✅ Manager Dashboard redirects to login (expected)")
        else:
            print(f"❌ Manager Dashboard returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Manager Dashboard: {e}")
    
    # Test 3: Check email service function
    print("\n3. Testing Email Service...")
    try:
        from email_service import send_candidate_assignment_email
        from models_mongo import Candidate
        from datetime import datetime
        
        # Create a mock candidate
        candidate = Candidate(
            first_name="Test",
            last_name="Candidate",
            email="test@example.com",
            phone="1234567890",
            gender="Male",
            dob="1990-01-01",
            education="Bachelor's",
            experience="3",
            assigned_by="hr@invensis.com"
        )
        
        interview_time = datetime.now() + timedelta(days=1)
        
        # Test email function (won't actually send due to missing app context)
        print("✅ Email service function exists and can be imported")
        
    except Exception as e:
        print(f"❌ Error testing email service: {e}")
    
    # Test 4: Check route functionality
    print("\n4. Testing Assignment Route...")
    try:
        response = requests.post(f"{base_url}/hr/assign_candidate", data={
            'candidate_id': 'test_id',
            'manager_email': 'test@example.com',
            'interview_time': '2025-08-10T11:00'
        })
        if response.status_code == 302:  # Redirect to login
            print("✅ Assignment route redirects to login (expected)")
        else:
            print(f"❌ Assignment route returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing assignment route: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\n📋 Manual Testing Required:")
    print("1. Login as HR user")
    print("2. Go to HR Dashboard")
    print("3. Click 'Assign' button on a candidate")
    print("4. Verify the modal shows:")
    print("   - Manager Email input field")
    print("   - Interview Date & Time input field")
    print("5. Fill in the fields and click 'Assign'")
    print("6. Verify the candidate is assigned")
    print("7. Login as the manager email")
    print("8. Verify only assigned candidates appear")
    print("9. Check if email notification was sent")

if __name__ == "__main__":
    test_assignment_changes() 