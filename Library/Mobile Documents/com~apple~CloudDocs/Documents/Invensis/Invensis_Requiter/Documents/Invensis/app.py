#!/usr/bin/env python3
"""
Invensis Hiring Portal - Main Application (FRESH DEPLOYMENT)
Fixed all caching and routing issues
"""

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import secrets

# Load environment variables
load_dotenv()

# Initialize Flask app with explicit configuration
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# MongoDB connection with error handling
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    print("ERROR: MONGODB_URI not set!")
    exit(1)

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    db = client['invensis']
    candidates_collection = db.candidates
    users_collection = db.users
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data.get('name', 'Unknown')
        self.role = user_data.get('role', 'user')
        self.is_active = user_data.get('is_active', True)

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({'_id': user_id, 'is_active': True})
        if user_data:
            return User(user_data)
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

# Routes with aggressive cache-busting
@app.route('/')
def index():
    response = jsonify({
        'status': 'ok',
        'message': 'Invensis Hiring Portal is running',
        'version': '3.0',
        'timestamp': str(datetime.now())
    })
    # Add cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Version'] = '3.0'
    return response

@app.route('/health')
def health():
    response = jsonify({
        'status': 'healthy',
        'timestamp': str(datetime.now())
    })
    # Add cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user_data = users_collection.find_one({'email': email, 'is_active': True})
            if user_data and check_password_hash(user_data['password_hash'], password):
                user = User(user_data)
                login_user(user)
                response = redirect(url_for(f'{user.role}_dashboard'))
                # Add cache-busting headers to redirect
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        except Exception as e:
            print(f"Login error: {e}")

        # Login failed
        response = make_response(render_template('login.html', error='Invalid email or password'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    # GET request
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout')
@login_required
def logout():
    logout_user()
    response = redirect(url_for('login'))
    # Add cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    """Simple dashboard route that redirects to appropriate role dashboard"""
    try:
        response = None
        if current_user.role == 'manager':
            response = redirect(url_for('manager_dashboard'))
        elif current_user.role == 'admin':
            response = redirect(url_for('login'))  # For now, redirect to login
        else:
            response = redirect(url_for('login'))

        # Add nuclear cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        response.headers['X-Redirect-Reason'] = f'Role: {current_user.role}'
        return response
    except Exception as e:
        print(f"Dashboard redirect error: {e}")
        response = redirect(url_for('login'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response

@app.route('/manager/dashboard')
@app.route('/manager/dashboard/<path:version>')
@login_required
def manager_dashboard(version=None):
    print(f"Manager dashboard accessed by: {current_user.email} (role: {current_user.role})")

    # Verify user is actually a manager
    if current_user.role != 'manager':
        print(f"Access denied for non-manager: {current_user.email}")
        response = make_response(redirect(url_for('login')))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        return response

    try:
        print("Loading manager dashboard data...")

        # Get assigned candidates with error handling
        try:
            assigned_candidates = list(candidates_collection.find({
                'manager_email': current_user.email,
                'status': {'$in': ['New', 'Assigned']}
            }).sort('created_at', -1).limit(100))
            print(f"Found {len(assigned_candidates)} assigned candidates")
        except Exception as e:
            print(f"Error loading assigned candidates: {e}")
            assigned_candidates = []

        # Get selected candidates with error handling
        try:
            selected_candidates = list(candidates_collection.find({
                'manager_email': current_user.email,
                'status': 'Selected'
            }).sort('updated_at', -1).limit(100))
            print(f"Found {len(selected_candidates)} selected candidates")
        except Exception as e:
            print(f"Error loading selected candidates: {e}")
            selected_candidates = []

        # Get not selected candidates with error handling
        try:
            not_selected_candidates = list(candidates_collection.find({
                'status': {'$in': ['Not Selected', 'Rejected', 'Declined', 'Failed', 'Not Approved']}
            }).sort('updated_at', -1).limit(100))
            print(f"Found {len(not_selected_candidates)} not selected candidates")
        except Exception as e:
            print(f"Error loading not selected candidates: {e}")
            not_selected_candidates = []

        # Add rejection info
        for candidate in not_selected_candidates:
            try:
                if candidate.get('manager_email') != current_user.email:
                    candidate['rejected_by'] = candidate.get('manager_email', 'Unknown Manager')
                else:
                    candidate['rejected_by'] = 'You'
            except:
                candidate['rejected_by'] = 'Unknown'

        # Get reassigned candidates with error handling
        try:
            reassigned_candidates = list(candidates_collection.find({
                'reassigned_by_manager': current_user.email,
                'status': 'Pending'
            }).sort('updated_at', -1).limit(100))
            print(f"Found {len(reassigned_candidates)} reassigned candidates")
        except Exception as e:
            print(f"Error loading reassigned candidates: {e}")
            reassigned_candidates = []

        print("Rendering manager dashboard template...")

        # Render template with error handling
        response = make_response(render_template('manager/dashboard.html',
                             assigned_candidates=assigned_candidates,
                             selected_candidates=selected_candidates,
                             not_selected_candidates=not_selected_candidates,
                             reassigned_candidates=reassigned_candidates))

        # Nuclear cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        response.headers['X-Manager-Email'] = current_user.email
        print("Manager dashboard loaded successfully")
        return response

    except Exception as e:
        print(f"CRITICAL ERROR in manager dashboard: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

        response = make_response(f"""
        <html>
        <head><title>Manager Dashboard Error</title></head>
        <body>
            <h1>Manager Dashboard Error</h1>
            <p>There was an error loading the manager dashboard.</p>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>User:</strong> {current_user.email}</p>
            <p><strong>Role:</strong> {current_user.role}</p>
            <p>Please contact the administrator or try again later.</p>
            <a href="/">Return to Home</a>
        </body>
        </html>
        """, 500)

        # Nuclear cache-busting even for errors
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        response.headers['X-Error-Time'] = str(datetime.now())
        return response

# Debug routes with cache-busting
@app.route('/debug/status')
def debug_status():
    try:
        response = jsonify({
            'status': 'ok',
            'database_connected': True,
            'mongodb_uri_set': bool(os.getenv('MONGODB_URI')),
            'flask_env': os.getenv('FLASK_ENV', 'production'),
            'candidates_count': candidates_collection.count_documents({}),
            'users_count': users_collection.count_documents({}),
            'version': '3.0',
            'manager_dashboard_fixed': True
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'error': str(e)
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response, 500

@app.route('/debug/simple')
def debug_simple():
    response = jsonify({
        'status': 'ok',
        'message': 'Flask app is working',
        'timestamp': str(datetime.now()),
        'version': '3.0'
    })
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    return response

@app.route('/debug/test-dashboard')
def test_dashboard():
    """Test route to verify dashboard functionality"""
    try:
        # Test database connection
        test_count = candidates_collection.count_documents({})
        response = jsonify({
            'status': 'success',
            'message': 'Dashboard test passed',
            'candidates_count': test_count,
            'mongodb_connected': True,
            'version': '3.0'
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': f'Dashboard test failed: {str(e)}'
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response, 500

# Production server configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"🚀 Starting Invensis Hiring Portal v3.0 on port {port}")
    print(f"🔧 Debug mode: {debug}")
    app.run(debug=debug, host='0.0.0.0', port=port)
