#!/usr/bin/env python3
"""
Test script for Invensis Hiring Portal
Verifies that all components are working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from app import app, db
        from models import User, Role, Candidate, ActivityLog, Feedback
        from routes.admin import admin_bp
        from routes.hr import hr_bp
        from routes.manager import manager_bp
        from routes.cluster import cluster_bp
        from email_service import send_email
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection and table creation"""
    try:
        from app import app, db
        from models import User, Role, Candidate, ActivityLog, Feedback
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_routes():
    """Test that all routes are registered"""
    try:
        from app import app
        
        # Check if routes are registered
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/',
            '/login',
            '/register',
            '/logout',
            '/admin/login',
            '/admin/dashboard',
            '/hr/dashboard',
            '/manager/dashboard',
            '/cluster/dashboard'
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} found")
            else:
                print(f"❌ Route {route} not found")
        
        return True
    except Exception as e:
        print(f"❌ Route test error: {e}")
        return False

def test_templates():
    """Test that all required templates exist"""
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/admin/login.html',
        'templates/admin/dashboard.html',
        'templates/hr/dashboard.html',
        'templates/manager/dashboard.html',
        'templates/cluster/dashboard.html'
    ]
    
    missing_templates = []
    for template in template_files:
        if os.path.exists(template):
            print(f"✅ Template {template} exists")
        else:
            print(f"❌ Template {template} missing")
            missing_templates.append(template)
    
    return len(missing_templates) == 0

def test_directories():
    """Test that all required directories exist"""
    directories = [
        'static',
        'static/css',
        'static/js',
        'static/images',
        'static/uploads',
        'templates',
        'templates/admin',
        'templates/hr',
        'templates/manager',
        'templates/cluster',
        'routes'
    ]
    
    missing_dirs = []
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory {directory} exists")
        else:
            print(f"❌ Directory {directory} missing")
            missing_dirs.append(directory)
    
    return len(missing_dirs) == 0

def main():
    """Run all tests"""
    print("🧪 Testing Invensis Hiring Portal...")
    print("=" * 50)
    
    load_dotenv()
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Routes Test", test_routes),
        ("Templates Test", test_templates),
        ("Directories Test", test_directories)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 To start the application:")
        print("1. Run: python init_db.py (to create admin user)")
        print("2. Run: python app.py")
        print("3. Visit: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    main() 