from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models_mongo import User, Candidate, Role, ActivityLog
from email_service import send_candidate_assignment_email
from werkzeug.utils import secure_filename
from bson import ObjectId
import os
import openai
import io
from datetime import datetime
import uuid
import json

# Set OpenAI API key
openai.api_key = "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"

recruiter_bp = Blueprint('recruiter', __name__)

def recruiter_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            # Return JSON error for API endpoints
            if request.path.startswith('/recruiter/') and request.method == 'POST':
                return jsonify({'success': False, 'message': 'Authentication required. Please login first.'}), 401
            return redirect(url_for('login'))
        if current_user.role != 'recruiter':
            flash('Access denied. Recruiter privileges required.', 'error')
            # Return JSON error for API endpoints
            if request.path.startswith('/recruiter/') and request.method == 'POST':
                return jsonify({'success': False, 'message': 'Access denied. Recruiter privileges required.'}), 403
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def parse_resume_with_ai(resume_text):
    """Parse resume using OpenAI API with enhanced prompting"""
    try:
        print("DEBUG: Attempting AI-powered resume parsing...")
        print(f"DEBUG: Resume text length: {len(resume_text)}")
        print(f"DEBUG: Resume text preview: {resume_text[:200]}...")
        print(f"DEBUG: Resume text end: ...{resume_text[-200:]}")
        
        # Create a unique session identifier for this parsing request
        session_id = str(uuid.uuid4())
        print(f"DEBUG: Session ID for this parsing: {session_id}")
        
        system_message = f"""You are a precise resume parser for session {session_id}. Extract information with 100% accuracy - copy EXACT text as written in the resume. Do not modify, interpret, or add any information. Only extract what is explicitly present in the text."""
        
        user_prompt = f"""Session {session_id}: Extract information with 100% accuracy from this resume:
 
Resume text:
{resume_text}
 
CRITICAL REQUIREMENTS FOR 100% ACCURACY:
1. Copy EXACT text as written in the resume - do not modify anything
2. If information is not found, return empty string "" or empty array []
3. For names, preserve exact spelling, capitalization, and formatting
4. For phone numbers, keep exact format (spaces, dashes, parentheses)
5. For email, preserve exact case and format
6. For skills, list only what is explicitly mentioned in the resume
7. For education and experience, copy exact text as written
 
Return ONLY this JSON format:
{{
    "full_name": "exact name from resume or empty string",
    "email": "exact email from resume or empty string",
    "phone": "exact phone from resume or empty string",
    "skills": ["exact skills from resume or empty array"],
    "education": "exact education text from resume or empty string",
    "experience": "exact experience text from resume or empty string"
}}
 
Return ONLY the JSON object, no other text."""

        # Call OpenAI API
        client = openai.OpenAI(api_key=openai.api_key)
        
        # Add more debugging to see what's being sent
        print(f"DEBUG: Resume text length: {len(resume_text)}")
        print(f"DEBUG: Resume text preview: {resume_text[:200]}...")
        print(f"DEBUG: Resume text end: ...{resume_text[-200:]}")
        
        # Add unique timestamp to prevent caching
        timestamp = datetime.now().isoformat()
        print(f"DEBUG: Request timestamp: {timestamp}")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.1,
            # Add unique parameters to prevent caching
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"DEBUG: AI Response: {ai_response[:500]}...")
        
        # Clean the response
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()
        
        # Parse the JSON response
        try:
            parsed_data = json.loads(ai_response)
            print("DEBUG: AI parsing successful!")
            
            # Validate that the extracted data actually matches the resume text
            if parsed_data.get('full_name'):
                full_name = parsed_data['full_name'].lower()
                resume_text_lower = resume_text.lower()
                
                # Check if the extracted name appears in the resume text
                if full_name not in resume_text_lower:
                    print(f"WARNING: Extracted name '{parsed_data['full_name']}' not found in resume text!")
                    print(f"Resume text contains: {resume_text[:100]}...")
                    
                    # Try to find a name in the resume text
                    import re
                    name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
                    potential_names = re.findall(name_pattern, resume_text)
                    if potential_names:
                        print(f"Potential names found in resume: {potential_names[:5]}")
                        # Use the first potential name found
                        parsed_data['full_name'] = potential_names[0]
                        print(f"Corrected name to: {parsed_data['full_name']}")
            
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            return None
            
    except Exception as e:
        print(f"DEBUG: OpenAI API error: {e}")
        return None

def format_ai_education(ai_education_list):
    """Formats the education array from AI parsing into a single string."""
    if not ai_education_list:
        return ""
    
    formatted_education = []
    for edu in ai_education_list:
        degree = edu.get('degree', 'N/A')
        field_of_study = edu.get('field_of_study', 'N/A')
        institution = edu.get('institution', 'N/A')
        start_year = edu.get('start_year', 'N/A')
        end_year = edu.get('end_year', 'N/A')
        
        if start_year == 'N/A' or end_year == 'N/A':
            formatted_education.append(f"{degree} in {field_of_study} from {institution}")
        else:
            formatted_education.append(f"{degree} in {field_of_study} from {institution} ({start_year}-{end_year})")
    
    return ' | '.join(formatted_education)

def format_ai_experience(ai_experience_list):
    """Formats the experience array from AI parsing into a single string."""
    if not ai_experience_list:
        return ""
    
    formatted_experience = []
    for exp in ai_experience_list:
        job_title = exp.get('job_title', 'N/A')
        company = exp.get('company', 'N/A')
        start_date = exp.get('start_date', 'N/A')
        end_date = exp.get('end_date', 'N/A')
        
        if start_date == 'N/A' or end_date == 'N/A':
            formatted_experience.append(f"{job_title} at {company}")
        else:
            formatted_experience.append(f"{job_title} at {company} ({start_date}-{end_date})")
    
    return ' | '.join(formatted_experience)

def verify_extracted_data(extracted_data, resume_text):
    """Verify that extracted data actually exists in the resume text."""
    issues = []
    resume_text_lower = resume_text.lower()
    
    # Check name
    if extracted_data.get('name'):
        name_lower = extracted_data['name'].lower()
        if name_lower not in resume_text_lower:
            issues.append(f"Name '{extracted_data['name']}' not found in resume")
    
    # Check email
    if extracted_data.get('email'):
        email_lower = extracted_data['email'].lower()
        if email_lower not in resume_text_lower:
            issues.append(f"Email '{extracted_data['email']}' not found in resume")
    
    # Check phone
    if extracted_data.get('phone'):
        phone_clean = extracted_data['phone'].replace('-', '').replace(' ', '')
        if phone_clean not in resume_text.replace('-', '').replace(' ', ''):
            issues.append(f"Phone '{extracted_data['phone']}' not found in resume")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }

