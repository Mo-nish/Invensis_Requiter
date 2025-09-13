#!/usr/bin/env python3
"""
Test script to verify modal content shows email input instead of dropdown
"""

import requests
from bs4 import BeautifulSoup

def test_modal_content():
    print("🧪 Testing Modal Content...")
    print("=" * 50)
    
    try:
        # Get the HR dashboard page
        response = requests.get("http://localhost:5001/hr/dashboard")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the modal content
            modal = soup.find('div', {'id': 'assignModal'})
            
            if modal:
                print("✅ Modal found")
                
                # Check for email input
                email_input = modal.find('input', {'type': 'email', 'id': 'managerEmail'})
                if email_input:
                    print("✅ Email input field found")
                    print(f"   Placeholder: {email_input.get('placeholder', 'Not set')}")
                else:
                    print("❌ Email input field NOT found")
                
                # Check for datetime input
                datetime_input = modal.find('input', {'type': 'datetime-local', 'id': 'interviewTime'})
                if datetime_input:
                    print("✅ Interview time input field found")
                else:
                    print("❌ Interview time input field NOT found")
                
                # Check for dropdown (should NOT exist)
                dropdown = modal.find('select', {'id': 'managerEmail'})
                if dropdown:
                    print("❌ Dropdown still exists (should be removed)")
                else:
                    print("✅ Dropdown removed (correct)")
                
                # Check for option elements (should NOT exist)
                options = modal.find_all('option')
                if options:
                    print(f"❌ {len(options)} option elements found (should be 0)")
                else:
                    print("✅ No option elements found (correct)")
                
            else:
                print("❌ Modal not found")
                
        else:
            print(f"❌ Failed to access HR dashboard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Instructions to clear browser cache:")
    print("1. Open browser developer tools (F12)")
    print("2. Right-click the refresh button")
    print("3. Select 'Empty Cache and Hard Reload'")
    print("4. Or press Ctrl+Shift+R (Cmd+Shift+R on Mac)")
    print("5. Then test the assignment modal again")

if __name__ == "__main__":
    test_modal_content() 