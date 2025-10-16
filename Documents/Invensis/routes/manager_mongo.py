from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models_mongo import User, Candidate, Feedback, ActivityLog
from email_service import send_feedback_notification_email
from datetime import datetime
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from bson import ObjectId

manager_bp = Blueprint('manager', __name__)

def manager_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if current_user.role != 'manager':
            flash('Access denied. Manager privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    try:
        # Get assigned candidates
        from models_mongo import candidates_collection
        assigned_candidates = list(candidates_collection.find({
            'manager_email': current_user.email,
            'status': {'$in': ['New', 'Assigned']}
        }).sort('created_at', -1))
        
        # Get selected candidates
        selected_candidates = list(candidates_collection.find({
            'manager_email': current_user.email,
            'status': 'Selected'
        }).sort('updated_at', -1))
        
        # Get not selected candidates - show ALL rejected candidates to ALL managers
        # This allows managers to see candidates rejected by other managers for transparency
        not_selected_candidates = list(candidates_collection.find({
            'status': {'$in': ['Not Selected', 'Rejected', 'Declined', 'Failed', 'Not Approved']}
        }).sort('updated_at', -1))
        
        # Add a note to each candidate indicating which manager originally rejected them
        for candidate in not_selected_candidates:
            if candidate.get('manager_email') != current_user.email:
                candidate['rejected_by'] = candidate.get('manager_email', 'Unknown Manager')
            else:
                candidate['rejected_by'] = 'You'
        
        # Get reassigned candidates (candidates that were reassigned by this manager)
        reassigned_candidates = list(candidates_collection.find({
            'reassigned_by_manager': current_user.email,
            'status': 'Pending'
        }).sort('updated_at', -1))
        
        return render_template('manager/dashboard_simple.html', 
                             assigned_candidates=assigned_candidates,
                             selected_candidates=selected_candidates,
                             not_selected_candidates=not_selected_candidates,
                             reassigned_candidates=reassigned_candidates)
    except Exception as e:
        print(f"Error in manager dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500

@manager_bp.route('/candidate/<candidate_id>')
@manager_required
def candidate_details(candidate_id):
    
    candidate = Candidate.find_by_id(candidate_id)
    if candidate:
        # Allow all managers to view any candidate for transparency
        # The original assignment check is removed to enable cross-manager visibility
        
        # Fetch feedback history for this candidate
        from models_mongo import feedback_collection
        feedback_history = list(feedback_collection.find({'candidate_id': candidate_id}).sort('timestamp', -1))
        
        # Convert feedback documents to Feedback objects
        feedback_objects = []
        for feedback_data in feedback_history:
            # Check if this feedback needs migration (has status but no rejection_reasons)
            if (feedback_data.get('status') in ['Not Selected', 'Rejected'] and 
                not feedback_data.get('rejection_reasons') and 
                candidate.rejection_reasons):
                # Migrate rejection reasons from candidate to feedback
                feedback_data['rejection_reasons'] = candidate.rejection_reasons
                feedback_data['rejection_notes'] = candidate.rejection_notes
                # Update the feedback record in the database
                feedback_collection.update_one(
                    {'_id': feedback_data['_id']},
                    {'$set': {
                        'rejection_reasons': candidate.rejection_reasons,
                        'rejection_notes': candidate.rejection_notes
                    }}
                )
            
            feedback = Feedback(
                candidate_id=feedback_data['candidate_id'],
                manager_email=feedback_data['manager_email'],
                feedback_text=feedback_data['feedback_text'],
                status=feedback_data['status'],
                overall_impression=feedback_data.get('overall_impression'),
                communication_rating=feedback_data.get('communication_rating'),
                technical_rating=feedback_data.get('technical_rating'),
                problem_solving_rating=feedback_data.get('problem_solving_rating'),
                cultural_fit_rating=feedback_data.get('cultural_fit_rating'),
                manager_rating=feedback_data.get('manager_rating'),
                rejection_reasons=feedback_data.get('rejection_reasons'),
                rejection_notes=feedback_data.get('rejection_notes'),
                next_review_date=feedback_data.get('next_review_date'),
                timestamp=feedback_data.get('timestamp'),
                _id=str(feedback_data['_id'])
            )
            feedback_objects.append(feedback)
        
        # Also check for feedback stored directly in the candidate document
        if candidate.manager_feedback:
            # Create a feedback object from candidate data
            candidate_feedback = Feedback(
                candidate_id=str(candidate._id),
                manager_email=candidate.manager_feedback.get('manager_email', 'Unknown'),
                feedback_text=candidate.manager_feedback.get('feedback', ''),
                status=candidate.status,
                overall_impression=candidate.manager_feedback.get('overall_impression', ''),
                communication_rating=candidate.manager_feedback.get('communication_skills', 0),
                technical_rating=candidate.manager_feedback.get('technical_skills', 0),
                problem_solving_rating=candidate.manager_feedback.get('problem_solving', 0),
                cultural_fit_rating=candidate.manager_feedback.get('cultural_fit', 0),
                manager_rating=candidate.manager_feedback.get('overall_rating', 0),
                rejection_reasons=candidate.rejection_reasons or [],
                rejection_notes=candidate.rejection_notes or '',
                next_review_date=None,
                timestamp=candidate.reviewed_at or candidate.updated_at,
                _id=f"candidate_{candidate._id}"
            )
            feedback_objects.append(candidate_feedback)
        
        # Get the latest feedback to pre-fill the form
        latest_feedback = feedback_objects[0] if feedback_objects else None
        
        return render_template('manager/candidate_details.html', 
                             candidate=candidate, 
                             feedback_history=feedback_objects,
                             latest_feedback=latest_feedback)
    else:
        flash('Candidate not found', 'error')
    
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/add_feedback', methods=['POST'])
@manager_required
def add_feedback():
    candidate_id = request.form['candidate_id']
    status = request.form['status']
    overall_impression = request.form.get('overall_impression', '')
    detailed_feedback = request.form.get('detailed_feedback', '')
    
    # Validate status
    if status not in ['Selected', 'Reassign to Hr', 'Not Selected']:
        return jsonify({'success': False, 'message': 'Invalid status'})
    
    # Get detailed ratings from new rating system
    communication_skills = request.form.get('communication_skills')
    technical_skills = request.form.get('technical_skills')
    problem_solving = request.form.get('problem_solving')
    cultural_fit = request.form.get('cultural_fit')
    manager_rating = request.form.get('manager_rating')
    
    # Get rejection reasons if status is "Not Selected"
    rejection_reasons = []
    rejection_notes = ""
    if status == "Not Selected":
        feedback_rejection_reasons = request.form.getlist('rejection_reasons')
        for reason in feedback_rejection_reasons:
            if reason == 'other':
                other_notes = request.form.get('other_notes', '').strip()
                if other_notes:
                    rejection_reasons.append('Other')
                    rejection_notes = other_notes
            else:
                rejection_reasons.append(reason)
    
    # Get next review date if status is "Reassign to Hr"
    next_review_date = None
    if status == "Reassign to Hr":
        next_review_date_str = request.form.get('next_review_date')
        if next_review_date_str:
            try:
                next_review_date = datetime.strptime(next_review_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid next review date format'})
    
    candidate = Candidate.find_by_id(candidate_id)
    if candidate and candidate.manager_email == current_user.email:
        # Update candidate status, feedback, and detailed ratings
        # If status is "Reassign to Hr", set to "Pending" for recruiter visibility
        if status == "Reassign to Hr":
            candidate.status = "Pending"
            # Reset assignment so recruiter can see it
            candidate.assigned_to_manager = False
            candidate.manager_email = None
            # Track who reassigned this candidate
            candidate.reassigned_by_manager = current_user.email
        else:
            candidate.status = status
        candidate.manager_feedback = detailed_feedback
        candidate.reviewed_at = datetime.utcnow()
        candidate.updated_at = datetime.utcnow()
        
        # Store detailed manager ratings in candidate record (only if status is "Selected")
        if status == "Selected":
            if communication_skills:
                candidate.manager_communication_skills = int(communication_skills)
            if technical_skills:
                candidate.manager_technical_skills = int(technical_skills)
            if problem_solving:
                candidate.manager_problem_solving = int(problem_solving)
            if cultural_fit:
                candidate.manager_cultural_fit = int(cultural_fit)
            if manager_rating:
                candidate.manager_overall_rating = float(manager_rating)
        
        # Store rejection reasons if status is "Not Selected"
        if status == "Not Selected":
            candidate.rejection_reasons = rejection_reasons
            candidate.rejection_notes = rejection_notes
        
        # Store next review date if status is "Reassign to Hr"
        if status == "Reassign to Hr":
            candidate.scheduled_date = next_review_date
        
        # Save candidate updates
        candidate.save()
        
        # Create feedback record with detailed ratings
        feedback = Feedback(
            candidate_id=candidate_id,
            manager_email=current_user.email,
            feedback_text=detailed_feedback,
            status="Pending" if status == "Reassign to Hr" else status,
            overall_impression=overall_impression,
            communication_rating=int(communication_skills) if communication_skills and status == "Selected" else None,
            technical_rating=int(technical_skills) if technical_skills and status == "Selected" else None,
            problem_solving_rating=int(problem_solving) if problem_solving and status == "Selected" else None,
            cultural_fit_rating=int(cultural_fit) if cultural_fit and status == "Selected" else None,
            manager_rating=float(manager_rating) if manager_rating and status == "Selected" else None,
            rejection_reasons=rejection_reasons if status == "Not Selected" else None,
            rejection_notes=rejection_notes if status == "Not Selected" else None,
            next_review_date=next_review_date if status == "Reassign to Hr" else None,
            timestamp=datetime.utcnow()
        )
        feedback.save()
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action=f'Added detailed feedback - {status}',
            details=f'Feedback for {candidate.first_name} {candidate.last_name}: {detailed_feedback[:50]}...'
        )
        activity.save()
        
        # Send notification to HR
        try:
            send_feedback_notification_email(candidate.assigned_by, candidate, status)
        except Exception as e:
            flash('Email notification failed', 'warning')
        
        return jsonify({'success': True, 'message': 'Feedback added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Candidate not found'})

@manager_bp.route('/reassign_candidate', methods=['POST'])
@manager_required
def reassign_candidate():
    candidate_id = request.form['candidate_id']
    note = request.form.get('note', '')
    
    candidate = Candidate.find_by_id(candidate_id)
    if candidate and candidate.manager_email == current_user.email:
        # Reset assignment and set to Pending for recruiter
        candidate.assigned_to_manager = False
        candidate.manager_email = None
        candidate.status = 'Pending'  # Changed from 'New' to 'Pending' for recruiter visibility
        candidate.manager_feedback = None
        candidate.reviewed_at = None
        candidate.reassignment_note = note  # Store the reassignment note
        candidate.reassigned_by_manager = current_user.email  # Track who reassigned this candidate
        candidate.save()
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action='Reassigned candidate to HR',
            target_email=candidate.email,
            details=f'Manager reassigned candidate {candidate.first_name} {candidate.last_name} to HR. Note: {note}'
        )
        activity.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Candidate reassigned to HR successfully'})
        flash('Candidate reassigned to HR successfully', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Candidate not found or not assigned to you'})
        flash('Candidate not found or not assigned to you', 'error')
    
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/export_feedback')
@manager_required
def export_feedback():
    format_type = request.args.get('format', 'csv')
    
    # Get all feedback for this manager
    from models_mongo import feedback_collection, candidates_collection
    feedbacks = list(feedback_collection.find({'manager_email': current_user.email}))
    
    if format_type == 'csv':
        # Create CSV
        data = []
        for feedback in feedbacks:
            candidate = candidates_collection.find_one({'_id': feedback['candidate_id']})
            if candidate:
                data.append({
                    'Candidate Name': candidate.get('name', ''),
                    'Email': candidate.get('email', ''),
                    'Status': feedback.get('status', ''),
                    'Feedback': feedback.get('feedback_text', ''),
                    'Date': feedback.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S')
                })
        
        df = pd.DataFrame(data)
        csv_data = df.to_csv(index=False)
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=feedback_export.csv'}
        )
    
    elif format_type == 'pdf':
        # Create PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Feedback Report")
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, f"Manager: {current_user.name}")
        p.drawString(100, 700, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        y_position = 650
        for feedback in feedbacks:
            candidate = candidates_collection.find_one({'_id': feedback['candidate_id']})
            if candidate and y_position > 100:
                p.drawString(100, y_position, f"Candidate: {candidate.get('name', '')}")
                p.drawString(100, y_position - 20, f"Status: {feedback.get('status', '')}")
                p.drawString(100, y_position - 40, f"Feedback: {feedback.get('feedback_text', '')[:50]}...")
                y_position -= 80
        
        p.showPage()
        p.save()
        buffer.seek(0)
        
        from flask import Response
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': 'attachment; filename=feedback_export.pdf'}
        )
    
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/bulk_move_candidates', methods=['POST'])
@manager_required
def bulk_move_candidates():
    from bson import ObjectId
    from models_mongo import candidates_collection, ActivityLog
    
    try:
        data = request.get_json()
        candidate_ids = data.get('candidate_ids', [])
        new_status = data.get('new_status', '')
        
        if not candidate_ids:
            return jsonify({'success': False, 'message': 'No candidates selected'})
        
        if not new_status:
            return jsonify({'success': False, 'message': 'No status specified'})
        
        # Convert string IDs to ObjectId
        object_ids = [ObjectId(cid) for cid in candidate_ids]
        
        # Get candidate details for logging and verify ownership
        candidates = list(candidates_collection.find({
            '_id': {'$in': object_ids},
            'manager_email': current_user.email
        }))
        
        if not candidates:
            return jsonify({'success': False, 'message': 'No candidates found or not assigned to you'})
        
        # Update candidates status
        result = candidates_collection.update_many(
            {
                '_id': {'$in': object_ids},
                'manager_email': current_user.email
            },
            {
                '$set': {
                    'status': new_status,
                    'reviewed_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            # Log the bulk move activity
            activity = ActivityLog(
                user_email=current_user.email,
                action=f'Bulk moved candidates to {new_status}',
                target_email='',
                details=f'Manager moved {result.modified_count} candidates to {new_status}: {", ".join([c.get("first_name", "") + " " + c.get("last_name", "") for c in candidates])}'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': f'Successfully moved {result.modified_count} candidates to {new_status}'})
        else:
            return jsonify({'success': False, 'message': 'No candidates found to update'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error moving candidates: {str(e)}'})

@manager_bp.route('/bulk_reassign_candidates', methods=['POST'])
@manager_required
def bulk_reassign_candidates():
    from bson import ObjectId
    from models_mongo import candidates_collection, ActivityLog
    
    try:
        data = request.get_json()
        candidate_ids = data.get('candidate_ids', [])
        
        if not candidate_ids:
            return jsonify({'success': False, 'message': 'No candidates selected'})
        
        # Convert string IDs to ObjectId
        object_ids = [ObjectId(cid) for cid in candidate_ids]
        
        # Get candidate details for logging and verify ownership
        candidates = list(candidates_collection.find({
            '_id': {'$in': object_ids},
            'manager_email': current_user.email
        }))
        
        if not candidates:
            return jsonify({'success': False, 'message': 'No candidates found or not assigned to you'})
        
        # Reassign candidates back to HR (remove manager assignment)
        result = candidates_collection.update_many(
            {
                '_id': {'$in': object_ids},
                'manager_email': current_user.email
            },
            {
                '$unset': {
                    'manager_email': '',
                    'scheduled_date': ''
                },
                '$set': {
                    'status': 'Pending',
                    'assigned_to_manager': False,
                    'reassigned_by_manager': current_user.email
                }
            }
        )
        
        if result.modified_count > 0:
            # Log the bulk reassign activity
            activity = ActivityLog(
                user_email=current_user.email,
                action='Bulk reassigned candidates to HR',
                target_email='',
                details=f'Manager reassigned {result.modified_count} candidates back to HR: {", ".join([c.get("first_name", "") + " " + c.get("last_name", "") for c in candidates])}'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': f'Successfully reassigned {result.modified_count} candidates to HR'})
        else:
            return jsonify({'success': False, 'message': 'No candidates found to reassign'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reassigning candidates: {str(e)}'}) 

@manager_bp.route('/test_feedback/<candidate_id>')
@manager_required
def test_feedback(candidate_id):
    """Test route to check feedback data in database"""
    from models_mongo import feedback_collection, candidates_collection
    
    # Check candidate data
    candidate_data = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
    
    # Check feedback data
    feedback_data = list(feedback_collection.find({'candidate_id': candidate_id}))
    
    return jsonify({
        'candidate': candidate_data,
        'feedback_count': len(feedback_data),
        'feedback_data': feedback_data
    }) 

@manager_bp.route('/save-rejection-reasons', methods=['POST'])
@manager_required
def save_rejection_reasons():
    try:
        data = request.get_json()
        candidate_id = data.get('candidate_id')
        rejection_reasons = data.get('rejection_reasons', [])
        rejection_notes = data.get('rejection_notes', '')
        
        if not candidate_id or not rejection_reasons:
            return jsonify({
                'success': False,
                'message': 'Missing required data'
            }), 400
        
        # Update candidate with rejection reasons
        from models_mongo import candidates_collection
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id), 'manager_email': current_user.email},
            {'$set': {
                'rejection_reasons': rejection_reasons,
                'rejection_notes': rejection_notes,
                'status': 'Not Selected',
                'reviewed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }}
        )
        
        if result.modified_count > 0:
            # Log the activity
            activity_log = ActivityLog(
                user_email=current_user.email,
                action=f'Updated rejection reasons for candidate {candidate_id}'
            )
            activity_log.save()
            
            return jsonify({
                'success': True,
                'message': 'Rejection reasons saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Candidate not found or no changes made'
            }), 404
            
    except Exception as e:
        print(f"Error saving rejection reasons: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to save rejection reasons'
        }), 500

@manager_bp.route('/logout')
@manager_required
def logout():
    """Manager logout route - redirects to home page"""
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('index'))

@manager_bp.route('/submit-feedback', methods=['POST'])
@manager_required
def submit_feedback():
    try:
        data = request.get_json()
        
        # Extract data from request
        candidate_id = data.get('candidate_id')
        status = data.get('status')
        communication_skills = data.get('communication_skills', 0)
        technical_skills = data.get('technical_skills', 0)
        problem_solving = data.get('problem_solving', 0)
        cultural_fit = data.get('cultural_fit', 0)
        overall_rating = data.get('overall_rating', 0)
        overall_impression = data.get('overall_impression', '')
        feedback = data.get('feedback', '')
        feedback_date = data.get('feedback_date')
        
        # Extract rejection reasons if status is "Not Selected"
        rejection_reasons = data.get('rejection_reasons', [])
        rejection_notes = data.get('rejection_notes', '')
        
        # Validate required fields
        if not candidate_id or not status:
            return jsonify({'error': 'Candidate ID and status are required'}), 400
        
        # If status is "Not Selected", rejection reasons are required
        if status == 'Not Selected' and not rejection_reasons:
            return jsonify({'error': 'Rejection reasons are required when marking candidate as not selected'}), 400
        
        # Update candidate status and add manager feedback
        from models_mongo import candidates_collection
        
        update_data = {
            'status': status,
            'manager_feedback': {
                'communication_skills': communication_skills,
                'technical_skills': technical_skills,
                'problem_solving': problem_solving,
                'cultural_fit': cultural_fit,
                'overall_rating': overall_rating,
                'overall_impression': overall_impression,
                'feedback': feedback,
                'feedback_date': feedback_date,
                'manager_email': current_user.email
            },
            'reviewed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # If status is "Selected", add selection date
        if status == 'Selected':
            update_data['selected_date'] = datetime.now().isoformat()
        elif status == 'Not Selected':
            update_data['rejection_date'] = datetime.now().isoformat()
        
        # Store rejection reasons if status is "Not Selected"
        if status == "Not Selected":
            update_data['rejection_reasons'] = rejection_reasons
            update_data['rejection_notes'] = rejection_notes
        
        # Update the candidate
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # Log the activity
            activity_log = ActivityLog(
                user_email=current_user.email,
                action=f'Manager feedback submitted - Status: {status}',
                details=f'Feedback submitted for candidate {candidate_id}'
            )
            activity_log.save()
            
            return jsonify({
                'success': True,
                'message': 'Feedback submitted successfully',
                'candidate_id': candidate_id,
                'status': status
            })
        else:
            return jsonify({'error': 'Candidate not found or no changes made'}), 404
            
    except Exception as e:
        print(f"Error submitting manager feedback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manager_bp.route('/analytics/<tab_name>')
@manager_required
def get_analytics_data(tab_name):
    """Get analytics data for Manager dashboard"""
    try:
        from models_mongo import candidates_collection, users_collection
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # Get candidates assigned to this manager
        manager_email = current_user.email
        candidates = list(candidates_collection.find({'manager_email': manager_email}))
        
        # Process data based on tab requested
        if tab_name == 'overview':
            # Status distribution
            status_counts = defaultdict(int)
            for candidate in candidates:
                status = candidate.get('status', 'Pending')
                status_counts[status] += 1
            
            # Monthly data (last 6 months)
            monthly_data = defaultdict(int)
            now = datetime.now()
            for i in range(6):
                month_date = now - timedelta(days=30*i)
                month_key = month_date.strftime('%b %Y')
                # Count candidates processed in this month
                for candidate in candidates:
                    created_date = candidate.get('created_at', now)
                    if isinstance(created_date, str):
                        try:
                            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        except:
                            created_date = now
                    
                    if created_date.strftime('%b %Y') == month_key:
                        monthly_data[month_key] += 1
            
            return jsonify({
                'success': True,
                'status_counts': dict(status_counts),
                'monthly_data': dict(monthly_data),
                'total_candidates': len(candidates),
                'last_updated': datetime.now().isoformat()
            })
            
        elif tab_name == 'trends':
            # Trend data over time
            trend_data = []
            now = datetime.now()
            for i in range(30, 0, -5):  # Last 30 days in 5-day intervals
                date = now - timedelta(days=i)
                date_str = date.strftime('%m/%d')
                
                # Count applications and selections for this period
                applications = 0
                selections = 0
                for candidate in candidates:
                    created_date = candidate.get('created_at', now)
                    if isinstance(created_date, str):
                        try:
                            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        except:
                            created_date = now
                    
                    if abs((created_date - date).days) <= 2:  # Within 2 days
                        applications += 1
                        if candidate.get('status') == 'Selected':
                            selections += 1
                
                success_rate = (selections / applications * 100) if applications > 0 else 0
                
                trend_data.append({
                    'date': date_str,
                    'applications': applications,
                    'selections': selections,
                    'success_rate': round(success_rate, 1)
                })
            
            return jsonify({
                'success': True,
                'trend_data': trend_data,
                'last_updated': datetime.now().isoformat()
            })
            
        elif tab_name == 'performance':
            # Team performance data
            team_data = defaultdict(int)
            response_data = defaultdict(list)
            
            # Get feedback data for response time analysis
            feedback_data = list(candidates_collection.find({'manager_email': manager_email, 'manager_feedback': {'$exists': True}}))
            
            # Mock team data (in real scenario, you'd have team member data)
            team_members = ['Manager Team', 'Self Performance']
            for member in team_members:
                team_data[member] = len([c for c in candidates if c.get('status') == 'Selected']) // len(team_members)
            
            # Response time data (days between assignment and feedback)
            for i in range(7):
                day = (datetime.now() - timedelta(days=i)).strftime('%m/%d')
                avg_response = 2.5 + (i * 0.3)  # Mock data with slight increase over time
                response_data[day] = round(avg_response, 1)
            
            return jsonify({
                'success': True,
                'team_data': dict(team_data),
                'response_data': dict(response_data),
                'last_updated': datetime.now().isoformat()
            })
            
        elif tab_name == 'reports':
            # Department and experience distribution
            department_data = defaultdict(int)
            experience_data = defaultdict(int)
            
            for candidate in candidates:
                # Mock department data (you might have this in candidate data)
                dept = candidate.get('department', 'General')
                department_data[dept] += 1
                
                # Experience level analysis (you might extract this from resume or candidate data)
                exp_years = candidate.get('experience_years', 0)
                if exp_years <= 2:
                    experience_data['0-2 years'] += 1
                elif exp_years <= 5:
                    experience_data['3-5 years'] += 1
                elif exp_years <= 10:
                    experience_data['6-10 years'] += 1
                else:
                    experience_data['10+ years'] += 1
            
            return jsonify({
                'success': True,
                'department_data': dict(department_data),
                'experience_data': dict(experience_data),
                'last_updated': datetime.now().isoformat()
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown tab: {tab_name}'
            }), 400
            
    except Exception as e:
        print(f"Error in Manager analytics {tab_name}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to load analytics data'
        }), 500 

@manager_bp.route('/request-candidates', methods=['GET'])
@manager_required
def request_candidates_page():
    """Page to display all candidate requests for the current manager"""
    try:
        from models_mongo import candidate_requests_collection, users_collection
        
        # Get requests for current manager directly from collection
        requests_data = list(candidate_requests_collection.find({'manager_email': current_user.email}))
        
        # Process each request with enhanced data
        enhanced_requests = []
        for request in requests_data:
            request['_id'] = str(request['_id'])
            
            # Add manager information (self in this case)
            request['requester_name'] = f"{current_user.first_name} {current_user.last_name}"
            request['requester_email'] = current_user.email
            
            # Map correct field names for template
            request['job_title'] = request.get('position_title', 'N/A')
            request['open_positions'] = request.get('quantity_needed', 0)
            
            # Calculate remaining positions
            assigned_count = request.get('assigned_count', 0)
            onboarded_count = request.get('onboarded_count', 0)
            request['remaining_positions'] = request['open_positions'] - onboarded_count
            
            # Calculate deadline status based on created_at
            if request.get('created_at'):
                try:
                    if isinstance(request['created_at'], str):
                        created_at_str = request['created_at']
                        if 'T' in created_at_str:
                            if created_at_str.endswith('Z'):
                                created_at_str = created_at_str[:-1] + '+00:00'
                            elif '+' not in created_at_str and 'Z' not in created_at_str:
                                created_at_str += '+00:00'
                            requested_date = datetime.fromisoformat(created_at_str)
                        else:
                            requested_date = datetime.fromisoformat(created_at_str)
                    else:
                        requested_date = request['created_at']
                    
                    # Calculate days since request
                    days_since_request = (datetime.now() - requested_date.replace(tzinfo=None)).days
                    
                    # Set deadline status based on days since request
                    if days_since_request > 15:
                        request['deadline_status'] = 'overdue'
                        request['deadline_color'] = 'red'
                        request['urgency_level'] = 'Critical'
                    elif days_since_request > 7:
                        request['deadline_status'] = 'urgent'
                        request['deadline_color'] = 'yellow'
                        request['urgency_level'] = 'High'
                    else:
                        request['deadline_status'] = 'active'
                        request['deadline_color'] = 'green'
                        request['urgency_level'] = request.get('urgency_level', 'Normal')
                    
                    request['days_since_request'] = days_since_request
                    request['requested_date_formatted'] = requested_date.strftime('%Y-%m-%d')
                    
                except Exception as e:
                    print(f"Error processing created_at for request {request.get('_id')}: {e}")
                    request['deadline_status'] = 'unknown'
                    request['deadline_color'] = 'gray'
                    request['days_since_request'] = 0
                    request['urgency_level'] = request.get('urgency_level', 'Unknown')
            
            enhanced_requests.append(request)
        
        # Calculate totals
        active_requests = [req for req in enhanced_requests if req.get('status', 'Active') == 'Active']
        total_requested = sum(req['open_positions'] for req in active_requests)
        total_remaining = sum(req['remaining_positions'] for req in active_requests)
        
        return render_template('manager/request_candidates.html', 
                             requests=enhanced_requests,
                             total_requested=total_requested,
                             total_remaining=total_remaining)
                             
    except Exception as e:
        print(f"Error loading candidate requests: {str(e)}")
        flash('Error loading candidate requests', 'error')
        return render_template('manager/request_candidates.html', 
                             requests=[],
                             total_requested=0,
                             total_remaining=0)

@manager_bp.route('/submit-candidate-request', methods=['POST'])
@manager_required
def submit_candidate_request():
    """Submit a new candidate request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['position_title', 'quantity_needed', 'urgency_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Create new request
        from models_mongo import CandidateRequest
        new_request = CandidateRequest(
            manager_email=current_user.email,
            position_title=data['position_title'],
            quantity_needed=int(data['quantity_needed']),
            urgency_level=data['urgency_level'],
            required_skills=data.get('required_skills', ''),
            additional_notes=data.get('additional_notes', '')
        )
        
        if new_request.save():
            # Log the activity
            activity_log = ActivityLog(
                user_email=current_user.email,
                action=f'Requested {data["quantity_needed"]} new candidates for {data["position_title"]}',
                details=f'Urgency: {data["urgency_level"]}, Skills: {data.get("required_skills", "N/A")}'
            )
            activity_log.save()
            
            return jsonify({
                'success': True,
                'message': 'Candidate request submitted successfully',
                'request_id': new_request._id
            })
        else:
            return jsonify({'error': 'Failed to save request'}), 500
            
    except Exception as e:
        print(f"Error submitting candidate request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manager_bp.route('/get-request-stats', methods=['GET'])
@manager_required
def get_request_stats():
    """Get statistics for candidate requests"""
    try:
        from models_mongo import CandidateRequest
        requests = CandidateRequest.find_by_manager(current_user.email)
        
        # Calculate statistics
        active_requests = [req for req in requests if req.status == 'Active']
        total_requested = sum(req.quantity_needed for req in active_requests)
        total_remaining = sum(req.remaining_count for req in active_requests)
        total_assigned = sum(req.assigned_count for req in active_requests)
        total_onboarded = sum(req.onboarded_count for req in active_requests)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_requested': total_requested,
                'total_remaining': total_remaining,
                'total_assigned': total_assigned,
                'total_onboarded': total_onboarded,
                'active_requests_count': len(active_requests)
            }
        })
        
    except Exception as e:
        print(f"Error getting request stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 