from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Candidate, User, Role, Feedback
from sqlalchemy import func
from datetime import datetime, timedelta

cluster_bp = Blueprint('cluster', __name__)

def cluster_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'cluster':
            flash('Access denied. Cluster privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@cluster_bp.route('/dashboard')
@cluster_required
def dashboard():
    # Get summary statistics
    total_candidates = Candidate.query.count()
    assigned_candidates = Candidate.query.filter_by(status='assigned').count()
    shortlisted_candidates = Candidate.query.filter_by(status='shortlisted').count()
    rejected_candidates = Candidate.query.filter_by(status='rejected').count()
    on_hold_candidates = Candidate.query.filter_by(status='on_hold').count()
    
    # Get status distribution for pie chart
    status_counts = db.session.query(
        Candidate.status, 
        func.count(Candidate.id)
    ).group_by(Candidate.status).all()
    
    # Get manager performance data
    manager_performance = db.session.query(
        Candidate.assigned_to,
        func.count(Candidate.id).label('total_assigned'),
        func.sum(func.case([(Candidate.status == 'shortlisted', 1)], else_=0)).label('shortlisted'),
        func.sum(func.case([(Candidate.status == 'rejected', 1)], else_=0)).label('rejected')
    ).filter(
        Candidate.assigned_to.isnot(None)
    ).group_by(Candidate.assigned_to).all()
    
    # Get HR submission summary
    hr_submissions = db.session.query(
        Candidate.assigned_by,
        func.count(Candidate.id).label('submissions')
    ).group_by(Candidate.assigned_by).all()
    
    # Get recent activity
    recent_candidates = Candidate.query.order_by(Candidate.created_at.desc()).limit(10).all()
    
    # Get monthly trends
    current_month = datetime.now().replace(day=1)
    monthly_data = db.session.query(
        func.date_trunc('month', Candidate.created_at).label('month'),
        func.count(Candidate.id).label('count')
    ).filter(
        Candidate.created_at >= current_month - timedelta(days=365)
    ).group_by(
        func.date_trunc('month', Candidate.created_at)
    ).order_by(
        func.date_trunc('month', Candidate.created_at)
    ).all()
    
    return render_template('cluster/dashboard.html',
                         total_candidates=total_candidates,
                         assigned_candidates=assigned_candidates,
                         shortlisted_candidates=shortlisted_candidates,
                         rejected_candidates=rejected_candidates,
                         on_hold_candidates=on_hold_candidates,
                         status_counts=status_counts,
                         manager_performance=manager_performance,
                         hr_submissions=hr_submissions,
                         recent_candidates=recent_candidates,
                         monthly_data=monthly_data)

@cluster_bp.route('/candidates')
@cluster_required
def candidates():
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template('cluster/candidates.html', candidates=candidates)

@cluster_bp.route('/candidate/<int:candidate_id>')
@cluster_required
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    feedbacks = Feedback.query.filter_by(candidate_id=candidate_id).order_by(Feedback.created_at.desc()).all()
    
    return render_template('cluster/candidate_detail.html',
                         candidate=candidate,
                         feedbacks=feedbacks)

@cluster_bp.route('/analytics')
@cluster_required
def analytics():
    # Get detailed analytics data
    analytics_data = {
        'total_candidates': Candidate.query.count(),
        'assigned_candidates': Candidate.query.filter_by(status='assigned').count(),
        'shortlisted_candidates': Candidate.query.filter_by(status='shortlisted').count(),
        'rejected_candidates': Candidate.query.filter_by(status='rejected').count(),
        'on_hold_candidates': Candidate.query.filter_by(status='on_hold').count(),
    }
    
    # Get status distribution
    status_distribution = db.session.query(
        Candidate.status,
        func.count(Candidate.id)
    ).group_by(Candidate.status).all()
    
    # Get manager performance
    manager_stats = db.session.query(
        Candidate.assigned_to,
        func.count(Candidate.id).label('total'),
        func.sum(func.case([(Candidate.status == 'shortlisted', 1)], else_=0)).label('shortlisted'),
        func.sum(func.case([(Candidate.status == 'rejected', 1)], else_=0)).label('rejected'),
        func.sum(func.case([(Candidate.status == 'on_hold', 1)], else_=0)).label('on_hold')
    ).filter(
        Candidate.assigned_to.isnot(None)
    ).group_by(Candidate.assigned_to).all()
    
    # Get HR performance
    hr_stats = db.session.query(
        Candidate.assigned_by,
        func.count(Candidate.id).label('submissions'),
        func.sum(func.case([(Candidate.status == 'assigned', 1)], else_=0)).label('assigned'),
        func.sum(func.case([(Candidate.status.in_(['shortlisted', 'rejected', 'on_hold']), 1)], else_=0)).label('reviewed')
    ).group_by(Candidate.assigned_by).all()
    
    return render_template('cluster/analytics.html',
                         analytics_data=analytics_data,
                         status_distribution=status_distribution,
                         manager_stats=manager_stats,
                         hr_stats=hr_stats)

@cluster_bp.route('/reports')
@cluster_required
def reports():
    # Get all candidates for reporting
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    
    # Calculate summary statistics
    total_candidates = len(candidates)
    assigned_count = len([c for c in candidates if c.status == 'assigned'])
    shortlisted_count = len([c for c in candidates if c.status == 'shortlisted'])
    rejected_count = len([c for c in candidates if c.status == 'rejected'])
    on_hold_count = len([c for c in candidates if c.status == 'on_hold'])
    
    # Get top performing managers
    manager_performance = db.session.query(
        Candidate.assigned_to,
        func.count(Candidate.id).label('total'),
        func.sum(func.case([(Candidate.status == 'shortlisted', 1)], else_=0)).label('shortlisted')
    ).filter(
        Candidate.assigned_to.isnot(None)
    ).group_by(Candidate.assigned_to).order_by(
        func.sum(func.case([(Candidate.status == 'shortlisted', 1)], else_=0)).desc()
    ).limit(5).all()
    
    return render_template('cluster/reports.html',
                         total_candidates=total_candidates,
                         assigned_count=assigned_count,
                         shortlisted_count=shortlisted_count,
                         rejected_count=rejected_count,
                         on_hold_count=on_hold_count,
                         manager_performance=manager_performance,
                         candidates=candidates) 