def correct_extracted_data(extracted_data, resume_text):
    """Attempt to correct extracted data by finding it in the resume text."""
    print("DEBUG: Attempting to correct extracted data...")
    
    # Try to find name
    if not extracted_data.get('name') or extracted_data['name'] not in resume_text:
        import re
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_names = re.findall(name_pattern, resume_text)
        if potential_names:
            corrected_name = potential_names[0]
            print(f"DEBUG: Corrected name from '{extracted_data.get('name', 'None')}' to '{corrected_name}'")
            extracted_data['name'] = corrected_name
            # Update first_name and last_name
            name_parts = corrected_name.split()
            extracted_data['first_name'] = name_parts[0] if name_parts else ''
            extracted_data['last_name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    # Try to find email
    if not extracted_data.get('email') or extracted_data['email'] not in resume_text:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        if emails:
            corrected_email = emails[0]
            print(f"DEBUG: Corrected email from '{extracted_data.get('email', 'None')}' to '{corrected_email}'")
            extracted_data['email'] = corrected_email
    
    # Try to find phone
    if not extracted_data.get('phone') or extracted_data['phone'] not in resume_text:
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phones = re.findall(phone_pattern, resume_text)
        if phones:
            corrected_phone = phones[0]
            print(f"DEBUG: Corrected phone from '{extracted_data.get('phone', 'None')}' to '{corrected_phone}'")
            extracted_data['phone'] = corrected_phone
    
    return extracted_data

@recruiter_bp.route('/debug-db')
@recruiter_required
def debug_db():
    """Debug database connection"""
    try:
        from models_mongo import candidates_collection, candidate_requests_collection
        
        candidates_count = candidates_collection.count_documents({})
        requests_count = candidate_requests_collection.count_documents({})
        
        candidates = list(candidates_collection.find({}).limit(3))
        requests = list(candidate_requests_collection.find({}).limit(3))
        
        debug_info = {
            'candidates_count': candidates_count,
            'requests_count': requests_count,
            'sample_candidates': [{'name': c.get('name'), 'email': c.get('email'), 'status': c.get('status')} for c in candidates],
            'sample_requests': [{'title': r.get('position_title'), 'manager': r.get('manager_email'), 'quantity': r.get('quantity_needed')} for r in requests],
            'mongodb_uri': os.getenv('MONGODB_URI', 'NOT_SET')[:50] + '...' if os.getenv('MONGODB_URI') else 'NOT_SET'
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__})

@recruiter_bp.route('/dashboard')
@recruiter_required
def dashboard():
    """Recruiter Dashboard"""
    try:
        from models_mongo import candidates_collection, candidate_requests_collection
        
        # Fetch all candidates for statistics
        all_candidates = list(candidates_collection.find({}))
        
        # Fetch candidate requests with deadline tracking
        candidate_requests = list(candidate_requests_collection.find({}))
        
        # Convert ObjectId to string for template compatibility
        for candidate in all_candidates:
            candidate['_id'] = str(candidate['_id'])
            
            # Generate reference ID if missing
            if not candidate.get('reference_id'):
                current_date = datetime.now().strftime('%Y%m%d')
                unique_id = str(uuid.uuid4())[:8].upper()
                reference_id = f'REF-{current_date}-{unique_id}'
                candidate['reference_id'] = reference_id
        
        # Process candidate requests with deadline status and manager info
        from models_mongo import users_collection
        for request in candidate_requests:
            request['_id'] = str(request['_id'])
            
            # Add manager information
            if request.get('manager_email'):
                manager = users_collection.find_one({'email': request['manager_email']})
                if manager:
                    request['requester_name'] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}"
                    request['requester_email'] = request['manager_email']
                else:
                    request['requester_name'] = request.get('manager_email', 'Unknown')
                    request['requester_email'] = request.get('manager_email', 'N/A')
            
            # Map correct field names for template
            request['job_title'] = request.get('position_title', 'N/A')
            request['open_positions'] = request.get('quantity_needed', 0)
            
            # Calculate remaining positions
            assigned_count = request.get('assigned_count', 0)
            onboarded_count = request.get('onboarded_count', 0)
            request['remaining_positions'] = request['open_positions'] - onboarded_count
            
            # Calculate deadline status based on created_at (days since request)
            if request.get('created_at'):
                try:
                    if isinstance(request['created_at'], str):
                        # Handle ISO format with or without timezone
                        created_at_str = request['created_at']
                        if 'T' in created_at_str:
                            # ISO format
                            if created_at_str.endswith('Z'):
                                created_at_str = created_at_str[:-1] + '+00:00'
                            elif '+' not in created_at_str and 'Z' not in created_at_str:
                                # No timezone info, assume UTC
                                created_at_str += '+00:00'
                            requested_date = datetime.fromisoformat(created_at_str)
                        else:
                            # Simple date format
                            requested_date = datetime.fromisoformat(created_at_str)
                    else:
                        requested_date = request['created_at']
                    
                    # Calculate days since request
                    days_since_request = (datetime.now() - requested_date.replace(tzinfo=None)).days
                    
                    # Set deadline status based on days since request
                    if days_since_request > 15:
                        request['deadline_status'] = 'overdue'
                        request['deadline_color'] = 'red'
                    elif days_since_request > 7:
                        request['deadline_status'] = 'urgent'
                        request['deadline_color'] = 'yellow'
                    else:
                        request['deadline_status'] = 'active'
                        request['deadline_color'] = 'green'
                    
                    request['days_since_request'] = days_since_request
                    request['requested_date_formatted'] = requested_date.strftime('%Y-%m-%d')
                    
                except Exception as e:
                    print(f"Error processing created_at for request {request.get('_id')}: {e}")
                    request['deadline_status'] = 'unknown'
                    request['deadline_color'] = 'gray'
                    request['days_since_request'] = 0
            
            # Also handle legacy deadline field if it exists
            if request.get('deadline'):
                deadline = request['deadline']
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                
                days_remaining = (deadline - datetime.now()).days
                if days_remaining < 0:
                    request['deadline_status'] = 'overdue'
                    request['deadline_color'] = 'red'
                elif days_remaining <= 7:
                    request['deadline_status'] = 'urgent'
                    request['deadline_color'] = 'yellow'
                elif days_remaining <= 15:
                    request['deadline_status'] = 'warning'
                    request['deadline_color'] = 'orange'
                else:
                    request['deadline_status'] = 'good'
                    request['deadline_color'] = 'green'
                
                request['days_remaining'] = days_remaining
                
                # Update the database with the new reference ID
                try:
                    candidates_collection.update_one(
                        {'_id': ObjectId(candidate['_id'])},
                        {'$set': {'reference_id': reference_id}}
                    )
                except Exception as update_error:
                    print(f"Error updating reference ID for candidate {candidate.get('_id')}: {update_error}")
            
            # Generate name field if missing
            if not candidate.get('name') and (candidate.get('first_name') or candidate.get('last_name')):
                first_name = candidate.get('first_name', '')
                last_name = candidate.get('last_name', '')
                combined_name = f"{first_name} {last_name}".strip()
                candidate['name'] = combined_name
                
                # Update the database with the new name field
                try:
                    candidates_collection.update_one(
                        {'_id': ObjectId(candidate['_id'])},
                        {'$set': {'name': combined_name}}
                    )
                except Exception as update_error:
                    print(f"Error updating name field for candidate {candidate.get('_id')}: {update_error}")
        
        print(f"DEBUG: Dashboard loaded {len(all_candidates)} candidates and {len(candidate_requests)} requests")
        print(f"DEBUG: Sample candidate names: {[c.get('name', 'No name') for c in all_candidates[:3]]}")
        print(f"DEBUG: Sample request titles: {[r.get('position_title', 'No title') for r in candidate_requests[:3]]}")
        
        return render_template('recruiter/dashboard.html', 
                             all_candidates=all_candidates, 
                             candidate_requests=candidate_requests)
        
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading dashboard data: {str(e)}', 'error')
        # Return empty dashboard with error handling
        return render_template('recruiter/dashboard.html', all_candidates=[], candidate_requests=[])


