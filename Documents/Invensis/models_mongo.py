from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
import uuid
import jwt
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

client = MongoClient(MONGODB_URI)
db = client['invensis']

# Collections
users_collection = db.users
roles_collection = db.roles
candidates_collection = db.candidates
activity_logs_collection = db.activity_logs
feedback_collection = db.feedback
user_emails_collection = db.user_emails
password_reset_tokens_collection = db.password_reset_tokens # Added for password reset tokens
candidate_requests_collection = db.candidate_requests # Added for candidate requests

class User(UserMixin):
    def __init__(self, email, name, role, password_hash=None, _id=None):
        self.email = email
        self.name = name
        self.role = role
        self.password_hash = password_hash
        self._id = _id
        self.created_at = datetime.utcnow()
        self._is_active = True

    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'is_active': self._is_active
        }

    @staticmethod
    def from_dict(data):
        user = User(
            email=data['email'],
            name=data['name'],
            role=data['role'],
            password_hash=data.get('password') or data.get('password_hash'),
            _id=str(data['_id'])
        )
        user.created_at = data.get('created_at', datetime.utcnow())
        user._is_active = data.get('isActive', data.get('is_active', True))
        return user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self._id)
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
    @property
    def is_authenticated(self):
        return True

    @staticmethod
    def find_by_email(email):
        data = users_collection.find_one({'email': email})
        if data:
            return User.from_dict(data)
        return None

    @staticmethod
    def find_by_id(user_id):
        try:
            data = users_collection.find_one({'_id': ObjectId(user_id)})
            if data:
                return User.from_dict(data)
        except:
            pass
        return None

    @staticmethod
    def find_by_role(role):
        data = users_collection.find_one({'role': role})
        if data:
            return User.from_dict(data)
        return None

    @staticmethod
    def count_by_role(role):
        """Count users by role"""
        return users_collection.count_documents({'role': role})

    @staticmethod
    def find_all_by_role(role):
        """Find all users by role"""
        data = users_collection.find({'role': role})
        users = []
        for user_data in data:
            users.append(User.from_dict(user_data))
        return users

    def save(self):
        if self._id:
            users_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': self.to_dict()}
            )
        else:
            result = users_collection.insert_one(self.to_dict())
            self._id = str(result.inserted_id)

class PasswordResetToken:
    def __init__(self, user_id, token, expires_at, _id=None):
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.is_used = False
        self._id = _id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at,
            'is_used': self.is_used,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        token_obj = PasswordResetToken(
            user_id=data['user_id'],
            token=data['token'],
            expires_at=data['expires_at'],
            _id=str(data['_id'])
        )
        token_obj.is_used = data.get('is_used', False)
        token_obj.created_at = data.get('created_at', datetime.utcnow())
        return token_obj

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def save(self):
        if self._id:
            password_reset_tokens_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': self.to_dict()}
            )
        else:
            result = password_reset_tokens_collection.insert_one(self.to_dict())
            self._id = str(result.inserted_id)

    @staticmethod
    def find_by_token(token):
        data = password_reset_tokens_collection.find_one({'token': token})
        if data:
            return PasswordResetToken.from_dict(data)
        return None

    @staticmethod
    def find_by_user_id(user_id):
        data = password_reset_tokens_collection.find_one({'user_id': user_id})
        if data:
            return PasswordResetToken.from_dict(data)
        return None

    @staticmethod
    def delete_expired_tokens():
        """Delete expired tokens to clean up the database"""
        password_reset_tokens_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })

class Role:
    def __init__(self, email, role_type, assigned_by=None, _id=None):
        self.email = email
        self.role_type = role_type
        self.assigned_by = assigned_by
        self._id = _id
        self.assigned_at = datetime.utcnow()
        self.is_active = True

    def to_dict(self):
        return {
            'email': self.email,
            'role_type': self.role_type,
            'assigned_by': self.assigned_by,
            'assigned_at': self.assigned_at,
            'is_active': self.is_active
        }

    @staticmethod
    def from_dict(data):
        role = Role(
            email=data['email'],
            role_type=data['role_type'],
            assigned_by=data.get('assigned_by'),
            _id=str(data['_id'])
        )
        role.assigned_at = data.get('assigned_at', datetime.utcnow())
        role.is_active = data.get('is_active', True)
        return role

    @staticmethod
    def find_by_email(email):
        data = roles_collection.find_one({'email': email})
        if data:
            return Role.from_dict(data)
        return None

    def save(self):
        if self._id:
            roles_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': self.to_dict()}
            )
        else:
            result = roles_collection.insert_one(self.to_dict())
            self._id = str(result.inserted_id)

