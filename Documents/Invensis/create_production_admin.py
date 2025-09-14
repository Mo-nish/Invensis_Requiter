#!/usr/bin/env python3
"""
Script to create admin user in production MongoDB Atlas
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models_mongo import User

def create_production_admin():
    """Create admin user in production database"""
    print("🚀 Creating admin user in production database...")
    print("=" * 50)
    
    # Check if admin user already exists
    existing_admin = User.find_by_email('admin@invensis.com')
    if existing_admin:
        print("✅ Admin user already exists!")
        print(f"   Email: {existing_admin.email}")
        print(f"   Name: {existing_admin.name}")
        print(f"   Role: {existing_admin.role}")
        print(f"   Active: {existing_admin.is_active}")
        return
    
    # Create new admin user
    try:
        admin_user = User(
            email='admin@invensis.com',
            name='Invensis Admin',
            role='admin'
        )
        admin_user.set_password('InvensisAdmin2025!')
        admin_user.save()
        
        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.name}")
        print(f"   Role: {admin_user.role}")
        print(f"   Active: {admin_user.is_active}")
        
        print()
        print("🔑 Login Credentials:")
        print("   Email: admin@invensis.com")
        print("   Password: InvensisAdmin2025!")
        print("   Admin Portal: https://invensis-requiter.onrender.com/admin/login")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print("Please check your MongoDB connection and try again.")

if __name__ == "__main__":
    create_production_admin()