@recruiter_bp.route('/candidates')
@recruiter_required
def candidates():
    """List all candidates for recruiter"""
    try:
        from models_mongo import candidates_collection
        candidates = list(candidates_collection.find({}))
        
        # Convert ObjectId to string and handle date conversion
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
            
            # Generate reference ID if missing
            if not candidate.get('reference_id'):
                current_date = datetime.now().strftime('%Y%m%d')
                unique_id = str(uuid.uuid4())[:8].upper()
                reference_id = f'REF-{current_date}-{unique_id}'
                candidate['reference_id'] = reference_id
                
                # Update the database with the new reference ID
                try:
                    candidates_collection.update_one(
                        {'_id': ObjectId(candidate['_id'])},
                        {'$set': {'reference_id': reference_id}}
                    )
                except Exception as update_error:
                    print(f"Error updating reference ID for candidate {candidate.get('_id')}: {update_error}")
            
            # Generate name field if missing
            if not candidate.get('name') and (candidate.get('first_name') or candidate.get('last_name')):
                first_name = candidate.get('first_name', '')
                last_name = candidate.get('last_name', '')
                combined_name = f"{first_name} {last_name}".strip()
                candidate['name'] = combined_name
                
                # Update the database with the new name field
                try:
                    candidates_collection.update_one(
                        {'_id': ObjectId(candidate['_id'])},
                        {'$set': {'name': combined_name}}
                    )
                except Exception as update_error:
                    print(f"Error updating name field for candidate {candidate.get('_id')}: {update_error}")
            
            # Convert created_at string to datetime object for template compatibility
            created_at = candidate.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        # Handle different ISO formats
                        clean_date = created_at.replace('Z', '+00:00')
                        candidate['created_at'] = datetime.fromisoformat(clean_date)
                    except Exception as date_error:
                        print(f"Date conversion error for candidate {candidate.get('_id')}: {date_error}, date: {created_at}")
                        candidate['created_at'] = None
                # If it's already a datetime object, keep it
                elif not hasattr(created_at, 'strftime'):
                    # If it's some other type, set to None
                    candidate['created_at'] = None
            
        return render_template('recruiter/candidates.html', candidates=candidates)
    except Exception as e:
        print(f"Error loading candidates: {str(e)}")
        flash('Error loading candidates', 'error')
        return redirect(url_for('recruiter.dashboard'))

@recruiter_bp.route('/candidate/<candidate_id>')
@recruiter_required
def candidate_details(candidate_id):
    try:
        from models_mongo import candidates_collection
        from bson import ObjectId
        
        # Try to find the candidate directly from the collection
        candidate_data = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
        
        if candidate_data:
            # Convert ObjectId to string for template compatibility
            candidate_data['_id'] = str(candidate_data['_id'])
            
            # Generate name field if missing
            if not candidate_data.get('name') and (candidate_data.get('first_name') or candidate_data.get('last_name')):
                first_name = candidate_data.get('first_name', '')
                last_name = candidate_data.get('last_name', '')
                combined_name = f"{first_name} {last_name}".strip()
                candidate_data['name'] = combined_name
            
            # Convert created_at string to datetime object for template compatibility
            created_at = candidate_data.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        # Handle different ISO formats
                        clean_date = created_at.replace('Z', '+00:00')
                        candidate_data['created_at'] = datetime.fromisoformat(clean_date)
                    except Exception as date_error:
                        print(f"Date conversion error for candidate {candidate_id}: {date_error}, date: {created_at}")
                        candidate_data['created_at'] = None
            
            # Calculate age from date of birth
            dob = candidate_data.get('dob')
            if dob:
                try:
                    if isinstance(dob, str):
                        # Parse the date string (assuming YYYY-MM-DD format)
                        dob_date = datetime.strptime(dob, '%Y-%m-%d')
                    else:
                        dob_date = dob
                    
                    # Calculate age
                    today = datetime.now()
                    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    candidate_data['age'] = age
                except Exception as age_error:
                    print(f"Age calculation error for candidate {candidate_id}: {age_error}, dob: {dob}")
                    candidate_data['age'] = None
            else:
                candidate_data['age'] = None
            
            return render_template('recruiter/candidate_details.html', candidate=candidate_data)
        else:
            flash('Candidate not found', 'error')
            return redirect(url_for('recruiter.dashboard'))
            
    except Exception as e:
        print(f"Error loading candidate details: {str(e)}")
        flash('Error loading candidate details', 'error')
        return redirect(url_for('recruiter.dashboard'))

@recruiter_bp.route('/delete_candidate/<candidate_id>', methods=['DELETE'])
@recruiter_required
def delete_candidate(candidate_id):
    """Delete a candidate"""
    try:
        from models_mongo import candidates_collection
        
        # Find the candidate first to get their name for logging
        candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'})
        
        # Delete the candidate
        result = candidates_collection.delete_one({'_id': ObjectId(candidate_id)})
        
        if result.deleted_count > 0:
            # Log the deletion activity
            try:
                activity_log = ActivityLog(
                    user_id=current_user.id,
                    action='delete_candidate',
                    details=f'Deleted candidate: {candidate.get("name", "Unknown")} (ID: {candidate_id})'
                )
                activity_log.save()
            except Exception as log_error:
                print(f"Warning: Failed to log deletion activity: {log_error}")
            
            return jsonify({'success': True, 'message': 'Candidate deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete candidate'})
            
    except Exception as e:
        print(f"Error deleting candidate: {str(e)}")
        return jsonify({'success': False, 'message': f'Error deleting candidate: {str(e)}'})

