from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user, login_user
from models_mongo import User, Role, ActivityLog, UserEmail
from email_service import send_role_assignment_email, send_invitation_email
from datetime import datetime, timedelta
import re
import jwt
import os

admin_bp = Blueprint('admin', __name__)

# JWT Secret for invitation tokens
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('admin.login'))
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_by_email(email)
        
        if user and user.role == 'admin' and user.check_password(password):
            login_user(user)
            session['role'] = 'admin'
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Count actual users from the users collection
    from models_mongo import users_collection, user_emails_collection
    
    # Count users by role
    manager_count = users_collection.count_documents({'role': 'manager'})
    cluster_count = users_collection.count_documents({'role': 'cluster'})
    hr_count = users_collection.count_documents({'role': 'hr_role'})
    recruiter_count = users_collection.count_documents({'role': 'recruiter'})
    admin_count = users_collection.count_documents({'role': 'admin'})
    total_users = users_collection.count_documents({})
    
    # Get invited emails from user_emails collection
    recruiter_emails = list(user_emails_collection.find({'role': 'Recruiter'}, {'email': 1, 'assigned_by': 1, 'created_at': 1}))
    hr_emails = list(user_emails_collection.find({'role': 'HR_Role'}, {'email': 1, 'assigned_by': 1, 'created_at': 1}))
    manager_emails = list(user_emails_collection.find({'role': 'Manager'}, {'email': 1, 'assigned_by': 1, 'created_at': 1}))
    cluster_emails = list(user_emails_collection.find({'role': 'Cluster Member'}, {'email': 1, 'assigned_by': 1, 'created_at': 1}))
    
    # Get recent activity logs
    from models_mongo import activity_logs_collection
    activity_logs = list(activity_logs_collection.find().sort('timestamp', -1).limit(50))
    
    return render_template('admin/dashboard.html', 
                         manager_count=manager_count,
                         cluster_count=cluster_count,
                         hr_count=hr_count,
                         recruiter_count=recruiter_count,
                         admin_count=admin_count,
                         total_users=total_users,
                         # Add invited emails
                         recruiter_emails=recruiter_emails,
                         hr_emails=hr_emails,
                         manager_emails=manager_emails,
                         cluster_emails=cluster_emails,
                         activity_logs=activity_logs)

@admin_bp.route('/add_role', methods=['POST'])
@admin_required
def add_role():
    email = request.form['email']
    role_type = request.form['role_type']
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'success': False, 'message': 'Invalid email format'})
    
    # Check if email already exists
    existing_role = Role.find_by_email(email)
    if existing_role:
        return jsonify({'success': False, 'message': 'Email already assigned a role'})
    
    # Create new role
    new_role = Role(
        email=email,
        role_type=role_type,
        assigned_by=current_user.email
    )
    new_role.save()
    
    # Log activity
    activity = ActivityLog(
        user_email=current_user.email,
        action=f'Assigned {role_type} role',
        target_email=email,
        details=f'Role {role_type} assigned to {email}'
    )
    activity.save()
    
    try:
        # Send email notification
        send_role_assignment_email(email, role_type)
        
        return jsonify({'success': True, 'message': f'{role_type.title()} role assigned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error assigning role'})

@admin_bp.route('/remove_role', methods=['POST'])
@admin_required
def remove_role():
    email = request.form['email']
    role_type = request.form['role_type']
    
    role = Role.find_by_email(email)
    if role and role.role_type == role_type:
        role.is_active = False
        role.save()
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action=f'Removed {role_type} role',
            target_email=email,
            details=f'Role {role_type} removed from {email}'
        )
        activity.save()
        
        return jsonify({'success': True, 'message': f'{role_type.title()} role removed successfully'})
    else:
        return jsonify({'success': False, 'message': 'Role not found'})

