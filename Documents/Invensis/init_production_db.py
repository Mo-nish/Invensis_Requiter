#!/usr/bin/env python3
"""
Script to initialize production database with admin user
This script runs automatically when the app starts
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_production_database():
    """Initialize production database with admin user"""
    try:
        from models_mongo import User
        
        print("🚀 Initializing production database...")
        
        # Get admin credentials from environment variables
        admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@invensis.com')
        admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'InvensisAdmin2025!')
        admin_name = os.getenv('DEFAULT_ADMIN_NAME', 'Invensis Admin')
        
        print(f"📧 Admin Email: {admin_email}")
        print(f"🔐 Admin Password: {admin_password}")
        
        # Check if admin user already exists
        existing_admin = User.find_by_email(admin_email)
        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Name: {existing_admin.name}")
            print(f"   Role: {existing_admin.role}")
            return True
        
        # Create new admin user
        admin_user = User(
            email=admin_email,
            name=admin_name,
            role='admin'
        )
        admin_user.set_password(admin_password)
        admin_user.save()
        
        print("✅ Admin user created successfully in production database!")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.name}")
        print(f"   Role: {admin_user.role}")
        print(f"   Active: {admin_user.is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing production database: {e}")
        return False

if __name__ == "__main__":
    init_production_database()