@recruiter_bp.route('/assign_candidate', methods=['POST'])
@recruiter_required
def assign_candidate_route():
    candidate_id = request.form['candidate_id']
    manager_email = request.form['manager_email']
    interview_time = request.form.get('interview_time')
    request_id = request.form.get('request_id')  # New: Link to specific request
    
    # Validate manager email format
    if not manager_email or '@' not in manager_email:
        return jsonify({'success': False, 'message': 'Please enter a valid manager email address'})
    
    candidate = Candidate.find_by_id(candidate_id)
    if candidate:
        # Convert interview_time string to datetime object
        interview_datetime = None
        if interview_time:
            try:
                interview_datetime = datetime.fromisoformat(interview_time.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'success': False, 'message': 'Please enter a valid interview date and time'})
        
        candidate.manager_email = manager_email
        candidate.scheduled_date = interview_datetime
        candidate.status = 'Assigned'
        candidate.assigned_to_manager = True
        candidate.assigned_manager_id = manager_email  # Set manager ID to prevent deletion
        
        # If request_id is provided, link the candidate to that request
        if request_id:
            candidate.linked_request_id = request_id
            print(f"DEBUG: Setting linked_request_id = {request_id} for candidate {candidate_id}")
        else:
            print(f"DEBUG: No request_id provided for candidate {candidate_id}")
        
        candidate.save()
        
        # Update request counts if request_id is provided
        if request_id:
            try:
                from models_mongo import CandidateRequest
                request_obj = CandidateRequest.find_by_id(request_id)
                if request_obj:
                    # Increment assigned count
                    new_assigned_count = request_obj.assigned_count + 1
                    request_obj.update_counts(assigned_count=new_assigned_count)
                    print(f"Updated request {request_id}: assigned_count = {new_assigned_count}")
            except Exception as e:
                print(f"Error updating request counts: {str(e)}")
        
        # Send email to manager
        try:
            send_candidate_assignment_email(
                manager_email, 
                candidate.first_name + ' ' + candidate.last_name,
                interview_datetime
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Don't fail the assignment if email fails
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action='Assigned candidate to manager',
            target_email=manager_email,
            details=f'Assigned candidate {candidate.first_name} {candidate.last_name} to manager {manager_email}'
        )
        activity.save()
        
        return jsonify({'success': True, 'message': 'Candidate assigned successfully'})
    else:
        return jsonify({'success': False, 'message': 'Candidate not found'})

