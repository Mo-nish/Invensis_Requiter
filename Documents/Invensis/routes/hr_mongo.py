from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models_mongo import User, Candidate, Role, ActivityLog
from email_service import send_candidate_assignment_email
from werkzeug.utils import secure_filename
from bson import ObjectId
import os
import openai
from datetime import datetime
import uuid
import json

# Set OpenAI API key
openai.api_key = "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"

hr_bp = Blueprint('hr', __name__)

def hr_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if current_user.role.lower() not in ['hr_role', 'hr']:  # Support both hr_role and hr for flexibility
            flash('Access denied. HR privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@hr_bp.route('/dashboard')
@hr_required
def dashboard():
    # Get all candidates (for Candidate List tab) using the Candidate model
    from models_mongo import candidates_collection
    
    # Query for ALL candidates (HR users need full visibility)
    # This ensures HR users see the complete hiring pipeline
    candidates_data = list(candidates_collection.find().sort('created_at', -1))
    
    # Convert to Candidate objects for proper data handling
    all_candidates = []
    for data in candidates_data:
        try:
            candidate = Candidate.from_dict(data)
            all_candidates.append(candidate)
        except Exception as e:
            print(f"Error converting candidate data: {e}")
            continue
    
    # Debug logging to check candidate counts by status
    status_counts = {}
    for candidate in all_candidates:
        status = candidate.status or 'Unknown'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"HR Dashboard {current_user.email} candidates by status: {status_counts}")
    
    # Get user counts by role for statistics
    hr_count = User.count_by_role('hr')
    manager_count = User.count_by_role('manager')
    cluster_count = User.count_by_role('cluster')
    
    print(f"User counts - HR: {hr_count}, Manager: {manager_count}, Cluster: {cluster_count}")
    
    # Check if this is an AJAX request for dynamic updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the candidate list HTML for AJAX requests
        return render_template('hr/candidate_list_partial.html', 
                             all_candidates=all_candidates)
    
    return render_template('hr/dashboard.html', 
                         all_candidates=all_candidates,
                         hr_count=hr_count,
                         manager_count=manager_count,
                         cluster_count=cluster_count)

@hr_bp.route('/add_candidate', methods=['POST'])
@hr_required
def add_candidate():
    try:
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        dob = request.form['dob']
        education = request.form['education']
        experience = request.form['experience']
        skills = request.form.get('skills', '')
        
        # Split name into first and last name
        name_parts = name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Process skills - convert comma-separated string to list and clean up
        if skills:
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        else:
            skills_list = []
        
        # Handle file uploads
        resume_path = None
        image_path = None
        
        print(f"DEBUG: Files in request: {list(request.files.keys())}")  # Debug logging
        print(f"DEBUG: Form data keys: {list(request.form.keys())}")  # Debug logging
        print(f"DEBUG: Content type: {request.content_type}")  # Debug logging
        
        # Ensure upload directory exists and has proper permissions
        upload_dir = 'static/uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            print(f"DEBUG: Created upload directory: {upload_dir}")
        
        print(f"DEBUG: Upload directory exists: {os.path.exists(upload_dir)}")
        print(f"DEBUG: Upload directory writable: {os.access(upload_dir, os.W_OK)}")
        
        try:
            if 'resume' in request.files:
                resume_file = request.files['resume']
                if resume_file.filename:
                    from cloud_storage import upload_file_to_s3, is_s3_configured
                    
                    if is_s3_configured():
                        # Upload to S3
                        success, resume_url, s3_key = upload_file_to_s3(resume_file, folder='invensis', file_type='resumes')
                        if success:
                            resume_path = resume_url  # Store full S3 URL
                            print(f"✅ Resume uploaded to S3: {resume_url}")
                        else:
                            print(f"❌ Resume upload failed: {resume_url}")
                            resume_path = None
                    else:
                        # Fallback to local storage
                        filename = secure_filename(f"{uuid.uuid4()}_{resume_file.filename}")
                        resume_path_local = os.path.join('static/uploads', filename)
                        print(f"DEBUG: Saving resume to: {resume_path_local}")  # Debug logging
                        
                        # Check if file was actually saved
                        try:
                            resume_file.save(resume_path_local)
                            if os.path.exists(resume_path_local):
                                print(f"DEBUG: Resume saved successfully to {resume_path_local}")
                                print(f"DEBUG: File size: {os.path.getsize(resume_path_local)} bytes")
                                resume_path = os.path.join('uploads', filename)  # Store relative path for database
                            else:
                                print(f"DEBUG: ERROR: File was not saved to {resume_path_local}")
                                resume_path = None
                        except Exception as save_error:
                            print(f"DEBUG: ERROR saving resume: {str(save_error)}")
                            resume_path = None
        except Exception as e:
            print(f"DEBUG: Error saving resume: {str(e)}")  # Debug logging
            resume_path = None
        
        try:
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file.filename:
                    # Validate file extension
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    file_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                    
                    if file_ext not in allowed_extensions:
                        print(f"DEBUG: Invalid file extension: {file_ext}")
                        image_path = None
                    else:
                        filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
                        image_path = os.path.join('static/uploads', filename)
                        print(f"DEBUG: Saving image to: {image_path}")  # Debug logging
                        
                        # Check if file was actually saved
                        try:
                            image_file.save(image_path)
                            if os.path.exists(image_path):
                                print(f"DEBUG: Image saved successfully to {image_path}")
                                print(f"DEBUG: File size: {os.path.getsize(image_path)} bytes")
                                # Store the path that matches what url_for expects
                                # Since files are saved to 'static/uploads/filename' and template uses url_for('static', filename=...)
                                # We need to store just 'uploads/filename' in the database
                                image_path = os.path.join('uploads', filename)
                            else:
                                print(f"DEBUG: ERROR: File was not saved to {image_path}")
                                image_path = None
                        except Exception as save_error:
                            print(f"DEBUG: ERROR saving image: {str(save_error)}")
                            image_path = None
        except Exception as e:
            print(f"DEBUG: Error saving image: {str(e)}")  # Debug logging
            image_path = None
        
        # Also check for 'photo' field (new form field name)
        try:
            if 'photo' in request.files:
                photo_file = request.files['photo']
                print(f"DEBUG: Photo file object: {photo_file}")  # Debug logging
                print(f"DEBUG: Photo filename: {photo_file.filename}")  # Debug logging
                print(f"DEBUG: Photo content type: {photo_file.content_type}")  # Debug logging
                
                if photo_file.filename:
                    # Validate file extension
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    file_ext = photo_file.filename.rsplit('.', 1)[1].lower() if '.' in photo_file.filename else ''
                    
                    if file_ext not in allowed_extensions:
                        print(f"DEBUG: Invalid file extension: {file_ext}")
                        image_path = None
                    else:
                        filename = secure_filename(f"{uuid.uuid4()}_{photo_file.filename}")
                        image_path = os.path.join('static/uploads', filename)
                        print(f"DEBUG: Saving photo to: {image_path}")  # Debug logging
                        
                        # Check if file was actually saved
                        try:
                            photo_file.save(image_path)
                            if os.path.exists(image_path):
                                print(f"DEBUG: Photo saved successfully to {image_path}")
                                print(f"DEBUG: File size: {os.path.getsize(image_path)} bytes")
                                # Store the path that matches what url_for expects
                                # Since files are saved to 'static/uploads/filename' and template uses url_for('static', filename=...)
                                # We need to store just 'uploads/filename' in the database
                                image_path = os.path.join('uploads', filename)
                            else:
                                print(f"DEBUG: ERROR: File was not saved to {str(image_path)}")
                                image_path = None
                        except Exception as save_error:
                            print(f"DEBUG: ERROR saving photo: {str(save_error)}")
                            image_path = None
        except Exception as e:
            print(f"DEBUG: Error saving photo: {str(e)}")  # Debug logging
            image_path = None
        
        # Get detailed rating fields
        communication_skills = request.form.get('communication_skills')
        adaptability = request.form.get('adaptability')
        teamwork_collaboration = request.form.get('teamwork_collaboration')
        job_fit = request.form.get('job_fit')
        overall_rating = request.form.get('overall_rating')
        other_notes = request.form.get('other_notes')
        
        # Convert ratings to appropriate types
        if communication_skills:
            communication_skills = int(communication_skills)
        if adaptability:
            adaptability = int(adaptability)
        if teamwork_collaboration:
            teamwork_collaboration = int(teamwork_collaboration)
        if job_fit:
            job_fit = int(job_fit)
        if overall_rating:
            overall_rating = float(overall_rating)
        
        # Create candidate
        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            gender=gender,
            dob=dob,
            education=education,
            experience=experience,
            assigned_by=current_user.email,
            resume_path=resume_path,
            image_path=image_path,
            skills=skills_list,
            # Detailed rating fields
            communication_skills=communication_skills,
            adaptability=adaptability,
            teamwork_collaboration=teamwork_collaboration,
            job_fit=job_fit,
            overall_rating=overall_rating,
            other_notes=other_notes
        )
        candidate.save()
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action='Added candidate',
            details=f'Added candidate {first_name} {last_name} ({email})'
        )
        activity.save()
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Candidate added successfully!',
                'reference_id': candidate.reference_id
            })
        else:
            flash('Candidate added successfully!', 'success')
            return redirect(url_for('hr.dashboard'))
        
    except Exception as e:
        print(f"Error adding candidate: {str(e)}")  # Debug logging
        error_message = f'An error occurred while adding the candidate: {str(e)}'
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': error_message
            })
        else:
            flash(error_message, 'error')
            return redirect(url_for('hr.dashboard'))

