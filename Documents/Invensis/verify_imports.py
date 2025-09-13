#!/usr/bin/env python3
"""
Script to verify all imports are working correctly
"""

def test_imports():
    print("🧪 Testing all imports...")
    print("=" * 50)
    
    # Test Flask imports
    try:
        from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
        print("✅ Flask imports successful")
    except ImportError as e:
        print(f"❌ Flask imports failed: {e}")
    
    # Test Flask-Login imports
    try:
        from flask_login import login_required, current_user, login_user, logout_user
        print("✅ Flask-Login imports successful")
    except ImportError as e:
        print(f"❌ Flask-Login imports failed: {e}")
    
    # Test Flask-Mail imports
    try:
        from flask_mail import Mail, Message
        print("✅ Flask-Mail imports successful")
    except ImportError as e:
        print(f"❌ Flask-Mail imports failed: {e}")
    
    # Test Werkzeug imports
    try:
        from werkzeug.security import generate_password_hash, check_password_hash
        from werkzeug.utils import secure_filename
        print("✅ Werkzeug imports successful")
    except ImportError as e:
        print(f"❌ Werkzeug imports failed: {e}")
    
    # Test MongoDB imports
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        print("✅ MongoDB imports successful")
    except ImportError as e:
        print(f"❌ MongoDB imports failed: {e}")
    
    # Test JWT imports
    try:
        import jwt
        print("✅ JWT imports successful")
    except ImportError as e:
        print(f"❌ JWT imports failed: {e}")
    
    # Test other imports
    try:
        from dotenv import load_dotenv
        import os
        import uuid
        from datetime import datetime, timedelta
        print("✅ Other imports successful")
    except ImportError as e:
        print(f"❌ Other imports failed: {e}")
    
    # Test pandas and reportlab for exports
    try:
        import pandas as pd
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        print("✅ Export library imports successful")
    except ImportError as e:
        print(f"❌ Export library imports failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Import verification completed!")
    print("\n✅ All imports should be working correctly.")
    print("📝 If you still see import errors in VS Code:")
    print("   1. Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)")
    print("   2. Type 'Python: Select Interpreter'")
    print("   3. Choose: ./venv/bin/python3")
    print("   4. Reload VS Code window (Cmd+Shift+P -> 'Developer: Reload Window')")

if __name__ == "__main__":
    test_imports() 