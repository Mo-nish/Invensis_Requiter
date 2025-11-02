from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-secret-key-here')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

# Debug email configuration
print(f"Email config - USER: {os.getenv('EMAIL_USER', 'NOT_SET')}")
print(f"Email config - PASS: {'SET' if os.getenv('EMAIL_PASS') else 'NOT_SET'}")
print(f"Email config - SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Import MongoDB models
from models_mongo import User, Role, Candidate, ActivityLog, Feedback, create_token, verify_token, UserEmail, PasswordResetToken

@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get user counts by role for statistics
    hr_count = User.count_by_role('hr_role')  # Fixed: use 'hr_role' instead of 'hr'
    recruiter_count = User.count_by_role('recruiter')  # Added: count recruiter users
    manager_count = User.count_by_role('manager')
    cluster_count = User.count_by_role('cluster')
    
    print(f"Landing page user counts - HR: {hr_count}, Recruiter: {recruiter_count}, Manager: {manager_count}, Cluster: {cluster_count}")
    
    return render_template('index.html', 
                         hr_count=hr_count,
                         recruiter_count=recruiter_count,  # Added: pass recruiter count to template
                         manager_count=manager_count,
                         cluster_count=cluster_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            # Create JWT token
            token = create_token(user.get_id(), user.role)
            session['token'] = token
            
            # Redirect based on role (handle both uppercase and lowercase)
            user_role = user.role.lower() if user.role else ''
            
            if user_role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user_role == 'hr':
                return redirect(url_for('recruiter.dashboard'))  # HR users (recruiters) go to recruiter dashboard
            elif user_role == 'hr_role':
                return redirect(url_for('hr.dashboard'))  # Actual HR users go to HR dashboard
            elif user_role == 'recruiter':
                return redirect(url_for('recruiter.dashboard'))
            elif user_role == 'manager':
                return redirect(url_for('manager.dashboard'))
            elif user_role == 'cluster':
                return redirect(url_for('cluster.dashboard'))
            else:
                # Fallback for unknown roles
                print(f"DEBUG: Unknown role '{user.role}' for user {user.email}")
                flash(f'Unknown role: {user.role}. Please contact admin.', 'error')
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check for invitation token in URL
    token = request.args.get('token')
    invited_email = None
    invited_role = None
    
    if token:
        # Verify JWT token
        try:
            payload = verify_token(token)
            if payload and payload.get('type') == 'invitation':
                invited_email = payload.get('email')
                invited_role = payload.get('role')
            else:
                flash('Invalid or expired invitation token', 'error')
        except Exception as e:
            flash('Invalid invitation token', 'error')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('name', email.split('@')[0])  # Use email prefix if name not provided
        
        # Check if user already exists
        if User.find_by_email(email):
            flash('Email already registered', 'error')
            return render_template('register.html', invited_email=invited_email, invited_role=invited_role)
        
        # Check if email is pre-approved using the new UserEmail model
        user_email = UserEmail.find_by_email(email)
        
        print(f"DEBUG: Checking email {email} - UserEmail result: {user_email}")
        
        if not user_email:
            flash('Email not authorized. Please contact admin or use a valid invitation link.', 'error')
            return render_template('register.html', invited_email=invited_email, invited_role=invited_role)
        
        # Create user with the role from UserEmail
        # Map the role names to match the expected format
        role_mapping = {
            'HR': 'hr',
            'Recruiter': 'recruiter',  # Added: Map Recruiter role
            'Manager': 'manager', 
            'Cluster Member': 'cluster'
        }
        user_role = role_mapping.get(user_email.role, user_email.role.lower())
        
        print(f"DEBUG: Creating user with role mapping: {user_email.role} -> {user_role}")
        
        user = User(email=email, name=name, role=user_role)
        user.set_password(password)
        user.save()
        
        # Log the registration activity
        activity = ActivityLog(
            user_email=email,
            action='User registration',
            details=f'New user registered with role: {user_email.role}'
        )
        activity.save()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', invited_email=invited_email, invited_role=invited_role)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('token', None)
    # All users (HR, Manager, Cluster, Admin) should go to home page
    return redirect(url_for('index'))

# Import routes after app initialization
from routes.admin_mongo import admin_bp
from routes.hr_mongo import hr_bp
from routes.recruiter_mongo import recruiter_bp
from routes.manager_mongo import manager_bp
from routes.cluster_mongo import cluster_bp
from routes.chatbot_mongo import chatbot_bp

# Import email service functions
from email_service import send_password_reset_email, send_password_changed_confirmation_email

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            
            if not email:
                return jsonify({'success': False, 'error': 'Email is required'}), 400
            
            # Check if user exists
            user = User.find_by_email(email)
            if not user:
                # Don't reveal if email exists or not for security
                return jsonify({'success': True, 'message': 'If the email exists, a reset link has been sent'})
            
            # Check if there's already an active token for this user
            user_id = user.get_id()
            print(f"DEBUG: Checking for tokens for user_id: {user_id} (type: {type(user_id)})")
            
            existing_token = PasswordResetToken.find_by_user_id(user_id)
            print(f"DEBUG: find_by_user_id result: {existing_token}")
            
            if existing_token:
                print(f"DEBUG: Found token: {existing_token.token[:20]}...")
                print(f"DEBUG: Token expires at: {existing_token.expires_at}")
                print(f"DEBUG: Current time: {datetime.utcnow()}")
                print(f"DEBUG: Is expired: {existing_token.is_expired()}")
                print(f"DEBUG: Is used: {existing_token.is_used}")
                
                # Clean up expired tokens first
                if existing_token.is_expired():
                    # Delete expired token
                    try:
                        from bson import ObjectId
                        password_reset_tokens_collection.delete_one({'_id': ObjectId(existing_token._id)})
                        existing_token = None
                        print("DEBUG: Expired token deleted")
                    except Exception as e:
                        print(f"DEBUG: Error deleting expired token: {e}")
                elif not existing_token.is_used:
                    # Active, non-expired token exists
                    print(f"DEBUG: Found active token for user {user_id}: {existing_token.token[:20]}...")
                    print(f"DEBUG: Token expires at: {existing_token.expires_at}")
                    print(f"DEBUG: Current time: {datetime.utcnow()}")
                    print(f"DEBUG: Is expired: {existing_token.is_expired()}")
                    return jsonify({'success': False, 'error': 'A reset link has already been sent. Please check your email or wait before requesting another.'}), 429
            else:
                print("DEBUG: No existing token found")
            
            # Generate unique token
            import secrets
            token = secrets.token_urlsafe(32)
            
            # Set expiration (1 hour from now)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Create and save token
            reset_token = PasswordResetToken(
                user_id=user.get_id(),
                token=token,
                expires_at=expires_at
            )
            reset_token.save()
            
            # Send email
            base_url = request.host_url.rstrip('/')
            send_password_reset_email(user.email, user.name, token, base_url)
            
            # Log the activity
            activity = ActivityLog(
                user_email=email,
                action='Password reset requested',
                details='Password reset link sent via email'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': 'Password reset link sent successfully'})
            
        except Exception as e:
            print(f"Error in forgot_password: {str(e)}")
            return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Handle password reset with token"""
    token = request.args.get('token')
    
    if not token:
        return redirect(url_for('forgot_password'))
    
    # Verify token
    reset_token = PasswordResetToken.find_by_token(token)
    if not reset_token:
        return redirect(url_for('forgot_password'))
    
    if reset_token.is_expired():
        return redirect(url_for('forgot_password'))
    
    if reset_token.is_used:
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if not new_password or not confirm_password:
                return jsonify({'success': False, 'error': 'Both password fields are required'}), 400
            
            if new_password != confirm_password:
                return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
            
            # Validate password strength
            if len(new_password) < 8:
                return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
            
            if not any(c.isupper() for c in new_password):
                return jsonify({'success': False, 'error': 'Password must contain at least one uppercase letter'}), 400
            
            if not any(c.islower() for c in new_password):
                return jsonify({'success': False, 'error': 'Password must contain at least one lowercase letter'}), 400
            
            if not any(c.isdigit() for c in new_password):
                return jsonify({'success': False, 'error': 'Password must contain at least one number'}), 400
            
            if not any(c in '!@#$%^&*(),.?":{}|<>' for c in new_password):
                return jsonify({'success': False, 'error': 'Password must contain at least one special character'}), 400
            
            # Get user and update password
            user = User.find_by_id(reset_token.user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.mark_as_used()
            
            # Send confirmation email
            base_url = request.host_url.rstrip('/')
            send_password_changed_confirmation_email(user.email, user.name, base_url)
            
            # Log the activity
            activity = ActivityLog(
                user_email=user.email,
                action='Password reset completed',
                details='Password successfully changed via reset link'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': 'Password updated successfully'})
            
        except Exception as e:
            print(f"Error in reset_password: {str(e)}")
            return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500
    
    return render_template('reset_password.html', token=token)

# Template context processor to handle current_user safely
@app.context_processor
def inject_user():
    try:
        from flask_login import current_user
        return dict(current_user=current_user if current_user.is_authenticated else None)
    except:
        return dict(current_user=None)

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(hr_bp, url_prefix='/hr')
app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
app.register_blueprint(manager_bp, url_prefix='/manager')
app.register_blueprint(cluster_bp, url_prefix='/cluster')
app.register_blueprint(chatbot_bp, url_prefix='/')

# Contact Support Route
@app.route('/contact-support')
def contact_support():
    return render_template('contact_support.html')

# Heaven Execution Chamber Route
@app.route('/heaven-execution')
def heaven_execution():
    return render_template('heaven_execution.html')

# Send Contact Email Route
@app.route('/send-contact-email', methods=['POST'])
def send_contact_email():
    try:
        data = request.get_json()
        user_email = data.get('email')
        subject = data.get('subject', 'Contact Support')
        message = data.get('message')
        
        if not user_email or not message:
            return jsonify({'success': False, 'message': 'Email and message are required'})
        
        # Create email message
        msg = Message(
            subject=f"Contact Support: {subject}",
            recipients=['p.monishreddy19@gmail.com'],
            body=f"""
From: {user_email}
Subject: {subject}

Message:
{message}

---
Sent from Invensis Hiring Portal Contact Support
            """,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send email
        mail.send(msg)
        
        return jsonify({'success': True, 'message': 'Email sent successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error sending email: {str(e)}'})

if __name__ == '__main__':
    # Ensure a single intended admin user exists (configurable via env)
    default_admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'invensisprocess@gmail.com')
    default_admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'Monish@007')
    default_admin_name = os.getenv('DEFAULT_ADMIN_NAME', 'Invensis Admin')

    ensured_admin = User.find_by_email(default_admin_email)
    if not ensured_admin:
        ensured_admin = User(
            email=default_admin_email,
            name=default_admin_name,
            role='admin'
        )
        ensured_admin.set_password(default_admin_password)
        ensured_admin.save()
        print(f"✅ Admin user ensured: {default_admin_email}")
    
    # Clean up expired password reset tokens
    try:
        PasswordResetToken.delete_expired_tokens()
        print("✅ Cleaned up expired password reset tokens")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up expired tokens: {e}")
    
    print("🚀 Starting Invensis Hiring Portal with MongoDB...")
    print("📱 Visit: http://localhost:5001")
    print("🔧 Admin Portal: http://localhost:5001/admin/login")
    print("=" * 50)
    
    # WebSocket event handlers for modern chat
    @socketio.on('connect')
    def handle_connect():
        print(f"🔌 Socket.IO connected: {request.sid}")
        emit('connected', {'message': 'Connected to Socket.IO', 'socket_id': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"🔌 Socket.IO disconnected: {request.sid}")
        # Update user online status
        if hasattr(request, 'user_id'):
            emit('user_offline', {'user_id': request.user_id}, broadcast=True)
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """User joins a chat conversation"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        
        if user_id and conversation_id:
            join_room(f"conversation_{conversation_id}")
            request.user_id = user_id
            print(f"👤 User {user_id} joined conversation {conversation_id}")
            
            # Notify others in the conversation
            emit('user_joined', {
                'user_id': user_id,
                'conversation_id': conversation_id
            }, room=f"conversation_{conversation_id}", include_self=False)
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """User leaves a chat conversation"""
        conversation_id = data.get('conversation_id')
        if conversation_id:
            leave_room(f"conversation_{conversation_id}")
            print(f"👤 User left conversation {conversation_id}")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle new message"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        message_type = data.get('type', 'text')
        file_url = data.get('file_url')
        file_name = data.get('file_name')
        
        if user_id and conversation_id and content:
            # Save message to database
            message_data = {
                'conversation_id': conversation_id,
                'sender_id': user_id,
                'content': content,
                'message_type': message_type,
                'file_url': file_url,
                'file_name': file_name,
                'timestamp': datetime.utcnow(),
                'status': 'sent'
            }
            
            # Add to messages collection
            messages_collection = db.messages
            result = messages_collection.insert_one(message_data)
            message_data['_id'] = str(result.inserted_id)
            
            # Broadcast to all users in conversation
            emit('new_message', message_data, room=f"conversation_{conversation_id}")
            
            print(f"📤 Message sent by {user_id} in conversation {conversation_id}")
    
    @socketio.on('typing_start')
    def handle_typing_start(data):
        """User starts typing"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        
        if user_id and conversation_id:
            emit('user_typing', {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'typing': True
            }, room=f"conversation_{conversation_id}", include_self=False)
    
    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        """User stops typing"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        
        if user_id and conversation_id:
            emit('user_typing', {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'typing': False
            }, room=f"conversation_{conversation_id}", include_self=False)
    
    @socketio.on('message_reaction')
    def handle_message_reaction(data):
        """Handle message reactions (👍❤️😂)"""
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        reaction = data.get('reaction')
        conversation_id = data.get('conversation_id')
        
        if user_id and message_id and reaction and conversation_id:
            # Update message with reaction
            messages_collection = db.messages
            messages_collection.update_one(
                {'_id': ObjectId(message_id)},
                {'$addToSet': {'reactions': {'user_id': user_id, 'reaction': reaction}}}
            )
            
            # Broadcast reaction to conversation
            emit('message_reaction_added', {
                'message_id': message_id,
                'user_id': user_id,
                'reaction': reaction
            }, room=f"conversation_{conversation_id}")
            
            print(f"😀 Reaction {reaction} added by {user_id} to message {message_id}")
    
    @socketio.on('message_read')
    def handle_message_read(data):
        """Mark message as read"""
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        conversation_id = data.get('conversation_id')
        
        if user_id and message_id and conversation_id:
            # Update message status
            messages_collection = db.messages
            messages_collection.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {'status': 'read', 'read_by': user_id, 'read_at': datetime.utcnow()}}
            )
            
            # Broadcast read status
            emit('message_read_status', {
                'message_id': message_id,
                'user_id': user_id,
                'status': 'read'
            }, room=f"conversation_{conversation_id}")
    
    @socketio.on('user_online')
    def handle_user_online(data):
        """User comes online"""
        user_id = data.get('user_id')
        if user_id:
            request.user_id = user_id
            emit('user_online_status', {'user_id': user_id, 'online': True}, broadcast=True)
            print(f"🟢 User {user_id} is online")
    
    @socketio.on('user_offline')
    def handle_user_offline(data):
        """User goes offline"""
        user_id = data.get('user_id')
        if user_id:
            emit('user_online_status', {'user_id': user_id, 'online': False}, broadcast=True)
            print(f"🔴 User {user_id} is offline")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001) 