@hr_bp.route('/parse_resume', methods=['POST'])
@hr_required
def parse_resume():
    """Parse resume and extract candidate information with enhanced logic"""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'message': 'No resume file uploaded'})
        
        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'success': False, 'message': 'No resume file selected'})
        
        # Get file extension
        file_ext = resume_file.filename.rsplit('.', 1)[1].lower()
        
        # Extract text from the resume
        resume_text = ""
        
        if file_ext == 'pdf':
            try:
                import fitz  # PyMuPDF
                # Save temporary file
                temp_path = f"/tmp/{uuid.uuid4()}.pdf"
                resume_file.save(temp_path)
                
                # Extract text from PDF
                doc = fitz.open(temp_path)
                for page in doc:
                    resume_text += page.get_text()
                doc.close()
                
                # Clean up temp file
                os.remove(temp_path)
                
            except ImportError:
                return jsonify({'success': False, 'message': 'PDF parsing not available. Please install PyMuPDF.'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error parsing PDF: {str(e)}'})
                
        elif file_ext == 'docx':
            try:
                from docx import Document
                # Save temporary file
                temp_path = f"/tmp/{uuid.uuid4()}.docx"
                resume_file.save(temp_path)
                
                # Extract text from DOCX
                doc = Document(temp_path)
                for paragraph in doc.paragraphs:
                    resume_text += paragraph.text + "\n"
                
                # Clean up temp file
                os.remove(temp_path)
                
            except ImportError:
                return jsonify({'success': False, 'message': 'Word document parsing not available. Please install python-docx.'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error parsing Word document: {str(e)}'})
                
        elif file_ext == 'doc':
            # For .doc files, suggest conversion to DOCX
            return jsonify({
                'success': False, 
                'message': 'DOC files are not directly supported. Please convert your resume to DOCX or PDF format for better compatibility.'
            })
        else:
            return jsonify({'success': False, 'message': 'Unsupported file format. Please upload PDF, DOC, or DOCX.'})
        
        # Try AI parsing first, then fall back to regex
        ai_data = parse_resume_with_ai(resume_text)
        
        if ai_data:
            print("DEBUG: Using AI-parsed data")
            # Map AI response to our expected format
            extracted_data = {
                'name': ai_data.get('full_name', ''),
                'email': ai_data.get('email', ''),
                'phone': ai_data.get('phone', ''),
                'dob': ai_data.get('date_of_birth', ''),
                'gender': ai_data.get('gender', ''),
                'skills': ai_data.get('skills', []),
                'education': format_ai_education(ai_data.get('education', [])),
                'experience': format_ai_experience(ai_data.get('experience', []))
            }
            extracted_data['parsing_method'] = 'AI-Powered (GPT-3.5)'
            print(f"DEBUG: AI extracted data: {extracted_data}")
            return jsonify({
                'success': True,
                'message': 'Resume parsed successfully using AI',
                'data': extracted_data,
                'parsing_method': 'AI-Powered (GPT-3.5)'
            })
        
        print("DEBUG: AI parsing failed, falling back to regex parsing")
        extracted_data = parse_resume_text_enhanced(resume_text)
        
        # Add debugging information
        print(f"DEBUG: Resume text length: {len(resume_text)}")
        print(f"DEBUG: Final extracted data: {extracted_data}")
        
        # Log any fields that couldn't be extracted
        missing_fields = []
        for field, value in extracted_data.items():
            if not value or (isinstance(value, list) and len(value) == 0):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"DEBUG: Missing fields: {missing_fields}")
        
        extracted_data['parsing_method'] = 'Regex Pattern Matching'
        return jsonify({
            'success': True, 
            'message': 'Resume parsed successfully',
            'data': extracted_data,
            'debug': {
                'text_length': len(resume_text),
                'missing_fields': missing_fields,
                'sample_text': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error parsing resume: {str(e)}'})

def parse_resume_text_enhanced(text):
    """Enhanced resume text parsing with improved regex patterns"""
    import re
    
    # Clean and normalize text first
    def clean_text(text):
        """Clean and normalize text for better parsing"""
        # Remove extra whitespace and normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common noise words and phrases
        noise_words = [
            'the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'been', 'will', 'can', 'are', 'was', 'were',
            'skills', 'abilities', 'applications', 'proficiency', 'education', 'experience', 'background', 'section',
            'resume', 'cv', 'curriculum vitae', 'personal', 'information', 'details', 'summary', 'objective'
        ]
        
        # Remove noise words (but keep them if they're part of actual content)
        for noise in noise_words:
            # Only remove standalone noise words, not those that are part of meaningful phrases
            text = re.sub(rf'\b{noise}\b', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    # Clean the input text
    cleaned_text = clean_text(text)
    print(f"DEBUG: Original text length: {len(text)}")
    print(f"DEBUG: Cleaned text length: {len(cleaned_text)}")
    
    extracted_data = {
        'name': '',
        'email': '',
        'phone': '',
        'dob': '',
        'gender': '',
        'skills': [],
        'education': '',
        'experience': ''
    }
    
    # 1. Extract Name - Look for capitalized words near "Name" or from top of document
    name_patterns = [
        r'(?:Name|Full Name|Candidate|Applicant)[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # First line with capitalized words
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s+(?:Email|Phone|Address|Objective))'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
        if match and len(match.group(1).split()) >= 2:  # At least 2 words
            extracted_data['name'] = match.group(1).strip()
            break
    
    # 2. Extract Email - Enhanced email pattern with better handling
    email_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
        r'[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}',  # Email with spaces
        r'(?:Email|E-mail|Mail|Contact)[\s:]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # Labeled email
        r'(?:Email|E-mail|Mail|Contact)[\s:]*([A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,})'  # Labeled email with spaces
    ]
    
    for pattern in email_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            email = match.group(1) if len(match.groups()) > 0 else match.group(0)
            # Clean up email by removing extra spaces and special characters
            email = re.sub(r'[^\w@.-]', '', email)
            if '@' in email and '.' in email.split('@')[1]:
                extracted_data['email'] = email
                break
    
    # If email still not found, try to find it in the entire text with more aggressive cleaning
    if not extracted_data['email']:
        # Look for email-like patterns and clean them up
        potential_emails = re.findall(r'[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}', cleaned_text)
        for potential_email in potential_emails:
            cleaned_email = re.sub(r'[^\w@.-]', '', potential_email)
            if '@' in cleaned_email and '.' in cleaned_email.split('@')[1]:
                extracted_data['email'] = cleaned_email
                break
    
    # 3. Extract Phone - Enhanced phone pattern
    phone_patterns = [
        r'(\+?\d[\d\s-]{8,}\d)',  # International format
        r'(\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4}))',  # US format
        r'(\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4})',  # General format
        r'(?:Phone|Mobile|Tel|Contact)[\s:]*(\+?[\d\s\-\(\)\.]+)'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            phone = re.sub(r'[^\d+]', '', match.group(1))  # Keep only digits and +
            if len(phone) >= 10:  # Minimum 10 digits
                extracted_data['phone'] = phone
                break
    
    # 4. Extract Date of Birth - Look for DOB patterns
    dob_patterns = [
        r'(?:DOB|Date of Birth|Birth Date|Born)[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(?:DOB|Date of Birth|Birth Date|Born)[\s:]*(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',  # General date format
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})'  # Month name format
    ]
    
    for pattern in dob_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            extracted_data['dob'] = match.group(1)
            break
    
    # 5. Extract Gender - Look for gender keywords
    gender_patterns = [
        r'\b(Male|Female|Other)\b',
        r'(?:Gender|Sex)[\s:]*([MF]|Male|Female|Other)',
        r'\b(M|F|MALE|FEMALE)\b'
    ]
    
    for pattern in gender_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            gender = match.group(1).upper()
            if gender in ['M', 'MALE']:
                extracted_data['gender'] = 'Male'
            elif gender in ['F', 'FEMALE']:
                extracted_data['gender'] = 'Female'
            else:
                extracted_data['gender'] = 'Other'
            break
    
    # 6. Extract Skills - Completely rewritten for clean, formatted output
    skills_keywords = [
        # Programming Languages
        'JavaScript', 'Python', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'TypeScript',
        'HTML', 'CSS', 'SQL', 'R', 'MATLAB', 'Scala', 'Perl', 'Shell', 'Bash', 'PowerShell',
        
        # Frameworks & Libraries
        'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Laravel', 'ASP.NET',
        'jQuery', 'Bootstrap', 'Tailwind CSS', 'Material-UI', 'Redux', 'Vuex', 'GraphQL', 'REST API',
        
        # Databases
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions',
        'Terraform', 'Ansible', 'Chef', 'Puppet', 'Vagrant',
        
        # Tools & Platforms
        'Git', 'SVN', 'JIRA', 'Confluence', 'Slack', 'Teams', 'Zoom', 'Figma', 'Adobe Creative Suite',
        'VS Code', 'IntelliJ', 'Eclipse', 'Xcode', 'Android Studio',
        
        # Methodologies
        'Agile', 'Scrum', 'Kanban', 'Waterfall', 'DevOps', 'CI/CD', 'TDD', 'BDD', 'Pair Programming',
        
        # Soft Skills
        'Leadership', 'Communication', 'Problem Solving', 'Critical Thinking', 'Teamwork', 'Time Management',
        'Project Management', 'Customer Service', 'Analytical Skills', 'Creativity',
        
        # Office & Business Tools
        'MS Office', 'Power BI', 'Excel', 'Word', 'PowerPoint', 'Outlook', 'Access', 'Project', 'Visio',
        'Tableau', 'Salesforce', 'SAP', 'Oracle', 'QuickBooks', 'Adobe Photoshop', 'Illustrator',
        
        # Web & Design
        'Web Design', 'Web Designing', 'HTML5', 'CSS3', 'Responsive Design', 'UI/UX', 'Photoshop', 'Illustrator',
        'Figma', 'Sketch', 'Adobe XD', 'Wireframing', 'Prototyping'
    ]
    
    found_skills = []
    
    # Look for skills section with very specific patterns
    skills_section_patterns = [
        # Look for "Skills & Abilities" section specifically
        r'(?:Skills\s*&\s*Abilities|SKILLS\s*&\s*ABILITIES)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:Skills\s*&\s*Abilities|SKILLS\s*&\s*ABILITIES)[\s:]*((?:[^•\n]+\n?)+)',
        
        # Look for "APPLICATIONS PROFICIENCY" section
        r'(?:APPLICATIONS\s*PROFICIENCY|Applications\s*Proficiency)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:APPLICATIONS\s*PROFICIENCY|Applications\s*Proficiency)[\s:]*((?:[^•\n]+\n?)+)',
        
        # Look for "Technical Skills" section
        r'(?:Technical\s*Skills|TECHNICAL\s*SKILLS)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:Technical\s*Skills|TECHNICAL\s*SKILLS)[\s:]*((?:[^•\n]+\n?)+)',
        
        # Look for "Skills" section (but be more careful)
        r'(?:^|\n)(?:Skills|SKILLS)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:^|\n)(?:Skills|SKILLS)[\s:]*((?:[^•\n]+\n?)+)'
    ]
    
    skills_section_text = ""
    for pattern in skills_section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            skills_section_text = match.group(1)
            print(f"DEBUG: Found skills section with pattern: {pattern}")
            print(f"DEBUG: Skills section content: {skills_section_text[:300]}...")
            break
    
    # Extract skills from the skills section if found
    if skills_section_text:
        # Clean the skills section text
        skills_section_text = re.sub(r'\s+', ' ', skills_section_text.strip())
        
        # Look for known skills in the skills section
        for skill in skills_keywords:
            if re.search(rf'\b{re.escape(skill)}\b', skills_section_text, re.IGNORECASE):
                found_skills.append(skill)
        
        # Also look for bullet points or list items
        bullet_skills = re.findall(r'[•\-\*]\s*([A-Za-z][A-Za-z0-9\s\(\)]+)', skills_section_text)
        for skill in bullet_skills:
            skill = skill.strip()
            if (skill and 
                len(skill) > 2 and 
                skill.lower() not in ['the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'been', 'will', 'can', 'are', 'was', 'were'] and
                skill.lower() not in [s.lower() for s in found_skills]):
                found_skills.append(skill)
        
        # Look for comma-separated skills in the skills section
        comma_skills = re.split(r'[,;]', skills_section_text)
        for skill in comma_skills:
            skill = skill.strip()
            if (skill and 
                len(skill) > 2 and 
                skill.lower() not in ['the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'been', 'will', 'can', 'are', 'was', 'were', 'skills', 'abilities', 'applications', 'proficiency'] and
                skill.lower() not in [s.lower() for s in found_skills]):
                found_skills.append(skill)
    
    # If no skills section found, look for skills throughout the document
    if not found_skills:
        print("DEBUG: No skills section found, searching throughout document")
        for skill in skills_keywords:
            if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
                found_skills.append(skill)
    
    # Clean up skills - remove duplicates and sort
    found_skills = list(set(found_skills))
    found_skills.sort()
    
    # Filter out any skills that look like work experience or job descriptions
    filtered_skills = []
    work_experience_indicators = [
        'responsibilities', 'team lead', 'pvt ltd', 'working as', 'production', 'quality', 'organizing',
        'present', 'role', 'until', 'company', 'corp', 'inc', 'ltd', 'llc', 'pvt', 'limited'
    ]
    
    for skill in found_skills:
        skill_lower = skill.lower()
        is_work_experience = False
        
        for indicator in work_experience_indicators:
            if indicator in skill_lower:
                is_work_experience = True
                break
        
        if not is_work_experience:
            filtered_skills.append(skill)
    
    # If we still don't have skills, try to extract from the entire document more intelligently
    if not filtered_skills:
        print("DEBUG: No skills found with keywords, trying intelligent extraction")
        # Look for technical terms and tools mentioned in the document
        technical_patterns = [
            r'\b(?:MS Office|Power BI|Excel|Word|PowerPoint|Outlook|Access|Project|Visio)\b',
            r'\b(?:Python|Java|JavaScript|HTML|CSS|SQL|React|Angular|Vue|Node\.js)\b',
            r'\b(?:Git|Docker|AWS|Azure|Google Cloud|Kubernetes|Jenkins)\b',
            r'\b(?:Photoshop|Illustrator|Figma|Sketch|Adobe XD)\b',
            r'\b(?:Agile|Scrum|DevOps|CI/CD|TDD|BDD)\b'
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            filtered_skills.extend(matches)
        
        # Remove duplicates again
        filtered_skills = list(set(filtered_skills))
        filtered_skills.sort()
    
    extracted_data['skills'] = filtered_skills
    print(f"DEBUG: Final extracted skills (after filtering): {filtered_skills}")
    
    # 7. Extract Education - Completely rewritten for clean, formatted output
    education_text = []
    
    # Look for education section specifically - be more precise and avoid skills section
    education_section_patterns = [
        # Look for "Education" section specifically
        r'(?:^|\n)(?:Education|EDUCATION)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:^|\n)(?:Education|EDUCATION)[\s:]*((?:[^•\n]+\n?)+)',
        
        # Look for "Academic" section
        r'(?:^|\n)(?:Academic|ACADEMIC)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:^|\n)(?:Academic|ACADEMIC)[\s:]*((?:[^•\n]+\n?)+)',
        
        # Look for "Qualifications" section
        r'(?:^|\n)(?:Qualifications|QUALIFICATIONS)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:^|\n)(?:Qualifications|QUALIFICATIONS)[\s:]*((?:[^•\n]+\n?)+)',
        
        # Look for "Educational Background" section
        r'(?:^|\n)(?:Educational Background|EDUCATIONAL BACKGROUND)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:^|\n)(?:Educational Background|EDUCATIONAL BACKGROUND)[\s:]*((?:[^•\n]+\n?)+)'
    ]
    
    education_section_text = ""
    for pattern in education_section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            education_section_text = match.group(1)
            print(f"DEBUG: Found education section with pattern: {pattern}")
            print(f"DEBUG: Education section content: {education_section_text[:300]}...")
            break
    
    if education_section_text:
        # Clean the education section text
        education_section_text = re.sub(r'\s+', ' ', education_section_text.strip())
        
        # Extract structured education information
        # Look for degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?Tech|M\.?Tech|B\.?E|M\.?E)[\s\w]*',
            r'(Computer Science|Engineering|Information Technology|Software Engineering|Data Science|Business Administration|Science|Arts|Commerce)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, education_section_text, re.IGNORECASE)
            education_text.extend(matches)
        
        # Look for institution names - be more specific
        institution_patterns = [
            r'(?:University|College|Institute|School)[\s\w]+',
            r'(?:Graduated|Completed|Passed)[\s\w]*(?:in|from)[\s\w]+',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|College|Institute|School))',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:science|arts|degree|junior|high|school))'
        ]
        
        for pattern in institution_patterns:
            matches = re.findall(pattern, education_section_text, re.IGNORECASE)
            education_text.extend(matches)
        
        # Look for years - be more specific
        year_patterns = [
            r'\b(19|20)\d{2}\b',  # Years 1900-2099
            r'(?:Graduated|Completed|Passed)[\s\w]*(\d{4})',
            r'(\d{4})'  # Any 4-digit year
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, education_section_text, re.IGNORECASE)
            education_text.extend(matches)
        
        # If we found structured education, use it
        if education_text:
            # Clean up education text - remove duplicates and sort
            education_text = list(set(education_text))
            education_text.sort()
            extracted_data['education'] = ' | '.join(education_text)
        else:
            # Fallback to the entire education section
            extracted_data['education'] = education_section_text.strip()
    else:
        print("DEBUG: No education section found, searching throughout document")
        # Fallback: use basic education extraction
        if not extracted_data['education']:
            extracted_data['education'] = "Education information not found in resume"
    
    # Clean and format the education output
    if extracted_data['education']:
        # Remove extra spaces and clean up the format
        education_clean = re.sub(r'\s+', ' ', extracted_data['education'])
        education_clean = re.sub(r'\|\s*\|', '|', education_clean)  # Remove double pipes
        education_clean = re.sub(r'^\|\s*', '', education_clean)  # Remove leading pipe
        education_clean = re.sub(r'\s*\|$', '', education_clean)  # Remove trailing pipe
        extracted_data['education'] = education_clean.strip()
    
    print(f"DEBUG: Final extracted education: {extracted_data['education']}")
    
    # 8. Extract Work Experience - Look for experience patterns with better calculation
    experience_patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
        r'(?:experience|exp)[\s\w]*(\d+)\s*(?:years?|yrs?)',
        r'(?:worked|experience)[\s\w]*(\d+)\s*(?:years?|yrs?)',
        r'(?:Total Experience|Work Experience)[\s:]*(\d+)\s*(?:years?|yrs?)',
        r'(?:Experience|Work History|Employment)[\s:]*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:experience|exp)',  # More flexible pattern
        r'(?:experience|exp)[\s\w]*(\d+)\s*(?:years?|yrs?)',  # Reverse pattern
        r'(\d+)\s*(?:years?|yrs?)',  # Just years mentioned
    ]
    
    years_of_experience = None
    for pattern in experience_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            years_of_experience = int(match.group(1))
            print(f"DEBUG: Found years of experience: {years_of_experience}")
            break
    
    # Look for experience section
    experience_section_patterns = [
        r'(?:Experience|Work History|Employment|Professional Experience|EXPERIENCE)[\s:]*([^•\n]+(?:\n[^•\n]+)*)',
        r'(?:Experience|Work History|Employment|Professional Experience|EXPERIENCE)[\s:]*((?:[^•\n]+\n?)+)'
    ]
    
    experience_section_text = ""
    for pattern in experience_section_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            experience_section_text = match.group(1)
            break
    
    # If we found years of experience, use that
    if years_of_experience:
        extracted_data['experience'] = f"{years_of_experience} years of experience"
    elif experience_section_text:
        print(f"DEBUG: Found experience section: {experience_section_text[:200]}...")
        
        # Extract key information from experience section
        experience_info = []
        
        # Look for job titles
        job_title_patterns = [
            r'(?:Software Engineer|Developer|Programmer|Analyst|Manager|Lead|Senior|Junior|Full Stack|Frontend|Backend|DevOps|Data Scientist|QA|Tester)[\s\w]*',
            r'(?:Engineer|Developer|Programmer|Analyst|Manager|Lead|Senior|Junior)[\s\w]*'
        ]
        
        for pattern in job_title_patterns:
            matches = re.findall(pattern, experience_section_text, re.IGNORECASE)
            experience_info.extend(matches)
        
        # Look for company names
        company_patterns = [
            r'(?:at|with|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:Company|Corp|Inc|Ltd|LLC|Pvt|Limited)[\s\w]*'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, experience_section_text, re.IGNORECASE)
            experience_info.extend(matches)
        
        # Combine information
        if experience_info:
            # Clean up experience info - remove duplicates and sort
            experience_info = list(set(experience_info))
            experience_info.sort()
            extracted_data['experience'] = ' | '.join(experience_info)[:200] + "..."
        else:
            # Clean up the experience section text
            cleaned_text = re.sub(r'\s+', ' ', experience_section_text.strip())
            extracted_data['experience'] = cleaned_text[:200] + "..."
    else:
        print("DEBUG: No experience section found, searching throughout document")
        # Fallback: look for experience patterns throughout the document
        for pattern in experience_patterns:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                years = match.group(1)
                extracted_data['experience'] = f"{years} years of experience"
                break
    
    print(f"DEBUG: Extracted experience: {extracted_data['experience']}")
    
    # If name wasn't found by patterns, try to extract from email
    if not extracted_data['name'] and extracted_data['email']:
        email_name = extracted_data['email'].split('@')[0]
        if '.' in email_name:
            name_parts = email_name.split('.')
            extracted_data['name'] = ' '.join([part.title() for part in name_parts])
        else:
            extracted_data['name'] = email_name.title()
    
    return extracted_data

def parse_resume_with_ai(resume_text):
    """Parse resume using OpenAI API with the exact prompt provided by user"""
    try:
        print("DEBUG: Attempting AI-powered resume parsing with exact prompt...")
        
        # Use the exact system message and prompt provided by user
        system_message = """You are an intelligent resume parser. Your job is to read raw text from resumes and extract candidate details in a clean, structured JSON format. You must strictly follow the JSON schema provided, avoid mixing unrelated information between fields, and remove duplicates or noise words."""
        
        user_prompt = f"""Extract the following fields from the given resume text:

- full_name
- email
- phone
- date_of_birth (format: YYYY-MM-DD if available, else null)
- gender
- skills (array of clean skill names only, no extra words)
- education (array of objects with: degree, field_of_study, institution, start_year, end_year)
- experience (array of objects with: job_title, company, start_date, end_date, responsibilities)

Rules:
1. Education entries must be chronological from earliest to latest.
2. Merge duplicates of the same institution into one record.
3. Remove any words not related to the requested field (e.g., do not include "skills" word inside skills list).
4. If a field is missing, set its value to null (not empty string).
5. Date of birth should be taken from resume if explicitly mentioned. If found, output in YYYY-MM-DD format. 
6. For skills, list only unique, clearly identifiable skills.
7. For education, link each degree with its institution and years.
8. Do not output any extra commentary—only return valid JSON.

Resume text:
{resume_text}

Expected Output Example:
{{
  "full_name": "Monish Reddy",
  "email": "monish.reddy@email.com",
  "phone": "7013984388",
  "date_of_birth": "1994-08-12",
  "gender": "Male",
  "skills": ["Python", "SQL", "Communication", "MS Office", "Web Designing"],
  "education": [
    {{
      "degree": "Bachelor of Science",
      "field_of_study": "Science & Arts",
      "institution": "Vijayam Science & Arts Degree College",
      "start_year": 2016,
      "end_year": 2019
    }},
    {{
      "degree": "PUC",
      "field_of_study": "Science",
      "institution": "Sri Chaitanya Junior College",
      "start_year": 2014,
      "end_year": 2016
    }},
    {{
      "degree": "SSC",
      "field_of_study": null,
      "institution": "Vijaya EM High School",
      "start_year": null,
      "end_year": 2014
    }}
  ],
  "experience": [
    {{
      "job_title": "Web Designer",
      "company": "ABC Technologies",
      "start_date": "2019-06",
      "end_date": "2023-08",
      "responsibilities": [
        "Designed and maintained company website",
        "Collaborated with developers to implement UI/UX changes"
      ]
    }}
  ]
}}

Return ONLY the JSON object, no additional text or explanations."""

        # Call OpenAI API with latest syntax
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.1  # Low temperature for consistent, structured output
        )
        
        # Extract the response content
        ai_response = response.choices[0].message.content.strip()
        print(f"DEBUG: AI Response: {ai_response[:500]}...")
        
        # Clean the response - remove any markdown formatting
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()
        
        # Parse the JSON response
        try:
            parsed_data = json.loads(ai_response)
            print("DEBUG: AI parsing successful!")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            print(f"DEBUG: Raw AI response: {ai_response}")
            return None
            
    except Exception as e:
        print(f"DEBUG: OpenAI API error: {e}")
        return None

def format_ai_education(ai_education_list):
    """Formats the education array from AI parsing into a single string."""
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
    formatted_experience = []
    for exp in ai_experience_list:
        job_title = exp.get('job_title', 'N/A')
        company = exp.get('company', 'N/A')
        start_date = exp.get('start_date', 'N/A')
        end_date = exp.get('end_date', 'N/A')
        responsibilities = exp.get('responsibilities', [])
        
        if start_date == 'N/A' or end_date == 'N/A':
            formatted_experience.append(f"{job_title} at {company}")
        else:
            formatted_experience.append(f"{job_title} at {company} ({start_date}-{end_date})")
        
        if responsibilities:
            formatted_experience.append("Responsibilities: " + ", ".join(responsibilities))
    
    return ' | '.join(formatted_experience)

@hr_bp.route('/assign_candidate', methods=['POST'])
@hr_required
def assign_candidate():
    candidate_id = request.form['candidate_id']
    manager_email = request.form['manager_email']
    interview_time = request.form.get('interview_time')
    
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
        candidate.save()
        
        # Send email to manager
        try:
            email_sent = send_candidate_assignment_email(manager_email, candidate, interview_datetime)
            if not email_sent:
                print(f"❌ Failed to send candidate assignment email to {manager_email}")
                flash('Email notification failed - check email configuration', 'warning')
        except Exception as e:
            print(f"❌ Email sending error: {str(e)}")
            flash('Email notification failed', 'warning')
        
        # Log activity
        activity = ActivityLog(
            user_email=current_user.email,
            action='Assigned candidate',
            target_email=manager_email,
            details=f'Assigned candidate {candidate.first_name} {candidate.last_name} to {manager_email} for interview on {interview_datetime.strftime("%Y-%m-%d %H:%M") if interview_datetime else "TBD"}'
        )
        activity.save()
        
        return jsonify({'success': True, 'message': 'Candidate assigned successfully'})
    else:
        return jsonify({'success': False, 'message': 'Candidate not found'})

@hr_bp.route('/candidates')
@hr_required
def candidates():
    # Get all candidates in the system for HR visibility
    # HR users need to see the complete hiring pipeline
    from models_mongo import candidates_collection
    
    # Query for ALL candidates (HR users need full visibility)
    candidates_data = list(candidates_collection.find().sort('created_at', -1))
    
    # Convert to Candidate objects for proper data handling
    candidates = []
    for data in candidates_data:
        try:
            candidate = Candidate.from_dict(data)
            candidates.append(candidate)
        except Exception as e:
            print(f"Error converting candidate data: {e}")
            continue
    
    # Debug logging to check candidate counts by status
    status_counts = {}
    for candidate in candidates:
        status = candidate.status or 'Unknown'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"HR {current_user.email} candidates by status: {status_counts}")
    
    # Check if this is an AJAX request for dynamic updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the content for AJAX requests
        return render_template('hr/candidates_content.html', candidates=candidates)
    
    return render_template('hr/candidates.html', 
                         candidates=candidates)

@hr_bp.route('/candidate/<candidate_id>')
@hr_required
def candidate_details(candidate_id):
    candidate = Candidate.find_by_id(candidate_id)
    if candidate:
        return render_template('hr/candidate_details.html', candidate=candidate)
    else:
        flash('Candidate not found', 'error')
        return redirect(url_for('hr.dashboard'))

@hr_bp.route('/update_candidate_ratings/<candidate_id>', methods=['POST'])
@hr_required
def update_candidate_ratings(candidate_id):
    """Update candidate ratings with the new detailed rating system"""
    try:
        from models_mongo import candidates_collection, ActivityLog
        
        # Find the candidate
        candidate_data = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
        if not candidate_data:
            return jsonify({'success': False, 'message': 'Candidate not found'})
        
        # Verify the candidate belongs to the current HR user
        if candidate_data.get('assigned_by') != current_user.email:
            return jsonify({'success': False, 'message': 'You can only update candidates you created'})
        
        # Get new rating values from form
        communication_skills = request.form.get('communication_skills')
        adaptability = request.form.get('adaptability')
        teamwork_collaboration = request.form.get('teamwork_collaboration')
        job_fit = request.form.get('job_fit')
        overall_rating = request.form.get('overall_rating')
        other_notes = request.form.get('other_notes')
        
        # Convert ratings to appropriate types
        update_data = {}
        if communication_skills:
            update_data['communication_skills'] = int(communication_skills)
        if adaptability:
            update_data['adaptability'] = int(adaptability)
        if teamwork_collaboration:
            update_data['teamwork_collaboration'] = int(teamwork_collaboration)
        if job_fit:
            update_data['job_fit'] = int(job_fit)
        if overall_rating:
            update_data['overall_rating'] = float(overall_rating)
        if other_notes is not None:
            update_data['other_notes'] = other_notes
        
        # Add updated timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update the candidate
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # Log the rating update activity
            candidate_name = f"{candidate_data.get('first_name', '')} {candidate_data.get('last_name', '')}"
            activity = ActivityLog(
                user_email=current_user.email,
                action='Updated candidate ratings',
                target_email='',
                details=f'Updated ratings for candidate {candidate_name} (ID: {candidate_id})'
            )
            activity.save()
            
            return jsonify({
                'success': True, 
                'message': f'Ratings updated successfully for {candidate_name}'
            })
        else:
            return jsonify({'success': False, 'message': 'No changes made to ratings'})
            
    except Exception as e:
        print(f"Error updating candidate ratings: {str(e)}")
        return jsonify({'success': False, 'message': f'Error updating ratings: {str(e)}'})

@hr_bp.route('/bulk_move_candidates', methods=['POST'])
@hr_required
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
        
        # Get candidate details for logging
        candidates = list(candidates_collection.find({'_id': {'$in': object_ids}}))
        
        # Update candidates status
        result = candidates_collection.update_many(
            {'_id': {'$in': object_ids}},
            {'$set': {'status': new_status}}
        )
        
        if result.modified_count > 0:
            # Log the bulk move activity
            activity = ActivityLog(
                user_email=current_user.email,
                action=f'Bulk moved candidates to {new_status}',
                target_email='',
                details=f'HR moved {result.modified_count} candidates to {new_status}: {", ".join([c.get("first_name", "") + " " + c.get("last_name", "") for c in candidates])}'
            )
            activity.save()
            
            return jsonify({'success': True, 'message': f'Successfully moved {result.modified_count} candidates to {new_status}'})
        else:
            return jsonify({'success': False, 'message': 'No candidates found to update'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error moving candidates: {str(e)}'})

@hr_bp.route('/delete_candidate/<candidate_id>', methods=['POST'])
@hr_required
def delete_candidate(candidate_id):
    """Conditional delete candidate - only if not in advanced stages (Assigned, Shortlisted, Hired)"""
    try:
        from bson import ObjectId
        from models_mongo import candidates_collection, ActivityLog
        
        # Find the candidate
        candidate_data = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
        if not candidate_data:
            return jsonify({
                'status': 'error',
                'message': 'Candidate not found.'
            }), 404
        
        # Convert to Candidate object for proper validation
        candidate = Candidate.from_dict(candidate_data)
        
        # Check if candidate can be deleted (not in advanced stages)
        if not candidate.can_be_deleted():
            return jsonify({
                'status': 'error',
                'message': f'Candidate cannot be deleted while in "{candidate.status}" status. Only candidates with "New", "Pending", "Rejected", "On Hold", or "Reassigned" status can be deleted.'
            }), 403
        
        # Verify the candidate belongs to the current HR user
        if candidate.assigned_by != current_user.email:
            return jsonify({
                'status': 'error',
                'message': 'You can only delete candidates you created.'
            }), 403
        
        # Delete the candidate
        if candidate.delete():
            # Log the deletion activity
            activity = ActivityLog(
                user_email=current_user.email,
                action='Deleted candidate',
                target_email='',
                details=f'Deleted candidate {candidate.first_name} {candidate.last_name} (ID: {candidate.reference_id})'
            )
            activity.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Candidate {candidate.first_name} {candidate.last_name} deleted successfully.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete candidate.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error deleting candidate: {str(e)}'
        }), 500

@hr_bp.route('/analytics/<tab_name>')
@hr_required
def get_analytics_data(tab_name):
    """Get analytics data for HR dashboard"""
    try:
        from models_mongo import candidates_collection, users_collection
        
        # Get all candidates
        candidates = list(candidates_collection.find())
        
        # Process data based on tab
        if tab_name == 'overview':
            # Status distribution
            status_counts = {}
            for candidate in candidates:
                status = candidate.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Monthly data (last 6 months)
            from datetime import datetime, timedelta
            monthly_data = {}
            for i in range(6):
                month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
                month_name = month_start.strftime('%b')
                monthly_data[month_name] = len([c for c in candidates if 
                    c.get('created_at') and 
                    datetime.fromisoformat(str(c['created_at']).replace('Z', '+00:00')).month == month_start.month])
            
            return jsonify({
                'success': True,
                'status_counts': status_counts,
                'monthly_data': monthly_data,
                'total_candidates': len(candidates)
            })
            
        elif tab_name == 'trends':
            # Weekly trends - Calculate from real data
            from datetime import datetime, timedelta
            weekly_applications = []
            weekly_selections = []
            
            # Get last 4 weeks of data
            for i in range(4):
                week_start = datetime.now() - timedelta(weeks=i+1)
                week_end = datetime.now() - timedelta(weeks=i)
                
                # Count applications in this week
                week_applications = len([c for c in candidates if 
                    c.get('created_at') and 
                    week_start <= datetime.fromisoformat(str(c['created_at']).replace('Z', '+00:00')) < week_end])
                
                # Count selections in this week
                week_selections = len([c for c in candidates if 
                    c.get('status') == 'Selected' and
                    c.get('created_at') and 
                    week_start <= datetime.fromisoformat(str(c['created_at']).replace('Z', '+00:00')) < week_end])
                
                weekly_applications.insert(0, week_applications)
                weekly_selections.insert(0, week_selections)
            
            # Monthly success rates - Calculate from real data
            monthly_success = []
            for i in range(6):
                month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                
                month_candidates = [c for c in candidates if 
                    c.get('created_at') and 
                    month_start <= datetime.fromisoformat(str(c['created_at']).replace('Z', '+00:00')) < month_end]
                
                if month_candidates:
                    selected_count = len([c for c in month_candidates if c.get('status') == 'Selected'])
                    success_rate = round((selected_count / len(month_candidates)) * 100, 1)
                else:
                    success_rate = 0
                
                monthly_success.insert(0, success_rate)
            
            return jsonify({
                'success': True,
                'weekly_applications': weekly_applications,
                'weekly_selections': weekly_selections,
                'monthly_success': monthly_success
            })
            
        elif tab_name == 'performance':
            # HR team performance
            hr_users = list(users_collection.find({'role': 'hr'}))
            hr_performance = []
            
            for hr in hr_users:
                hr_email = hr.get('email')
                hr_candidates = [c for c in candidates if c.get('assigned_by') == hr_email]
                selected_candidates = [c for c in hr_candidates if c.get('status') == 'Selected']
                
                hr_performance.append({
                    'name': hr.get('name', 'Unknown'),
                    'candidates_added': len(hr_candidates),
                    'successful_placements': len(selected_candidates)
                })
            
            # Response time data (sample)
            response_times = [2.5, 1.8, 3.2, 2.1, 1.5]
            
            return jsonify({
                'success': True,
                'hr_performance': hr_performance,
                'response_times': response_times
            })
            
        elif tab_name == 'reports':
            # Department distribution (sample data)
            departments = {
                'Engineering': 35,
                'Marketing': 20,
                'Sales': 15,
                'HR': 10,
                'Operations': 20
            }
            
            # Experience level distribution
            experience_levels = [12, 25, 18, 15]  # 0-1, 1-3, 3-5, 5+ years
            
            return jsonify({
                'success': True,
                'departments': departments,
                'experience_levels': experience_levels
            })
            
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid tab name'
            }), 400
            
    except Exception as e:
        print(f"Error getting analytics data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting analytics data: {str(e)}'
        }), 500

