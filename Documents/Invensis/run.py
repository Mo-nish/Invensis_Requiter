#!/usr/bin/env python3
"""
Startup script for Invensis Hiring Portal
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_mongo import app

def main():
    """Start the application"""
    print("🚀 Starting Invensis Hiring Portal...")
    print("=" * 50)
    
    # Check if admin user exists
    try:
        from models_mongo import User
        admin_user = User.find_by_role('admin')
        if not admin_user:
            print("⚠️  No admin user found!")
            print("Please create an admin user manually.")
            print("You can still start the application, but admin features won't work.")
        else:
            print("✅ Admin user found")
    except Exception as e:
        print(f"⚠️  Could not check for admin user: {e}")
        print("The application will start, but admin features may not work.")
    
    print("✅ Application ready")
    print("🌐 Starting server...")
    print("📱 Visit: http://localhost:5001")
    print("🔧 Admin Portal: http://localhost:5001/admin/login")
    print("=" * 50)
    
    # Start the application
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Starting server on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main() 