@admin_bp.route('/activity_logs')
@admin_required
def activity_logs():
    from models_mongo import activity_logs_collection
    from datetime import datetime
    logs = list(activity_logs_collection.find().sort('timestamp', -1))
    return render_template('admin/activity_logs.html', activity_logs=logs, now=datetime.now())

@admin_bp.route('/delete_activity_log/<log_id>', methods=['DELETE'])
@admin_required
def delete_activity_log(log_id):
    from models_mongo import activity_logs_collection
    from bson import ObjectId
    
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(log_id)
        
        # Delete the activity log
        result = activity_logs_collection.delete_one({'_id': object_id})
        
        if result.deleted_count > 0:
            # Log the deletion activity
            from models_mongo import ActivityLog
            activity = ActivityLog(
                user_email=session.get('email', 'admin'),
                action='Deleted activity log',
                target_email='',
                details=f'Admin deleted activity log with ID: {log_id}'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': 'Activity log deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Activity log not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting activity log: {str(e)}'})

@admin_bp.route('/clear_all_activity_logs', methods=['DELETE'])
@admin_required
def clear_all_activity_logs():
    from models_mongo import activity_logs_collection
    
    try:
        # Get count before deletion
        count = activity_logs_collection.count_documents({})
        
        # Delete all activity logs
        result = activity_logs_collection.delete_many({})
        
        if result.deleted_count > 0:
            # Log the bulk deletion activity
            from models_mongo import ActivityLog
            activity = ActivityLog(
                user_email=session.get('email', 'admin'),
                action='Cleared all activity logs',
                target_email='',
                details=f'Admin cleared all {count} activity logs'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': f'All {result.deleted_count} activity logs cleared successfully'})
        else:
            return jsonify({'success': False, 'message': 'No activity logs to clear'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error clearing activity logs: {str(e)}'})

@admin_bp.route('/logout')
@admin_required
def logout():
    session.pop('role', None)
    return redirect(url_for('index'))

# Unified Email Management Functions
def add_user_and_send_invite(email, role):
    """Unified function to add user email and send invitation"""
    try:
        # Check if email already exists
        existing_user = UserEmail.find_by_email(email)
        if existing_user:
            return False, 'Email already exists in the system'
        
        # Create new user email record
        new_user_email = UserEmail(
            email=email,
            role=role,
            assigned_by=current_user.email
        )
        new_user_email.save()
        
        # Create JWT token for invitation
        token = jwt.encode(
            {
                'email': email,
                'role': role,
                'type': 'invitation',
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            JWT_SECRET,
            algorithm='HS256'
        )
        
        # Build registration link
        registration_link = f"{request.host_url.rstrip('/')}/register?token={token}"
        
        # Send invitation email
        email_sent = send_invitation_email(email, role, registration_link)
        if not email_sent:
            print(f"❌ Failed to send invitation email to {email}")
            # Still return success for user addition, but log the email failure
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action=f'Added {role} email',
            target_email=email,
            details=f'Added {role} email and sent invitation to {email}'
        )
        activity.save()
        
        return True, f'{role} email added successfully and invitation sent'
        
    except Exception as e:
        print(f"Error in add_user_and_send_invite: {e}")
        return False, f'Error adding {role} email: {str(e)}'

@admin_bp.route('/add_recruiter_email', methods=['POST'])
@admin_required
def add_recruiter_email():
    email = request.form.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'success': False, 'message': 'Invalid email format'})
    
    success, message = add_user_and_send_invite(email, 'Recruiter')  # Fixed: Use 'Recruiter' role for recruiters
    return jsonify({'success': success, 'message': message})

@admin_bp.route('/add_hr_email', methods=['POST'])
@admin_required
def add_hr_email():
    email = request.form.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'success': False, 'message': 'Invalid email format'})
    
    success, message = add_user_and_send_invite(email, 'HR_Role')  # Use HR_Role for actual HR users
    return jsonify({'success': success, 'message': message})