class Candidate:
    def __init__(self, first_name, last_name, email, phone, gender, dob, education, experience, 
                 assigned_by, resume_path=None, image_path=None, _id=None,
                 skills=None, communication_skills=None, adaptability=None, teamwork_collaboration=None, 
                 job_fit=None, overall_rating=None, other_notes=None,
                 manager_communication_skills=None, manager_technical_skills=None, manager_problem_solving=None,
                 manager_cultural_fit=None, manager_overall_rating=None,
                 rejection_reasons=None, rejection_notes=None, onboarding_status=None, onboarding_date=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.gender = gender
        self.dob = dob
        self.education = education
        self.experience = experience
        self.assigned_by = assigned_by
        self.resume_path = resume_path
        self.image_path = image_path
        self._id = _id
        self.reference_id = self.generate_reference_id()
        self.status = 'Pending'
        self.assigned_to_manager = False
        self.manager_email = None
        self.assigned_manager_id = None  # New field for conditional delete
        self.manager_feedback = None
        self.reviewed_at = None
        self.scheduled_date = None
        self.skills = skills or []
        # Detailed rating fields
        self.communication_skills = communication_skills or 0
        self.adaptability = adaptability or 0
        self.teamwork_collaboration = teamwork_collaboration or 0
        self.job_fit = job_fit or 0
        self.overall_rating = overall_rating or 0
        self.other_notes = other_notes or ""
        
        # Manager rating fields
        self.manager_communication_skills = manager_communication_skills or 0
        self.manager_technical_skills = manager_technical_skills or 0
        self.manager_problem_solving = manager_problem_solving or 0
        self.manager_cultural_fit = manager_cultural_fit or 0
        self.manager_overall_rating = manager_overall_rating or 0
        
        # Rejection reasons fields
        self.rejection_reasons = rejection_reasons or []
        self.rejection_notes = rejection_notes or ""
        
        # Onboarding fields
        self.onboarding_status = onboarding_status or 'Not Onboarded'
        self.onboarding_date = onboarding_date
        
        # Request linking field
        self.linked_request_id = None
        
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def generate_reference_id(self):
        return f"REF-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'dob': self.dob,
            'education': self.education,
            'experience': self.experience,
            'assigned_by': self.assigned_by,
            'resume_path': self.resume_path,
            'image_path': self.image_path,
            'reference_id': self.reference_id,
            'status': self.status,
            'assigned_to_manager': self.assigned_to_manager,
            'manager_email': self.manager_email,
            'assigned_manager_id': self.assigned_manager_id,  # New field for conditional delete
            'manager_feedback': self.manager_feedback,
            'reviewed_at': self.reviewed_at,
            'scheduled_date': self.scheduled_date,
            'skills': self.skills,
            # Detailed rating fields
            'communication_skills': self.communication_skills,
            'adaptability': self.adaptability,
            'teamwork_collaboration': self.teamwork_collaboration,
            'job_fit': self.job_fit,
            'overall_rating': self.overall_rating,
            'other_notes': self.other_notes,
            
            # Manager rating fields
            'manager_communication_skills': self.manager_communication_skills,
            'manager_technical_skills': self.manager_technical_skills,
            'manager_problem_solving': self.manager_problem_solving,
            'manager_cultural_fit': self.manager_cultural_fit,
            'manager_overall_rating': self.manager_overall_rating,
            'rejection_reasons': self.rejection_reasons,
            'rejection_notes': self.rejection_notes,
            'onboarding_status': self.onboarding_status,
            'onboarding_date': self.onboarding_date,
            'linked_request_id': self.linked_request_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        # Handle both old and new schemas
        if 'first_name' in data and 'last_name' in data:
            # New schema
            first_name = data['first_name']
            last_name = data['last_name']
        elif 'name' in data:
            # Old schema - split name into first and last
            name_parts = data['name'].split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
        else:
            # Fallback
            first_name = data.get('first_name', 'Unknown')
            last_name = data.get('last_name', '')
        
        # Handle both old and new date fields
        dob = data.get('dob') or data.get('dateOfBirth') or data.get('age', 'Unknown')
        
        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=data['email'],
            phone=data.get('phone') or data.get('phoneNumber', ''),
            gender=data['gender'],
            dob=dob,
            education=data['education'],
            experience=data['experience'],
            assigned_by=data.get('assigned_by') or data.get('createdBy', 'Unknown'),
            resume_path=data.get('resume_path'),
            image_path=data.get('image_path'),
            _id=str(data['_id']),
            skills=data.get('skills', []),
            # Detailed rating fields
            communication_skills=data.get('communication_skills', 0),
            adaptability=data.get('adaptability', 0),
            teamwork_collaboration=data.get('teamwork_collaboration', 0),
            job_fit=data.get('job_fit', 0),
            overall_rating=data.get('overall_rating', 0),
            other_notes=data.get('other_notes', ""),
            
            # Manager rating fields
            manager_communication_skills=data.get('manager_communication_skills', 0),
            manager_technical_skills=data.get('manager_technical_skills', 0),
            manager_problem_solving=data.get('manager_problem_solving', 0),
            manager_cultural_fit=data.get('manager_cultural_fit', 0),
            manager_overall_rating=data.get('manager_overall_rating', 0),
            rejection_reasons=data.get('rejection_reasons', []),
            rejection_notes=data.get('rejection_notes', "")
        )
        candidate.reference_id = data.get('reference_id', candidate.reference_id)
        candidate.status = data.get('status', 'New')
        candidate.assigned_to_manager = data.get('assigned_to_manager', False)
        candidate.manager_email = data.get('manager_email')
        candidate.assigned_manager_id = data.get('assigned_manager_id')  # New field for conditional delete
        candidate.manager_feedback = data.get('manager_feedback')
        candidate.reviewed_at = data.get('reviewed_at')
        candidate.scheduled_date = data.get('scheduled_date')
        
        # Onboarding fields
        candidate.onboarding_status = data.get('onboarding_status', 'Not Onboarded')
        candidate.onboarding_date = data.get('onboarding_date')
        
        candidate.created_at = data.get('created_at', datetime.utcnow())
        candidate.updated_at = data.get('updated_at', datetime.utcnow())
        return candidate

    @staticmethod
    def find_by_id(candidate_id):
        try:
            data = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
            if data:
                return Candidate.from_dict(data)
        except:
            pass
        return None

    def save(self):
        """Save the candidate to the database"""
        from models_mongo import candidates_collection
        
        candidate_data = self.to_dict()
        if hasattr(self, '_id') and self._id:
            # Update existing candidate
            candidates_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': candidate_data}
            )
        else:
            # Insert new candidate
            result = candidates_collection.insert_one(candidate_data)
            self._id = str(result.inserted_id)
        
        return self
    
    def can_be_deleted(self):
        """Check if candidate can be deleted (not in advanced stages)"""
        # Candidates cannot be deleted if they are assigned, shortlisted, or hired
        return self.status not in ['Assigned', 'Shortlisted', 'Hired']
    
    def delete(self):
        """Delete the candidate from the database"""
        from models_mongo import candidates_collection
        
        if hasattr(self, '_id') and self._id:
            candidates_collection.delete_one({'_id': ObjectId(self._id)})
            return True
        return False
    
    @staticmethod
    def migrate_old_ratings():
        """Migrate old rating fields to new detailed rating system"""
        from models_mongo import candidates_collection
        
        # Find all candidates with old rating fields
        old_rating_candidates = candidates_collection.find({
            '$or': [
                {'hr_rating': {'$exists': True}},
                {'tech_rating': {'$exists': True}},
                {'hr_review': {'$exists': True}},
                {'tech_review': {'$exists': True}}
            ]
        })
        
        migrated_count = 0
        for candidate_data in old_rating_candidates:
            try:
                # Calculate overall rating from old fields
                hr_rating = candidate_data.get('hr_rating', 0)
                tech_rating = candidate_data.get('tech_rating', 0)
                
                # Convert old ratings to new system
                update_data = {
                    'communication_skills': hr_rating if hr_rating else 0,
                    'adaptability': hr_rating if hr_rating else 0,
                    'teamwork_collaboration': hr_rating if hr_rating else 0,
                    'job_fit': tech_rating if tech_rating else 0,
                    'overall_rating': round((hr_rating + tech_rating) / 2, 1) if hr_rating and tech_rating else 0,
                    'other_notes': candidate_data.get('hr_review', '') + ' ' + candidate_data.get('tech_review', ''),
                    'updated_at': datetime.utcnow()
                }
                
                # Remove old fields
                unset_data = {
                    'hr_rating': '',
                    'hr_review': '',
                    'tech_rating': '',
                    'tech_review': ''
                }
                
                # Update the candidate
                candidates_collection.update_one(
                    {'_id': candidate_data['_id']},
                    {
                        '$set': update_data,
                        '$unset': unset_data
                    }
                )
                
                migrated_count += 1
                print(f"Migrated candidate: {candidate_data.get('first_name', 'Unknown')} {candidate_data.get('last_name', '')}")
                
            except Exception as e:
                print(f"Error migrating candidate {candidate_data.get('_id')}: {e}")
                continue
        
        print(f"Migration completed. {migrated_count} candidates migrated.")
        return migrated_count

    @staticmethod
    def find_all():
        """Find all candidates in the database"""
        from models_mongo import candidates_collection
        
        candidates_data = list(candidates_collection.find())
        return [Candidate.from_dict(data) for data in candidates_data]

    @staticmethod
    def find_by_status_list(status_list):
        """Find candidates with any of the specified statuses"""
        from models_mongo import candidates_collection
        
        candidates_data = list(candidates_collection.find({'status': {'$in': status_list}}))
        return [Candidate.from_dict(data) for data in candidates_data]

    @staticmethod
    def find_by_status(status):
        """Find candidates with a specific status"""
        from models_mongo import candidates_collection
        
        candidates_data = list(candidates_collection.find({'status': status}))
        return [Candidate.from_dict(data) for data in candidates_data]

