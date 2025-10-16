#!/usr/bin/env python3
"""
Invensis Hiring Portal - Main Application
"""

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['invensis']
candidates_collection = db.candidates
users_collection = db.users

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data['name']
        self.role = user_data['role']
        self.is_active = user_data.get('is_active', True)

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({'_id': user_id})
        if user_data:
            return User(user_data)
    except:
        pass
    return None

# Routes
@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Invensis Hiring Portal is running',
        'version': '2.0',
        'timestamp': str(datetime.now())
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': str(datetime.now())
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = users_collection.find_one({'email': email, 'is_active': True})
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for(f'{user.role}_dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/manager/dashboard')
@app.route('/manager/dashboard?v=<version>')
@login_required
def manager_dashboard(version=None):
    if current_user.role != 'manager':
        response = make_response(redirect(url_for('login')))
        # Add cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        return response

    try:
        # Get assigned candidates
        assigned_candidates = list(candidates_collection.find({
            'manager_email': current_user.email,
            'status': {'$in': ['New', 'Assigned']}
        }).sort('created_at', -1))
        
        # Get selected candidates
        selected_candidates = list(candidates_collection.find({
            'manager_email': current_user.email,
            'status': 'Selected'
        }).sort('updated_at', -1))
        
        # Get not selected candidates
        not_selected_candidates = list(candidates_collection.find({
            'status': {'$in': ['Not Selected', 'Rejected', 'Declined', 'Failed', 'Not Approved']}
        }).sort('updated_at', -1))
        
        # Add rejection info
        for candidate in not_selected_candidates:
            if candidate.get('manager_email') != current_user.email:
                candidate['rejected_by'] = candidate.get('manager_email', 'Unknown Manager')
            else:
                candidate['rejected_by'] = 'You'
        
        # Get reassigned candidates
        reassigned_candidates = list(candidates_collection.find({
            'reassigned_by_manager': current_user.email,
            'status': 'Pending'
        }).sort('updated_at', -1))
        
        response = make_response(render_template('manager/dashboard.html',
                             assigned_candidates=assigned_candidates,
                             selected_candidates=selected_candidates,
                             not_selected_candidates=not_selected_candidates,
                             reassigned_candidates=reassigned_candidates))
        # Add cache-busting headers to prevent caching of dashboard
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        return response
    
    except Exception as e:
        print(f"Error in manager dashboard: {str(e)}")
        response = make_response(f"""
        <html>
        <head><title>Manager Dashboard Error</title></head>
        <body>
            <h1>Manager Dashboard Error</h1>
            <p>There was an error loading the manager dashboard.</p>
            <p><strong>Error:</strong> {str(e)}</p>
            <p>Please contact the administrator or try again later.</p>
            <a href="/">Return to Home</a>
        </body>
        </html>
        """, 500)
        # Add cache-busting headers even for error responses
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Cache-Bust'] = str(int(time.time()))
        return response

# Debug routes
@app.route('/debug/status')
def debug_status():
    try:
        return jsonify({
            'status': 'ok',
            'database_connected': True,
            'mongodb_uri_set': bool(os.getenv('MONGODB_URI')),
            'flask_env': os.getenv('FLASK_ENV', 'development'),
            'candidates_count': candidates_collection.count_documents({}),
            'users_count': users_collection.count_documents({})
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/debug/simple')
def debug_simple():
    return jsonify({
        'status': 'ok',
        'message': 'Flask app is working',
        'timestamp': str(datetime.now())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
