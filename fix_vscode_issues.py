#!/usr/bin/env python3
"""
Comprehensive script to fix all VS Code issues
"""

import os
import subprocess
import sys

def fix_vscode_issues():
    print("🔧 Fixing VS Code Issues...")
    print("=" * 60)
    
    # Check if we're in the virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ Not running in virtual environment!")
        print("Please activate the virtual environment first:")
        print("source venv/bin/activate")
        return
    
    print("✅ Running in virtual environment")
    
    # Check Python interpreter
    python_path = sys.executable
    print(f"✅ Python interpreter: {python_path}")
    
    # Verify all packages are installed
    print("\n📦 Verifying package installations...")
    
    packages = [
        'flask',
        'flask-login', 
        'flask-mail',
        'werkzeug',
        'pymongo',
        'dnspython',
        'PyJWT',
        'python-dotenv',
        'email-validator',
        'pillow',
        'reportlab',
        'pandas'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
    
    # Create VS Code configuration files
    print("\n⚙️ Creating VS Code configuration...")
    
    # Ensure .vscode directory exists
    os.makedirs('.vscode', exist_ok=True)
    
    # Create workspace settings
    workspace_settings = {
        "python.defaultInterpreterPath": "./venv/bin/python3",
        "python.terminal.activateEnvironment": True,
        "python.analysis.extraPaths": [
            "./venv/lib/python3.13/site-packages"
        ],
        "python.analysis.autoImportCompletions": True,
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoSearchPaths": True,
        "python.analysis.diagnosticMode": "workspace",
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": False,
        "python.linting.mypyEnabled": False,
        "files.associations": {
            "*.py": "python"
        },
        "python.analysis.include": [
            "**/*.py"
        ],
        "python.analysis.exclude": [
            "**/venv/**",
            "**/__pycache__/**",
            "**/.git/**"
        ]
    }
    
    import json
    with open('.vscode/settings.json', 'w') as f:
        json.dump(workspace_settings, f, indent=4)
    
    print("✅ Created .vscode/settings.json")
    
    # Create launch configuration
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Flask",
                "type": "python",
                "request": "launch",
                "module": "flask",
                "env": {
                    "FLASK_APP": "app_mongo.py",
                    "FLASK_ENV": "development"
                },
                "args": [
                    "run",
                    "--no-debugger",
                    "--no-reload",
                    "--host=0.0.0.0",
                    "--port=5001"
                ],
                "jinja": True,
                "justMyCode": True,
                "python": "${workspaceFolder}/venv/bin/python3"
            },
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "python": "${workspaceFolder}/venv/bin/python3"
            }
        ]
    }
    
    with open('.vscode/launch.json', 'w') as f:
        json.dump(launch_config, f, indent=4)
    
    print("✅ Created .vscode/launch.json")
    
    # Create pyrightconfig.json
    pyright_config = {
        "include": [
            "."
        ],
        "exclude": [
            "**/node_modules",
            "**/__pycache__",
            "venv",
            ".venv",
            "instance"
        ],
        "ignore": [
            "**/venv/**",
            "**/__pycache__/**",
            "**/.git/**"
        ],
        "reportMissingImports": "warning",
        "reportMissingTypeStubs": False,
        "pythonVersion": "3.13",
        "pythonPlatform": "Darwin",
        "executionEnvironments": [
            {
                "root": ".",
                "pythonVersion": "3.13",
                "pythonPlatform": "Darwin",
                "extraPaths": [
                    "./venv/lib/python3.13/site-packages"
                ]
            }
        ]
    }
    
    with open('pyrightconfig.json', 'w') as f:
        json.dump(pyright_config, f, indent=4)
    
    print("✅ Created pyrightconfig.json")
    
    print("\n" + "=" * 60)
    print("🎉 VS Code Configuration Complete!")
    print("\n📋 Next Steps:")
    print("1. Close VS Code completely")
    print("2. Reopen VS Code in this project folder")
    print("3. Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)")
    print("4. Type 'Python: Select Interpreter'")
    print("5. Choose: ./venv/bin/python3")
    print("6. Press Cmd+Shift+P -> 'Developer: Reload Window'")
    print("\n✅ This should resolve all 70 import issues!")
    print("\n🔍 If issues persist:")
    print("- Check that the virtual environment is activated")
    print("- Verify all packages are installed: pip install -r requirements.txt")
    print("- Restart VS Code completely")

if __name__ == "__main__":
    fix_vscode_issues() 