class ActivityLog:
    def __init__(self, user_email, action, target_email=None, details=None, _id=None):
        self.user_email = user_email
        self.action = action
        self.target_email = target_email
        self.details = details
        self._id = _id
        self.timestamp = datetime.utcnow()
        self.ip_address = None

    def to_dict(self):
        return {
            'user_email': self.user_email,
            'action': self.action,
            'target_email': self.target_email,
            'details': self.details,
            'timestamp': self.timestamp,
            'ip_address': self.ip_address
        }

    def save(self):
        if self._id:
            activity_logs_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': self.to_dict()}
            )
        else:
            result = activity_logs_collection.insert_one(self.to_dict())
            self._id = str(result.inserted_id)

class Feedback:
    def __init__(self, candidate_id, manager_email, feedback_text, status, 
                 overall_impression=None, communication_rating=None, technical_rating=None, 
                 problem_solving_rating=None, cultural_fit_rating=None, manager_rating=None,
                 rejection_reasons=None, rejection_notes=None, next_review_date=None,
                 timestamp=None, _id=None):
        self.candidate_id = candidate_id
        self.manager_email = manager_email
        self.feedback_text = feedback_text
        self.status = status
        self.overall_impression = overall_impression
        self.communication_rating = communication_rating
        self.technical_rating = technical_rating
        self.problem_solving_rating = problem_solving_rating
        self.cultural_fit_rating = cultural_fit_rating
        self.manager_rating = manager_rating
        self.rejection_reasons = rejection_reasons or []
        self.rejection_notes = rejection_notes or ""
        self.next_review_date = next_review_date
        self.timestamp = timestamp or datetime.utcnow()
        self._id = _id
        self.created_at = self.timestamp

    def to_dict(self):
        return {
            'candidate_id': self.candidate_id,
            'manager_email': self.manager_email,
            'feedback_text': self.feedback_text,
            'status': self.status,
            'overall_impression': self.overall_impression,
            'communication_rating': self.communication_rating,
            'technical_rating': self.technical_rating,
            'problem_solving_rating': self.problem_solving_rating,
            'cultural_fit_rating': self.cultural_fit_rating,
            'manager_rating': self.manager_rating,
            'rejection_reasons': self.rejection_reasons,
            'rejection_notes': self.rejection_notes,
            'next_review_date': self.next_review_date,
            'timestamp': self.timestamp,
            'created_at': self.created_at
        }

    def save(self):
        if self._id:
            feedback_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': self.to_dict()}
            )
        else:
            result = feedback_collection.insert_one(self.to_dict())
            self._id = str(result.inserted_id)

    @staticmethod
    def find_all():
        """Find all feedback records in the database"""
        from models_mongo import feedback_collection
        
        feedback_data = list(feedback_collection.find())
        return [Feedback.from_dict(data) for data in feedback_data]

    @staticmethod
    def from_dict(data):
        """Create a Feedback object from dictionary data"""
        feedback = Feedback(
            candidate_id=data['candidate_id'],
            manager_email=data['manager_email'],
            feedback_text=data['feedback_text'],
            status=data['status'],
            overall_impression=data.get('overall_impression'),
            communication_rating=data.get('communication_rating'),
            technical_rating=data.get('technical_rating'),
            problem_solving_rating=data.get('problem_solving_rating'),
            cultural_fit_rating=data.get('cultural_fit_rating'),
            manager_rating=data.get('manager_rating'),
            rejection_reasons=data.get('rejection_reasons'),
            rejection_notes=data.get('rejection_notes'),
            next_review_date=data.get('next_review_date'),
            timestamp=data.get('timestamp'),
            _id=str(data['_id']) if data.get('_id') else None
        )
        feedback.created_at = data.get('created_at', feedback.timestamp)
        return feedback

    def delete(self):
        """Delete the feedback record from the database"""
        if self._id:
            feedback_collection.delete_one({'_id': ObjectId(self._id)})
            return True
        return False