@admin_bp.route('/add_manager_email', methods=['POST'])
@admin_required
def add_manager_email():
    email = request.form.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'success': False, 'message': 'Invalid email format'})
    
    success, message = add_user_and_send_invite(email, 'Manager')
    return jsonify({'success': success, 'message': message})

@admin_bp.route('/add_cluster_email', methods=['POST'])
@admin_required
def add_cluster_email():
    email = request.form.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'success': False, 'message': 'Invalid email format'})
    
    success, message = add_user_and_send_invite(email, 'Cluster Member')
    return jsonify({'success': success, 'message': message})

@admin_bp.route('/clear_all_candidates', methods=['POST'])
@admin_required
def clear_all_candidates():
    """Clear all candidate data from the database"""
    try:
        from models_mongo import candidates_collection, feedback_collection, candidate_requests_collection
        
        # Get confirmation from request
        confirmation = request.json.get('confirmation', '') if request.is_json else request.form.get('confirmation', '')
        
        if confirmation != 'DELETE ALL CANDIDATES':
            return jsonify({
                'success': False,
                'message': 'Invalid confirmation. Please type "DELETE ALL CANDIDATES" to confirm.'
            }), 400
        
        # Count before deletion
        candidates_count = candidates_collection.count_documents({})
        feedback_count = feedback_collection.count_documents({})
        candidate_requests_count = candidate_requests_collection.count_documents({})
        
        # Delete all candidates
        candidates_deleted = candidates_collection.delete_many({}).deleted_count
        
        # Delete all feedback
        feedback_deleted = feedback_collection.delete_many({}).deleted_count
        
        # Delete all candidate requests
        candidate_requests_deleted = candidate_requests_collection.delete_many({}).deleted_count
        
        # Log the activity
        try:
            activity_log = ActivityLog(
                user_email=current_user.email,
                action='clear_all_candidates',
                details=f'Cleared all candidate data: {candidates_deleted} candidates, {feedback_deleted} feedback records, {candidate_requests_deleted} candidate requests'
            )
            activity_log.save()
        except Exception as log_error:
            print(f"Warning: Failed to log activity: {log_error}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully cleared all candidate data: {candidates_deleted} candidates, {feedback_deleted} feedback records, {candidate_requests_deleted} candidate requests'
        })
        
    except Exception as e:
        print(f"Error clearing candidates: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error clearing candidate data: {str(e)}'
        }), 500

@admin_bp.route('/remove_user_email', methods=['POST'])
@admin_required
def remove_user_email():
    email = request.form.get('email')
    role = request.form.get('role')
    
    if not email or not role:
        return jsonify({'success': False, 'message': 'Email and role are required'})
    
    try:
        from models_mongo import users_collection, password_reset_tokens_collection
        from bson import ObjectId
        
        user_email = UserEmail.find_by_email(email)
        if user_email and user_email.role == role:
            # Delete UserEmail record
            user_email.delete()
            
            # Delete User record from users_collection (if exists)
            user = User.find_by_email(email)
            if user:
                users_collection.delete_one({'email': email})
                print(f"✅ Deleted User record for {email}")
            
            # Delete password reset tokens for this user (if exists)
            if user:
                try:
                    password_reset_tokens_collection.delete_many({'user_id': str(user._id)})
                    print(f"✅ Deleted password reset tokens for {email}")
                except Exception as token_error:
                    print(f"⚠️ Warning: Could not delete password reset tokens: {token_error}")
            
            # Log activity
            activity = ActivityLog(
                user_email=current_user.email,
                action=f'Removed {role} email',
                target_email=email,
                details=f'Removed {role} email: {email}. User account and related data completely deleted.'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': f'{role} email and user account removed successfully. User can now register again.'})
        else:
            return jsonify({'success': False, 'message': 'Email not found'})
            
    except Exception as e:
        print(f"❌ Error removing user email: {str(e)}")
        return jsonify({'success': False, 'message': f'Error removing email: {str(e)}'}) 