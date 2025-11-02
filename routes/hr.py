from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Candidate, User, Role
from email_service import send_candidate_assignment_email
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

hr_bp = Blueprint('hr', __name__)

def hr_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'hr':
            flash('Access denied. HR privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@hr_bp.route('/dashboard')
@hr_required
def dashboard():
    candidates = Candidate.query.filter_by(assigned_by=current_user.email).order_by(Candidate.created_at.desc()).all()
    managers = Role.query.filter_by(role_type='manager', is_active=True).all()
    
    return render_template('hr/dashboard.html', 
                         candidates=candidates,
                         managers=managers)

@hr_bp.route('/add_candidate', methods=['POST'])
@hr_required
def add_candidate():
    try:
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        age = int(request.form['age'])
        education = request.form['education']
        experience = request.form['experience']
        
        # Handle file uploads
        resume_path = None
        image_path = None
        
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume and resume.filename != '':
                filename = secure_filename(f"{uuid.uuid4()}_{resume.filename}")
                resume_path = os.path.join('static/uploads', filename)
                resume.save(resume_path)
        
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != '':
                filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
                image_path = os.path.join('static/uploads', filename)
                image.save(image_path)
        
        # Create candidate
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            gender=gender,
            age=age,
            education=education,
            experience=experience,
            resume_path=resume_path,
            image_path=image_path,
            assigned_by=current_user.email
        )
        
        db.session.add(candidate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Candidate added successfully',
            'reference_id': candidate.reference_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@hr_bp.route('/assign_candidate', methods=['POST'])
@hr_required
def assign_candidate():
    candidate_id = request.form['candidate_id']
    manager_email = request.form['manager_email']
    scheduled_date = request.form['scheduled_date']
    
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'success': False, 'message': 'Candidate not found'})
    
    # Update candidate
    candidate.assigned_to = manager_email
    candidate.status = 'assigned'
    candidate.scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%dT%H:%M')
    
    db.session.commit()
    
    # Send email to manager
    send_candidate_assignment_email(manager_email, candidate)
    
    return jsonify({'success': True, 'message': 'Candidate assigned successfully'})

@hr_bp.route('/candidates')
@hr_required
def candidates():
    candidates = Candidate.query.filter_by(assigned_by=current_user.email).order_by(Candidate.created_at.desc()).all()
    return render_template('hr/candidates.html', candidates=candidates)

@hr_bp.route('/candidate/<int:candidate_id>')
@hr_required
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template('hr/candidate_detail.html', candidate=candidate) 