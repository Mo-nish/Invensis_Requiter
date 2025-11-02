from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Candidate, Feedback, User
from email_service import send_feedback_notification_email
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

manager_bp = Blueprint('manager', __name__)

def manager_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'manager':
            flash('Access denied. Manager privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    assigned_candidates = Candidate.query.filter_by(
        assigned_to=current_user.email,
        status='assigned'
    ).order_by(Candidate.created_at.desc()).all()
    
    reviewed_candidates = Candidate.query.filter(
        Candidate.assigned_to == current_user.email,
        Candidate.status.in_(['shortlisted', 'rejected', 'on_hold'])
    ).order_by(Candidate.updated_at.desc()).all()
    
    return render_template('manager/dashboard.html',
                         assigned_candidates=assigned_candidates,
                         reviewed_candidates=reviewed_candidates)

@manager_bp.route('/candidate/<int:candidate_id>')
@manager_required
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Check if manager has access to this candidate
    if candidate.assigned_to != current_user.email:
        flash('Access denied to this candidate', 'error')
        return redirect(url_for('manager.dashboard'))
    
    feedbacks = Feedback.query.filter_by(candidate_id=candidate_id).order_by(Feedback.created_at.desc()).all()
    
    return render_template('manager/candidate_detail.html',
                         candidate=candidate,
                         feedbacks=feedbacks)

@manager_bp.route('/add_feedback', methods=['POST'])
@manager_required
def add_feedback():
    candidate_id = request.form['candidate_id']
    feedback_text = request.form['feedback']
    status = request.form['status']
    
    candidate = Candidate.query.get(candidate_id)
    if not candidate or candidate.assigned_to != current_user.email:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Create feedback
    feedback = Feedback(
        candidate_id=candidate_id,
        manager_email=current_user.email,
        feedback_text=feedback_text,
        status=status
    )
    db.session.add(feedback)
    
    # Update candidate status
    candidate.status = status
    candidate.feedback = feedback_text
    candidate.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Send notification to HR
    send_feedback_notification_email(candidate.assigned_by, candidate, status)
    
    return jsonify({'success': True, 'message': 'Feedback added successfully'})

@manager_bp.route('/reassign_candidate', methods=['POST'])
@manager_required
def reassign_candidate():
    candidate_id = request.form['candidate_id']
    note = request.form.get('note', '')
    
    candidate = Candidate.query.get(candidate_id)
    if not candidate or candidate.assigned_to != current_user.email:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Reset candidate status
    candidate.status = 'pending'
    candidate.assigned_to = None
    candidate.scheduled_date = None
    candidate.feedback = note
    candidate.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Candidate reassigned to HR'})

@manager_bp.route('/export_feedback')
@manager_required
def export_feedback():
    format_type = request.args.get('format', 'csv')
    
    candidates = Candidate.query.filter_by(assigned_to=current_user.email).all()
    
    if format_type == 'csv':
        data = []
        for candidate in candidates:
            data.append({
                'Reference ID': candidate.reference_id,
                'Name': candidate.name,
                'Email': candidate.email,
                'Status': candidate.status,
                'Feedback': candidate.feedback,
                'Created Date': candidate.created_at.strftime('%Y-%m-%d'),
                'Updated Date': candidate.updated_at.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=feedback_export.csv'
        }
    
    elif format_type == 'pdf':
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Manager Feedback Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add candidate data
        for candidate in candidates:
            story.append(Paragraph(f"<b>Reference ID:</b> {candidate.reference_id}", styles['Normal']))
            story.append(Paragraph(f"<b>Name:</b> {candidate.name}", styles['Normal']))
            story.append(Paragraph(f"<b>Status:</b> {candidate.status}", styles['Normal']))
            if candidate.feedback:
                story.append(Paragraph(f"<b>Feedback:</b> {candidate.feedback}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue(), 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': 'attachment; filename=feedback_export.pdf'
        }
    
    return jsonify({'success': False, 'message': 'Invalid format'})

@manager_bp.route('/feedback_history')
@manager_required
def feedback_history():
    feedbacks = Feedback.query.filter_by(manager_email=current_user.email).order_by(Feedback.created_at.desc()).all()
    return render_template('manager/feedback_history.html', feedbacks=feedbacks) 