class CandidateRequest:
    def __init__(self, manager_email, position_title, quantity_needed, urgency_level, 
                 required_skills="", additional_notes="", status="Active"):
        self.manager_email = manager_email
        self.position_title = position_title
        self.quantity_needed = int(quantity_needed)
        self.urgency_level = urgency_level
        self.required_skills = required_skills
        self.additional_notes = additional_notes
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.assigned_count = 0
        self.onboarded_count = 0
        self.remaining_count = int(quantity_needed)
        self._id = None

    @property
    def remaining_count(self):
        return self.quantity_needed - self.assigned_count

    @remaining_count.setter
    def remaining_count(self, value):
        self._remaining_count = value

    def save(self):
        try:
            from models_mongo import candidate_requests_collection
            if self._id:
                # Update existing
                result = candidate_requests_collection.update_one(
                    {'_id': ObjectId(self._id)},
                    {'$set': {
                        'manager_email': self.manager_email,
                        'position_title': self.position_title,
                        'quantity_needed': self.quantity_needed,
                        'urgency_level': self.urgency_level,
                        'required_skills': self.required_skills,
                        'additional_notes': self.additional_notes,
                        'status': self.status,
                        'assigned_count': self.assigned_count,
                        'onboarded_count': self.onboarded_count,
                        'updated_at': datetime.now().isoformat()
                    }}
                )
                return result.modified_count > 0
            else:
                # Create new
                data = {
                    'manager_email': self.manager_email,
                    'position_title': self.position_title,
                    'quantity_needed': self.quantity_needed,
                    'urgency_level': self.urgency_level,
                    'required_skills': self.required_skills,
                    'additional_notes': self.additional_notes,
                    'status': self.status,
                    'assigned_count': self.assigned_count,
                    'onboarded_count': self.onboarded_count,
                    'created_at': self.created_at,
                    'updated_at': self.updated_at
                }
                result = candidate_requests_collection.insert_one(data)
                if result.inserted_id:
                    self._id = str(result.inserted_id)
                    return True
                return False
        except Exception as e:
            print(f"Error saving candidate request: {str(e)}")
            return False

    @classmethod
    def find_by_manager(cls, manager_email):
        try:
            from models_mongo import candidate_requests_collection
            requests = list(candidate_requests_collection.find({'manager_email': manager_email}).sort('created_at', -1))
            return [cls._from_dict(req) for req in requests]
        except Exception as e:
            print(f"Error finding requests by manager: {str(e)}")
            return []

    @classmethod
    def find_all_active(cls):
        try:
            from models_mongo import candidate_requests_collection
            requests = list(candidate_requests_collection.find({'status': 'Active'}).sort('created_at', -1))
            return [cls._from_dict(req) for req in requests]
        except Exception as e:
            print(f"Error finding all active requests: {str(e)}")
            return []

    @classmethod
    def find_by_id(cls, request_id):
        try:
            from models_mongo import candidate_requests_collection
            request_data = candidate_requests_collection.find_one({'_id': ObjectId(request_id)})
            if request_data:
                return cls._from_dict(request_data)
            return None
        except Exception as e:
            print(f"Error finding request by ID: {str(e)}")
            return None

    @classmethod
    def _from_dict(cls, data):
        request = cls(
            manager_email=data['manager_email'],
            position_title=data['position_title'],
            quantity_needed=data['quantity_needed'],
            urgency_level=data['urgency_level'],
            required_skills=data.get('required_skills', ''),
            additional_notes=data.get('additional_notes', ''),
            status=data.get('status', 'Active')
        )
        request._id = str(data['_id'])
        request.created_at = data.get('created_at', datetime.now().isoformat())
        request.updated_at = data.get('updated_at', datetime.now().isoformat())
        request.assigned_count = data.get('assigned_count', 0)
        request.onboarded_count = data.get('onboarded_count', 0)
        return request

    def update_counts(self, assigned_count=None, onboarded_count=None):
        if assigned_count is not None:
            self.assigned_count = assigned_count
        if onboarded_count is not None:
            self.onboarded_count = onboarded_count
        self.updated_at = datetime.now().isoformat()
        return self.save()

