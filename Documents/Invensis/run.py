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
    
    # Initialize production database with admin user
    try:
        from init_production_db import init_production_database
        print("🔧 Initializing production database...")
        if init_production_database():
            print("✅ Production database initialized successfully!")
        else:
            print("⚠️  Could not initialize production database")
    except Exception as e:
        print(f"⚠️  Could not initialize production database: {e}")
        print("The application will start, but admin features may not work.")
    
    print("✅ Application ready")
    print("🌐 Starting server...")
    print("📱 Visit: http://localhost:5001")
    print("🔧 Admin Portal: http://localhost:5001/admin/login")
    print("=" * 50)
    
    # Start the application
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Starting server on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main() 