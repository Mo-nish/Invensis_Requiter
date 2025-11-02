#!/usr/bin/env python3
"""
Script to verify admin user creation
"""

import os
from dotenv import load_dotenv
from models_mongo import User

load_dotenv()

def verify_admin_users():
    print("🔍 Verifying Admin Users...")
    print("=" * 50)
    
    # Check default admin
    admin1 = User.find_by_email('admin@invensis.com')
    if admin1:
        print("✅ Default Admin: admin@invensis.com")
        print(f"   Name: {admin1.name}")
        print(f"   Role: {admin1.role}")
        print(f"   Active: {admin1.is_active}")
    else:
        print("❌ Default Admin not found")
    
    print()
    
    # Check your admin
    admin2 = User.find_by_email('p.monishreddy19@gmail.com')
    if admin2:
        print("✅ Your Admin: p.monishreddy19@gmail.com")
        print(f"   Name: {admin2.name}")
        print(f"   Role: {admin2.role}")
        print(f"   Active: {admin2.is_active}")
    else:
        print("❌ Your Admin not found")
    
    print()
    print("🔑 Login Credentials:")
    print("   Email: p.monishreddy19@gmail.com")
    print("   Password: Monish@007")
    print("   Admin Portal: http://localhost:5001/admin/login")

if __name__ == "__main__":
    verify_admin_users() 