@recruiter_bp.route('/upload_candidate', methods=['GET', 'POST'])
@recruiter_required
def upload_candidate():
    """Upload new candidate"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            position_applied = request.form.get('position_applied')
            
            # Handle file uploads
            resume_file = request.files.get('resume')
            image_file = request.files.get('image')
            
            # Generate reference ID
            current_date = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:8].upper()
            reference_id = f'REF-{current_date}-{unique_id}'
            
            # Create candidate record
            candidate_data = {
                'first_name': first_name,
                'last_name': last_name,
                'name': f"{first_name} {last_name}".strip(),  # Add combined name field
                'email': email,
                'phone': phone,
                'position_applied': position_applied,
                'status': 'Pending',
                'recruiter_email': current_user.email,
                'assigned_by': current_user.email,  # Add this for cluster dashboard compatibility
                'reference_id': reference_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Add additional parsed fields if they exist in the form
            additional_fields = [
                'dob', 'gender', 'skills', 'education', 'experience', 
                'parsing_method', 'age', 'cluster', 'location'
            ]
            
            # Add rating fields if they exist in the form
            rating_fields = [
                'overall_rating', 'communication_skills', 'adaptability', 
                'teamwork_collaboration', 'job_fit', 'other_notes'
            ]
            
            for field in additional_fields:
                field_value = request.form.get(field)
                if field_value:
                    if field == 'skills' and isinstance(field_value, str):
                        # Convert skills string to list if needed
                        try:
                            if field_value.startswith('[') and field_value.endswith(']'):
                                import json
                                candidate_data[field] = json.loads(field_value)
                            else:
                                candidate_data[field] = [skill.strip() for skill in field_value.split(',') if skill.strip()]
                        except:
                            candidate_data[field] = [field_value]
                    else:
                        candidate_data[field] = field_value
            
            # Add rating fields - always include them, defaulting to 0 if not set
            for field in rating_fields:
                field_value = request.form.get(field, '0')
                
                if field in ['overall_rating', 'communication_skills', 'adaptability', 'teamwork_collaboration', 'job_fit']:
                    try:
                        # Handle decimal values properly
                        if field_value and field_value != '0':
                            if field == 'overall_rating':
                                # Store overall rating as float to preserve decimals
                                candidate_data[field] = float(field_value)
                            else:
                                # Store individual ratings as integers
                                if isinstance(field_value, str) and '.' in field_value:
                                    float_value = float(field_value)
                                    candidate_data[field] = int(float_value)
                                else:
                                    candidate_data[field] = int(field_value)
                        else:
                            candidate_data[field] = 0
                    except (ValueError, TypeError) as e:
                        candidate_data[field] = 0
                else:
                    # For non-numeric fields like other_notes
                    candidate_data[field] = field_value if field_value else ''

            
            # Handle file uploads
            if resume_file and resume_file.filename:
                filename = secure_filename(resume_file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                resume_path = os.path.join('static/uploads', unique_filename)
                resume_file.save(resume_path)
                candidate_data['resume_path'] = resume_path
            
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                image_path = os.path.join('static/uploads', unique_filename)
                image_file.save(image_path)
                candidate_data['image_path'] = image_path
            
            # Save to database
            from models_mongo import candidates_collection
            result = candidates_collection.insert_one(candidate_data)
            
            # Log activity
            activity_log = ActivityLog(
                user_email=current_user.email,
                action=f'Added new candidate: {first_name} {last_name}'
            )
            activity_log.save()
            
            flash('Candidate uploaded successfully!', 'success')
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Candidate added successfully!',
                    'reference_id': f'REF-{result.inserted_id}'
                })
            else:
                # Redirect for non-AJAX requests
                return redirect(url_for('recruiter.candidates'))
            
        except Exception as e:
            print(f"Error uploading candidate: {str(e)}")
            flash('Error uploading candidate', 'error')
    
    return redirect(url_for('recruiter.dashboard'))

@recruiter_bp.route('/update_candidate_ratings/<candidate_id>', methods=['POST'])
@recruiter_required
def update_candidate_ratings(candidate_id):
    """Update candidate ratings"""
    try:
        from models_mongo import candidates_collection
        from bson import ObjectId
        
        # Get rating data from form
        rating_data = {
            'overall_rating': request.form.get('overall_rating'),
            'communication_skills': request.form.get('communication_skills'),
            'adaptability': request.form.get('adaptability'),
            'teamwork_collaboration': request.form.get('teamwork_collaboration'),
            'job_fit': request.form.get('job_fit'),
            'other_notes': request.form.get('other_notes'),
            'updated_at': datetime.now().isoformat()
        }
        
        # Convert rating fields to integers and remove None values
        rating_data = {k: v for k, v in rating_data.items() if v is not None}
        
        # Convert numeric rating fields to integers
        numeric_fields = ['overall_rating', 'communication_skills', 'adaptability', 'teamwork_collaboration', 'job_fit']
        for field in numeric_fields:
            if field in rating_data:
                try:
                    rating_data[field] = int(rating_data[field])
                except (ValueError, TypeError):
                    rating_data[field] = 0
        
        # Update candidate in database
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {'$set': rating_data}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Candidate ratings updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No changes made to candidate ratings'
            })
            
    except Exception as e:
        print(f"Error updating candidate ratings: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating ratings: {str(e)}'
        }), 500

@recruiter_bp.route('/assign/<candidate_id>', methods=['POST'])
@recruiter_required
def assign_candidate_to_manager(candidate_id):
    """Assign candidate to manager"""
    try:
        manager_email = request.form.get('manager_email')
        
        if not manager_email:
            return jsonify({'success': False, 'message': 'Manager email required'}), 400
        
        from models_mongo import candidates_collection, users_collection
        
        # Update candidate assignment
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {
                '$set': {
                    'manager_email': manager_email,
                    'status': 'Assigned',
                    'assigned_at': datetime.now().isoformat(),
                    'assigned_by': current_user.email
                }
            }
        )
        
        if result.modified_count > 0:
            # Get candidate and manager details
            candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
            manager = users_collection.find_one({'email': manager_email})
            
            # Send email notification
            try:
                send_candidate_assignment_email(
                    manager_email=manager_email,
                    manager_name=f"{manager.get('first_name', '')} {manager.get('last_name', '')}",
                    candidate_name=f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}",
                    position=candidate.get('position_applied', ''),
                    recruiter_name=f"{current_user.first_name} {current_user.last_name}"
                )
            except Exception as email_error:
                print(f"Email sending failed: {str(email_error)}")
            
            # Log activity
            activity_log = ActivityLog(
                user_email=current_user.email,
                action=f'Assigned {candidate.get("first_name", "")} {candidate.get("last_name", "")} to {manager.get("first_name", "")} {manager.get("last_name", "")}',
                timestamp=datetime.now()
            )
            activity_log.save()
            
            return jsonify({'success': True, 'message': 'Candidate assigned successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to assign candidate'}), 400
            
    except Exception as e:
        print(f"Error assigning candidate: {str(e)}")
        return jsonify({'success': False, 'message': 'Error assigning candidate'}), 500

@recruiter_bp.route('/api/candidates')
@recruiter_required
def api_candidates():
    """API endpoint for candidate data"""
    try:
        from models_mongo import candidates_collection, users_collection
        
        # Get all candidates
        candidates = list(candidates_collection.find({}))
        
        # Enrich with manager information
        for candidate in candidates:
            if candidate.get('manager_email'):
                manager = users_collection.find_one({'email': candidate['manager_email']})
                if manager:
                    candidate['manager_name'] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}"
            
            # Convert ObjectId to string
            candidate['_id'] = str(candidate['_id'])
        
        return jsonify({'success': True, 'candidates': candidates})
        
    except Exception as e:
        print(f"Error getting candidates: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading candidates'}), 500

@recruiter_bp.route('/api/managers')
@recruiter_required
def api_managers():
    """Get list of managers for assignment"""
    try:
        from models_mongo import users_collection
        
        managers = list(users_collection.find({'role': 'manager'}, {
            'first_name': 1, 'last_name': 1, 'email': 1
        }))
        
        manager_list = []
        for manager in managers:
            manager_list.append({
                'email': manager['email'],
                'name': f"{manager.get('first_name', '')} {manager.get('last_name', '')}"
            })
        
        return jsonify({'success': True, 'managers': manager_list})
        
    except Exception as e:
        print(f"Error getting managers: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading managers'}), 500

@recruiter_bp.route('/api/analytics')
@recruiter_required
def get_analytics_data():
    """Get analytics data for recruiter dashboard"""
    try:
        from models_mongo import candidates_collection, users_collection
        from collections import defaultdict
        
        # Get all candidates assigned by this recruiter
        candidates = list(candidates_collection.find({'recruiter_email': current_user.email}))
        
        # Calculate statistics
        total_candidates = len(candidates)
        status_counts = defaultdict(int)
        position_counts = defaultdict(int)
        monthly_stats = defaultdict(int)
        
        for candidate in candidates:
            # Status distribution
            status = candidate.get('status', 'Unknown')
            status_counts[status] += 1
            
            # Position distribution
            position = candidate.get('position_applied', 'Unknown')
            position_counts[position] += 1
            
            # Monthly trends
            created_at = candidate.get('created_at', '')
            if created_at:
                try:
                    # Handle both datetime objects and ISO strings
                    if isinstance(created_at, str):
                        clean_date = created_at.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(clean_date)
                    elif hasattr(created_at, 'strftime'):
                        dt = created_at
                    else:
                        continue  # Skip invalid date types
                    month = dt.strftime('%Y-%m')
                    monthly_stats[month] += 1
                except Exception as e:
                    print(f"Analytics date parsing error: {e}, created_at: {created_at}, type: {type(created_at)}")
                    continue
        
        # Success rate calculation
        selected_count = status_counts.get('Selected', 0)
        success_rate = round((selected_count / total_candidates * 100), 2) if total_candidates > 0 else 0
        
        analytics_data = {
            'total_candidates': total_candidates,
            'status_counts': dict(status_counts),
            'position_counts': dict(position_counts),
            'monthly_stats': dict(monthly_stats),
            'success_rate': success_rate,
            'pending_count': status_counts.get('Pending', 0),
            'assigned_count': status_counts.get('Assigned', 0),
            'selected_count': selected_count,
            'not_selected_count': status_counts.get('Not Selected', 0)
        }
        
        return jsonify({
            'success': True,
            'data': analytics_data
        })
        
    except Exception as e:
        print(f"Error getting analytics data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting analytics data: {str(e)}'
        }), 500

@recruiter_bp.route('/requests')
@recruiter_required
def candidate_requests():
    """Redirect to the main candidate requests page"""
    return redirect(url_for('recruiter.view_candidate_requests'))

@recruiter_bp.route('/api/requests')
@recruiter_required
def api_candidate_requests():
    """Get candidate requests from managers"""
    try:
        from models_mongo import candidate_requests_collection, users_collection
        
        # Get all active requests
        requests = list(candidate_requests_collection.find({'status': {'$ne': 'Completed'}}))
        
        # Enrich with manager information
        for request in requests:
            if request.get('manager_email'):
                manager = users_collection.find_one({'email': request['manager_email']})
                if manager:
                    request['manager_name'] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}"
            
            # Convert ObjectId to string
            request['_id'] = str(request['_id'])
        
        return jsonify({'success': True, 'requests': requests})
        
    except Exception as e:
        print(f"Error getting candidate requests: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading requests'}), 500

@recruiter_bp.route('/test_parse', methods=['GET'])
@recruiter_required
def test_parse():
    """Test route to verify parse_resume endpoint is accessible"""
    return jsonify({'success': True, 'message': 'Parse endpoint is accessible'})

@recruiter_bp.route('/parse_resume', methods=['POST'])
@recruiter_required  # Re-enabled with better error handling
def parse_resume():
    """Parse resume and extract candidate information"""
    try:
        print(f"DEBUG: parse_resume called with files: {list(request.files.keys())}")
        
        if 'resume' not in request.files:
            print("DEBUG: No resume file in request.files")
            return jsonify({'success': False, 'message': 'No resume file uploaded'})
        
        resume_file = request.files['resume']
        print(f"DEBUG: Resume file received: {resume_file.filename}, size: {resume_file.content_length if hasattr(resume_file, 'content_length') else 'unknown'}")
        
        if resume_file.filename == '':
            print("DEBUG: Empty filename")
            return jsonify({'success': False, 'message': 'No resume file selected'})
        
        # Process the actual resume file for real data extraction
        print("DEBUG: Processing real resume file for accurate data extraction")
        
        # Get file extension
        file_ext = resume_file.filename.rsplit('.', 1)[1].lower()
        
        # Extract text from the resume
        resume_text = ""
        
        if file_ext == 'pdf':
            try:
                import fitz  # PyMuPDF
                print("DEBUG: PyMuPDF imported successfully")
                
                # Save temporary file
                temp_path = f"/tmp/{uuid.uuid4()}.pdf"
                print(f"DEBUG: Saving to temp path: {temp_path}")
                resume_file.save(temp_path)
                
                # Check if file was saved
                import os
                if os.path.exists(temp_path):
                    file_size = os.path.getsize(temp_path)
                    print(f"DEBUG: Temp file saved, size: {file_size} bytes")
                    
                    # Verify the file is not empty
                    if file_size == 0:
                        print("ERROR: Temp file is empty (0 bytes)!")
                        return jsonify({'success': False, 'message': 'The uploaded file appears to be empty or corrupted. Please try uploading a different file.'})
                else:
                    print("ERROR: Temp file was not created!")
                    return jsonify({'success': False, 'message': 'Failed to save temporary PDF file'})
                
                # Extract text from PDF
                print("DEBUG: Opening PDF with PyMuPDF...")
                doc = fitz.open(temp_path)
                print(f"DEBUG: PDF opened, pages: {len(doc)}")
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    print(f"DEBUG: Processing page {page_num + 1}")
                    
                    # Try different text extraction methods
                    page_text = page.get_text()
                    print(f"DEBUG: Page {page_num + 1} text length: {len(page_text)}")
                    print(f"DEBUG: Page {page_num + 1} text preview: {page_text[:100]}...")
                    
                    if len(page_text) == 0:
                        print(f"DEBUG: Page {page_num + 1} returned empty text, trying alternative method...")
                        # Try alternative text extraction
                        page_text = page.get_text("text")
                        print(f"DEBUG: Alternative method text length: {len(page_text)}")
                    
                    resume_text += page_text
                
                doc.close()
                print(f"DEBUG: PDF closed")
                
                print(f"DEBUG: Total extracted text length: {len(resume_text)}")
                print(f"DEBUG: Extracted text preview: {resume_text[:300]}...")
                print(f"DEBUG: Extracted text end: ...{resume_text[-300:]}")
                
                # If still no text, try a different approach
                if len(resume_text.strip()) == 0:
                    print("WARNING: No text extracted from PDF, trying alternative methods...")
                    
                    # Try to read file directly
                    try:
                        with open(temp_path, 'rb') as f:
                            file_content = f.read()
                            print(f"DEBUG: File content size: {len(file_content)} bytes")
                            print(f"DEBUG: File content preview: {file_content[:100]}...")
                    except Exception as read_error:
                        print(f"DEBUG: Error reading file directly: {read_error}")
                    
                    # Try alternative PDF parsing with different method
                    try:
                        print("DEBUG: Trying alternative PDF parsing method...")
                        doc = fitz.open(temp_path)
                        for page_num in range(len(doc)):
                            page = doc[page_num]
                            # Try different text extraction parameters
                            page_text = page.get_text("text", sort=True)
                            print(f"DEBUG: Alternative method page {page_num + 1} text length: {len(page_text)}")
                            resume_text += page_text
                        doc.close()
                    except Exception as alt_error:
                        print(f"DEBUG: Alternative PDF parsing also failed: {alt_error}")
                    
                    # If still no text, try using pdfplumber as fallback
                    if len(resume_text.strip()) == 0:
                        try:
                            print("DEBUG: Trying pdfplumber as fallback...")
                            import pdfplumber
                            with pdfplumber.open(temp_path) as pdf:
                                for page in pdf.pages:
                                    page_text = page.extract_text()
                                    if page_text:
                                        resume_text += page_text
                                        print(f"DEBUG: pdfplumber extracted text length: {len(page_text)}")
                        except ImportError:
                            print("DEBUG: pdfplumber not available")
                        except Exception as pdfplumber_error:
                            print(f"DEBUG: pdfplumber failed: {pdfplumber_error}")
                    
                    # If still no text, try OCR with Tesseract
                    if len(resume_text.strip()) == 0:
                        try:
                            print("DEBUG: Trying OCR with Tesseract...")
                            import pytesseract
                            from PIL import Image
                            
                            # Convert PDF pages to images and extract text with OCR
                            doc = fitz.open(temp_path)
                            for page_num in range(len(doc)):
                                page = doc[page_num]
                                print(f"DEBUG: Converting page {page_num + 1} to image for OCR...")
                                
                                # Convert page to image
                                mat = fitz.Matrix(2.0, 2.0)  # Higher resolution for better OCR
                                pix = page.get_pixmap(matrix=mat)
                                img_data = pix.tobytes("png")
                                
                                # Open image with PIL
                                img = Image.open(io.BytesIO(img_data))
                                
                                # Extract text with Tesseract
                                ocr_text = pytesseract.image_to_string(img, lang='eng')
                                print(f"DEBUG: OCR extracted {len(ocr_text)} characters from page {page_num + 1}")
                                print(f"DEBUG: OCR text preview: {ocr_text[:100]}...")
                                
                                resume_text += ocr_text
                                
                                # Clean up
                                pix = None
                                img.close()
                            
                            doc.close()
                            print(f"DEBUG: OCR completed, total text length: {len(resume_text)}")
                            
                        except ImportError:
                            print("DEBUG: pytesseract or PIL not available")
                        except Exception as ocr_error:
                            print(f"DEBUG: OCR failed: {ocr_error}")
                            import traceback
                            traceback.print_exc()
                    
                    print(f"DEBUG: After all methods, total text length: {len(resume_text)}")
                
                # Clean up temp file AFTER all processing is complete
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        print(f"DEBUG: Temp file cleaned up: {temp_path}")
                except Exception as cleanup_error:
                    print(f"WARNING: Failed to clean up temp file: {cleanup_error}")
                
            except ImportError:
                return jsonify({'success': False, 'message': 'PDF parsing not available. Please install PyMuPDF.'})
            except Exception as e:
                print(f"ERROR: PDF parsing failed: {str(e)}")
                print(f"ERROR: Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
                
                # Clean up temp file even if processing failed
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        print(f"DEBUG: Temp file cleaned up after error: {temp_path}")
                except Exception as cleanup_error:
                    print(f"WARNING: Failed to clean up temp file after error: {cleanup_error}")
                
                return jsonify({'success': False, 'message': f'Error parsing PDF: {str(e)}'})
                
        elif file_ext in ['docx', 'doc']:
            return jsonify({
                'success': False, 
                'message': 'Word documents not supported yet. Please convert to PDF format.'
            })
        else:
            return jsonify({'success': False, 'message': 'Unsupported file format. Please upload PDF.'})
        
        # Check if we actually extracted any text
        if len(resume_text.strip()) == 0:
            print("ERROR: No text extracted from resume file!")
            return jsonify({
                'success': False, 
                'message': 'Failed to extract text from the resume file. The file might be corrupted, password-protected, or in an unsupported format. Please try uploading a different PDF file.'
            })
        
        print(f"DEBUG: Proceeding with AI parsing for text length: {len(resume_text)}")
        
        # Try AI parsing first, then fall back to regex
        ai_data = None
        try:
            ai_data = parse_resume_with_ai(resume_text)
        except Exception as e:
            print(f"DEBUG: AI parsing failed: {e}")
            ai_data = None
        
        if ai_data:
            print("DEBUG: Using AI-parsed data")
            # Generate reference ID for AI-parsed data
            current_date = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:8].upper()
            reference_id = f'REF-{current_date}-{unique_id}'
            
            # Map AI response to frontend field names for 100% accuracy
            extracted_data = {
                'name': ai_data.get('full_name', ''),
                'email': ai_data.get('email', ''),
                'phone': ai_data.get('phone', ''),
                'skills': ai_data.get('skills', []),
                'education': ai_data.get('education', ''),
                'experience': ai_data.get('experience', ''),
                'reference_id': reference_id
            }
            
            # Verify extracted data against resume text
            print("DEBUG: Verifying extracted data against resume text...")
            verification_results = verify_extracted_data(extracted_data, resume_text)
            if not verification_results['valid']:
                print(f"WARNING: Data verification failed: {verification_results['issues']}")
                # Try to correct the data
                extracted_data = correct_extracted_data(extracted_data, resume_text)
            
            extracted_data['parsing_method'] = 'AI-Powered (GPT-3.5)'
            print(f"DEBUG: Final extracted data: {extracted_data}")
            return jsonify({
                'success': True,
                'message': 'Resume parsed successfully using AI',
                'data': extracted_data,
                'parsing_method': 'AI-Powered (GPT-3.5)'
            })
        
        print("DEBUG: AI parsing failed, falling back to regex parsing")
        
        # Fallback to simple regex-based parsing
        import re
        
        extracted_data = {
            'name': '',
            'email': '',
            'phone': '',
            'skills': [],
            'education': '',
            'experience': ''
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        if emails:
            extracted_data['email'] = emails[0]
        
        # Extract phone number
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        phones = re.findall(phone_pattern, resume_text)
        if phones:
            extracted_data['phone'] = phones[0]
        
        # Better name extraction logic
        lines = resume_text.split('\n')
        for line in lines[:15]:  # Check first 15 lines
            line = line.strip()
            # Skip lines that are likely not names
            if not line or len(line) < 2:
                continue
            if '@' in line or line.lower() in ['resume', 'cv', 'curriculum vitae']:
                continue
            if re.match(r'^\d+', line) or re.match(r'^phone', line.lower()):
                continue
            if re.match(r'^address', line.lower()) or re.match(r'^email', line.lower()):
                continue
            
            # Check if line looks like a name (contains letters, reasonable length)
            if any(c.isalpha() for c in line) and len(line.split()) <= 4 and len(line) <= 50:
                # Additional checks for name-like patterns
                words = line.split()
                if len(words) >= 1 and all(word.replace('.', '').replace(',', '').isalpha() or len(word) <= 3 for word in words):
                    extracted_data['name'] = line
                    break
        
        print(f"DEBUG: Fallback extracted data: {extracted_data}")
        
        return jsonify({
            'success': True,
            'message': 'Resume parsed successfully (basic extraction)',
            'data': extracted_data,
            'parsing_method': 'Basic Text Extraction'
        })
        
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        # Return basic fallback data even if everything fails
        return jsonify({
            'success': True,
            'message': 'Resume uploaded successfully (manual entry required)',
            'data': {
                'name': '',
                'email': '',
                'phone': '',
                'skills': '',
                'education': '',
                'experience': ''
            },
            'parsing_method': 'Manual Entry Required'
        })

@recruiter_bp.route('/api/analytics')
@recruiter_required  
def api_analytics():
    """API endpoint for analytics data"""
    try:
        from models_mongo import candidates_collection, users_collection
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # Get candidates for this recruiter
        candidates = list(candidates_collection.find({'recruiter_email': current_user.email}))
        
        # Status distribution
        status_counts = defaultdict(int)
        for candidate in candidates:
            status = candidate.get('status', 'Unknown')
            status_counts[status] += 1
        
        # Monthly data (last 6 months)
        monthly_data = defaultdict(int)
        for candidate in candidates:
            created_at = candidate.get('created_at', '')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        clean_date = created_at.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(clean_date)
                    elif hasattr(created_at, 'strftime'):
                        dt = created_at
                    else:
                        continue
                    month_key = dt.strftime('%Y-%m')
                    monthly_data[month_key] += 1
                except Exception as e:
                    print(f"Date parsing error: {e}")
                    continue
        
        # Weekly trends (last 4 weeks)
        weekly_trends = defaultdict(lambda: {'applications': 0, 'selections': 0})
        for candidate in candidates:
            created_at = candidate.get('created_at', '')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        clean_date = created_at.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(clean_date)
                    elif hasattr(created_at, 'strftime'):
                        dt = created_at
                    else:
                        continue
                    
                    # Calculate week number
                    week_start = dt - timedelta(days=dt.weekday())
                    week_key = f"Week {((dt - week_start).days // 7) + 1}"
                    weekly_trends[week_key]['applications'] += 1
                    
                    if candidate.get('status') == 'Selected':
                        weekly_trends[week_key]['selections'] += 1
                except Exception as e:
                    print(f"Weekly trend error: {e}")
                    continue
        
        # Monthly success rates
        monthly_success = defaultdict(float)
        for candidate in candidates:
            created_at = candidate.get('created_at', '')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        clean_date = created_at.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(clean_date)
                    elif hasattr(created_at, 'strftime'):
                        dt = created_at
                    else:
                        continue
                    
                    month_key = dt.strftime('%Y-%m')
                    if candidate.get('status') == 'Selected':
                        monthly_success[month_key] += 1
                except Exception as e:
                    print(f"Success rate error: {e}")
                    continue
        
        # Calculate success rates as percentages
        for month in monthly_success:
            total_in_month = monthly_data.get(month, 1)
            monthly_success[month] = round((monthly_success[month] / total_in_month) * 100, 1)
        
        # HR Performance (if applicable)
        hr_performance = []
        hr_users = list(users_collection.find({'role': 'hr'}))
        for hr in hr_users:
            hr_candidates = [c for c in candidates if c.get('hr_email') == hr.get('email')]
            hr_performance.append({
                'name': hr.get('name', 'Unknown HR'),
                'candidates_added': len(hr_candidates),
                'successful_placements': len([c for c in hr_candidates if c.get('status') == 'Selected'])
            })
        
        # Department distribution
        departments = defaultdict(int)
        for candidate in candidates:
            dept = candidate.get('department', 'General')
            departments[dept] += 1
        
        # Experience level distribution
        experience_levels = [0, 0, 0, 0]  # 0-1, 1-3, 3-5, 5+ years
        for candidate in candidates:
            exp_years = candidate.get('experience_years', 0)
            if exp_years <= 1:
                experience_levels[0] += 1
            elif exp_years <= 3:
                experience_levels[1] += 1
            elif exp_years <= 5:
                experience_levels[2] += 1
            else:
                experience_levels[3] += 1
        
        return jsonify({
            'success': True,
            'status_counts': dict(status_counts),
            'monthly_data': dict(monthly_data),
            'weekly_trends': dict(weekly_trends),
            'monthly_success': dict(monthly_success),
            'hr_performance': hr_performance,
            'departments': dict(departments),
            'experience_levels': experience_levels,
            'total_candidates': len(candidates)
        })
    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@recruiter_bp.route('/candidate-requests', methods=['GET'])
@recruiter_required
def view_candidate_requests():
    """Page to display all candidate requests from all managers"""
    try:
        from models_mongo import candidate_requests_collection, users_collection
        
        # Get all active requests directly from collection
        requests_data = list(candidate_requests_collection.find({'status': {'$ne': 'Completed'}}))
        
        # Process each request with enhanced data
        enhanced_requests = []
        for request in requests_data:
            request['_id'] = str(request['_id'])
            
            # Add manager information
            if request.get('manager_email'):
                manager = users_collection.find_one({'email': request['manager_email']})
                if manager:
                    request['requester_name'] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}"
                    request['requester_email'] = request['manager_email']
                else:
                    request['requester_name'] = request.get('manager_email', 'Unknown')
                    request['requester_email'] = request.get('manager_email', 'N/A')
            
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
                        request['urgency_level'] = 'Normal'
                    
                    request['days_since_request'] = days_since_request
                    request['requested_date_formatted'] = requested_date.strftime('%Y-%m-%d')
                    
                except Exception as e:
                    print(f"Error processing created_at for request {request.get('_id')}: {e}")
                    request['deadline_status'] = 'unknown'
                    request['deadline_color'] = 'gray'
                    request['days_since_request'] = 0
                    request['urgency_level'] = 'Unknown'
            
            enhanced_requests.append(request)
        
        # Calculate totals
        total_requested = sum(req['open_positions'] for req in enhanced_requests)
        total_remaining = sum(req['remaining_positions'] for req in enhanced_requests)
        total_assigned = sum(req.get('assigned_count', 0) for req in enhanced_requests)
        total_onboarded = sum(req.get('onboarded_count', 0) for req in enhanced_requests)
        
        # Get unique manager emails for filtering
        manager_emails = list(set(req.get('manager_email', '') for req in enhanced_requests if req.get('manager_email')))
        
        return render_template('recruiter/candidate_requests.html', 
                             requests=enhanced_requests,
                             total_requested=total_requested,
                             total_remaining=total_remaining,
                             total_assigned=total_assigned,
                             total_onboarded=total_onboarded,
                             manager_emails=manager_emails)
                             
    except Exception as e:
        print(f"Error loading candidate requests: {str(e)}")
        flash('Error loading candidate requests', 'error')
        return render_template('recruiter/candidate_requests.html', 
                             requests=[],
                             total_requested=0,
                             total_remaining=0,
                             total_assigned=0,
                             total_onboarded=0,
                             manager_emails=[])

@recruiter_bp.route('/get-request-stats', methods=['GET'])
@recruiter_required
def get_recruiter_request_stats():
    """Get statistics for all candidate requests"""
    try:
        print("DEBUG: get-request-stats called")
        
        # Simple fallback stats to avoid database errors
        stats = {
            'total_requested': 0,
            'total_remaining': 0,
            'total_assigned': 0,
            'total_onboarded': 0
        }
        
        try:
            from models_mongo import CandidateRequest
            requests = CandidateRequest.find_all_active()
            
            # Calculate statistics
            total_requested = sum(getattr(req, 'quantity_needed', 0) for req in requests)
            total_remaining = sum(getattr(req, 'remaining_count', 0) for req in requests)
            total_assigned = sum(getattr(req, 'assigned_count', 0) for req in requests)
            total_onboarded = sum(getattr(req, 'onboarded_count', 0) for req in requests)
            
            stats = {
                'total_requested': total_requested,
                'total_remaining': total_remaining,
                'total_assigned': total_assigned,
                'total_onboarded': total_onboarded,
                'active_requests_count': len(requests)
            }
        except Exception as db_error:
            print(f"DEBUG: Database error in get-request-stats: {db_error}")
            # Use fallback stats
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error getting request stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@recruiter_bp.route('/get-pending-candidates', methods=['GET'])
@recruiter_required
def get_pending_candidates():
    """Get pending candidates available for assignment"""
    try:
        from models_mongo import candidates_collection
        
        # Get candidates that are pending and not already assigned
        pending_candidates = list(candidates_collection.find({
            'status': 'Pending',
            'manager_email': {'$exists': False}
        }).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for candidate in pending_candidates:
            candidate['_id'] = str(candidate['_id'])
        
        return jsonify({
            'success': True,
            'candidates': pending_candidates
        })
        
    except Exception as e:
        print(f"Error getting pending candidates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@recruiter_bp.route('/logout')
@recruiter_required
def logout():
    """Recruiter logout route - redirects to home page"""
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('index'))