@hr_bp.route('/onboarding')
@hr_required
def onboarding():
    """HR Onboarding Dashboard"""
    return render_template('hr/onboarding.html')

@hr_bp.route('/onboarding/candidates')
@hr_required
def get_onboarding_candidates():
    """Get candidates for onboarding (Selected by managers)"""
    try:
        from models_mongo import candidates_collection, users_collection
        
        # Get candidates with status 'Selected'
        selected_candidates = list(candidates_collection.find({'status': 'Selected'}))
        
        # Enrich with manager information
        for candidate in selected_candidates:
            if candidate.get('manager_email'):
                manager = users_collection.find_one({'email': candidate['manager_email']})
                if manager:
                    candidate['manager_name'] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}"
            
            # Convert ObjectId to string for JSON serialization
            candidate['_id'] = str(candidate['_id'])
        
        return jsonify({
            'success': True,
            'candidates': selected_candidates
        })
    except Exception as e:
        print(f"Error getting onboarding candidates: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load candidates'}), 500

@hr_bp.route('/onboarding/update', methods=['POST'])
@hr_required
def update_onboarding_status():
    """Update candidate onboarding status"""
    try:
        from models_mongo import candidates_collection
        
        data = request.get_json()
        candidate_id = data.get('candidate_id')
        status = data.get('status')
        onboarding_date = data.get('onboarding_date')
        notes = data.get('notes', '')
        
        if not candidate_id or not status:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Update candidate record
        update_data = {
            'onboarding_status': status,
            'onboarding_notes': notes,
            'onboarding_updated_by': current_user.email,
            'onboarding_updated_at': datetime.now().isoformat()
        }
        
        if onboarding_date:
            update_data['onboarding_date'] = onboarding_date
        
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # If candidate is onboarded and linked to a request, update request counts
            if status == 'Onboarded':
                try:
                    candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
                    print(f"DEBUG: Candidate {candidate_id} - linked_request_id: {candidate.get('linked_request_id') if candidate else 'None'}")
                    
                    if candidate and candidate.get('linked_request_id'):
                        from models_mongo import CandidateRequest
                        request_obj = CandidateRequest.find_by_id(candidate['linked_request_id'])
                        if request_obj:
                            # Increment onboarded count
                            new_onboarded_count = request_obj.onboarded_count + 1
                            request_obj.update_counts(onboarded_count=new_onboarded_count)
                            print(f"SUCCESS: Updated request {candidate['linked_request_id']}: onboarded_count = {new_onboarded_count}")
                        else:
                            print(f"ERROR: Request object not found for ID: {candidate['linked_request_id']}")
                    else:
                        print(f"WARNING: Candidate {candidate_id} has no linked_request_id")
                except Exception as e:
                    print(f"Error updating request counts during onboarding: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Log activity
            candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
            activity_log = ActivityLog(
                user_email=current_user.email,
                action=f'Updated onboarding status for {candidate.get("name", "")} to {status}'
            )
            activity_log.save()
            
            return jsonify({'success': True, 'message': 'Onboarding status updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'No changes made'}), 400
            
    except Exception as e:
        print(f"Error updating onboarding status: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update status'}), 500

@hr_bp.route('/managers')
@hr_required
def get_managers():
    """Get list of managers for filtering"""
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
        
        return jsonify({
            'success': True,
            'managers': manager_list
        })
    except Exception as e:
        print(f"Error getting managers: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load managers'}), 500

@hr_bp.route('/api/onboarding-stats')
@hr_required
def get_onboarding_stats():
    """Get onboarding statistics for HR dashboard"""
    try:
        from models_mongo import candidates_collection
        from datetime import datetime
        
        # Get candidates with status 'Selected' (ready for onboarding)
        selected_candidates = list(candidates_collection.find({'status': 'Selected'}))
        
        print(f"DEBUG: Found {len(selected_candidates)} selected candidates")
        
        # Calculate statistics
        pending = len([c for c in selected_candidates if c.get('onboarding_status') != 'Onboarded'])
        completed = len([c for c in selected_candidates if c.get('onboarding_status') == 'Onboarded'])
        
        # This month onboarding
        current_month = datetime.now().strftime('%Y-%m')
        this_month = len([c for c in selected_candidates 
                         if c.get('onboarding_date') and 
                         isinstance(c.get('onboarding_date'), str) and
                         c.get('onboarding_date').startswith(current_month)])
        
        # Success rate
        total = len(selected_candidates)
        success_rate = round((completed / total * 100), 2) if total > 0 else 0
        
        print(f"DEBUG: Stats calculated - Pending: {pending}, Completed: {completed}, This Month: {this_month}, Success Rate: {success_rate}%")
        
        return jsonify({
            'success': True,
            'stats': {
                'pending': pending,
                'completed': completed,
                'thisMonth': this_month,
                'successRate': success_rate
            }
        })
    except Exception as e:
        print(f"Error getting onboarding stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Failed to load stats: {str(e)}'}), 500

@hr_bp.route('/api/recent-activities')
@hr_required
def get_recent_activities():
    """Get recent onboarding activities"""
    try:
        from models_mongo import candidates_collection, activity_logs_collection
        
        # Get recent onboarding activities
        activities = list(activity_logs_collection.find({
            'action': {'$regex': 'onboarding', '$options': 'i'}
        }).sort('timestamp', -1).limit(10))
        
        print(f"DEBUG: Found {len(activities)} recent activities")
        
        activity_list = []
        for activity in activities:
            try:
                timestamp = activity.get('timestamp')
                if timestamp:
                    if isinstance(timestamp, str):
                        date_str = timestamp[:10]  # Take first 10 characters for YYYY-MM-DD
                    else:
                        date_str = timestamp.strftime('%Y-%m-%d')
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                
                activity_list.append({
                    'name': activity.get('user_email', 'Unknown'),
                    'action': activity.get('action', ''),
                    'date': date_str,
                    'status': 'Completed'  # Default status
                })
            except Exception as e:
                print(f"Error processing activity {activity.get('_id')}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'activities': activity_list
        })
    except Exception as e:
        print(f"Error getting recent activities: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'activities': []}), 500

@hr_bp.route('/logout')
@hr_required
def logout():
    """HR logout route - redirects to home page"""
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('index'))