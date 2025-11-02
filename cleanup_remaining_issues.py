#!/usr/bin/env python3
"""
Script to identify and fix remaining issues
"""

import os
import glob

def cleanup_remaining_issues():
    print("🧹 Cleaning up remaining issues...")
    print("=" * 50)
    
    # List all Python files
    python_files = glob.glob("*.py") + glob.glob("routes/*.py")
    
    print("📁 Python files found:")
    for file in python_files:
        print(f"   - {file}")
    
    # Check for any remaining old files that might cause issues
    old_files = [
        "app.py",  # Already deleted
        "create_admin.py",  # Already deleted
        "init_db.py",  # Already deleted
        "models.py",  # Old SQLAlchemy models
    ]
    
    print("\n🗑️ Checking for old files:")
    for file in old_files:
        if os.path.exists(file):
            print(f"   ❌ {file} still exists - should be removed")
        else:
            print(f"   ✅ {file} removed")
    
    # Check for any __pycache__ directories
    pycache_dirs = glob.glob("**/__pycache__", recursive=True)
    if pycache_dirs:
        print(f"\n🗑️ Found {len(pycache_dirs)} __pycache__ directories")
        for dir in pycache_dirs:
            print(f"   - {dir}")
        print("   💡 These can be safely deleted")
    
    # Check for any .pyc files
    pyc_files = glob.glob("**/*.pyc", recursive=True)
    if pyc_files:
        print(f"\n🗑️ Found {len(pyc_files)} .pyc files")
        for file in pyc_files:
            print(f"   - {file}")
        print("   💡 These can be safely deleted")
    
    print("\n" + "=" * 50)
    print("🎉 Cleanup completed!")
    print("\n📋 Next Steps:")
    print("1. Close VS Code completely")
    print("2. Delete any __pycache__ directories if found")
    print("3. Reopen VS Code")
    print("4. Press Cmd+Shift+P -> 'Python: Restart Language Server'")
    print("5. Check Problems panel - should show 0 issues")
    
    print("\n🔍 If issues persist:")
    print("- Delete .vscode folder and recreate it")
    print("- Run: source venv/bin/activate && python3 verify_imports.py")
    print("- Restart VS Code completely")

if __name__ == "__main__":
    cleanup_remaining_issues() 