from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models import db, User, Role, ActivityLog
from email_service import send_role_assignment_email
from datetime import datetime
import re

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
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
        user = User.query.filter_by(email=email, role='admin').first()
        
        if user and user.check_password_hash(password):
            session['role'] = 'admin'
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    hr_emails = Role.query.filter_by(role_type='hr', is_active=True).all()
    manager_emails = Role.query.filter_by(role_type='manager', is_active=True).all()
    cluster_emails = Role.query.filter_by(role_type='cluster', is_active=True).all()
    
    activity_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    return render_template('admin/dashboard.html', 
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
    existing_role = Role.query.filter_by(email=email).first()
    if existing_role:
        return jsonify({'success': False, 'message': 'Email already assigned a role'})
    
    # Create new role
    new_role = Role(
        email=email,
        role_type=role_type,
        assigned_by=current_user.email
    )
    db.session.add(new_role)
    
    # Log activity
    activity = ActivityLog(
        user_email=current_user.email,
        action=f'Assigned {role_type} role',
        target_email=email,
        details=f'Role {role_type} assigned to {email}'
    )
    db.session.add(activity)
    
    try:
        db.session.commit()
        
        # Send email notification
        send_role_assignment_email(email, role_type)
        
        return jsonify({'success': True, 'message': f'{role_type.title()} role assigned successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error assigning role'})

@admin_bp.route('/remove_role', methods=['POST'])
@admin_required
def remove_role():
    email = request.form['email']
    role_type = request.form['role_type']
    
    role = Role.query.filter_by(email=email, role_type=role_type).first()
    if role:
        role.is_active = False
        db.session.commit()
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action=f'Removed {role_type} role',
            target_email=email,
            details=f'Role {role_type} removed from {email}'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{role_type.title()} role removed successfully'})
    
    return jsonify({'success': False, 'message': 'Role not found'})

@admin_bp.route('/activity_logs')
@admin_required
def activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    return render_template('admin/activity_logs.html', logs=logs)

@admin_bp.route('/logout')
@admin_required
def logout():
    session.pop('role', None)
    return redirect(url_for('index')) 