# JWT Token functions
def create_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

class UserEmail:
    def __init__(self, email, role, assigned_by=None, _id=None):
        self.email = email
        self.role = role
        self.assigned_by = assigned_by
        self._id = _id
        self.created_at = datetime.utcnow()
        self.is_active = True

    def to_dict(self):
        return {
            'email': self.email,
            'role': self.role,
            'assigned_by': self.assigned_by,
            'created_at': self.created_at,
            'is_active': self.is_active
        }

    @staticmethod
    def from_dict(data):
        user_email = UserEmail(
            email=data['email'],
            role=data['role'],
            assigned_by=data.get('assigned_by'),
            _id=str(data['_id']) if data.get('_id') else None
        )
        user_email.created_at = data.get('created_at', datetime.utcnow())
        user_email.is_active = data.get('is_active', True)
        return user_email

    def save(self):
        if self._id:
            user_emails_collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': self.to_dict()}
            )
        else:
            result = user_emails_collection.insert_one(self.to_dict())
            self._id = str(result.inserted_id)

    def delete(self):
        if self._id:
            user_emails_collection.delete_one({'_id': ObjectId(self._id)})
            return True
        return False

    @staticmethod
    def find_by_email(email):
        data = user_emails_collection.find_one({'email': email})
        if data:
            return UserEmail.from_dict(data)
        return None

    @staticmethod
    def find_by_role(role):
        data = list(user_emails_collection.find({'role': role, 'is_active': True}))
        return [UserEmail.from_dict(item) for item in data]

    @staticmethod
    def find_all():
        data = list(user_emails_collection.find({'is_active': True}))
        return [UserEmail.from_dict(item) for item in data] 