"""Additional comprehensive tests for models_mongo.py methods"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId
from models_mongo import Candidate, Feedback, ActivityLog


def test_candidate_from_dict():
    """Test Candidate.from_dict()"""
    data = {
        '_id': ObjectId(),
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'gender': 'Male',
        'dob': datetime(1990, 1, 1),
        'education': 'B.Tech',
        'experience': '5 years',
        'assigned_by': 'hr@example.com',
        'status': 'pending',
        'reference_id': 'REF-20240101-ABCD1234'
    }
    candidate = Candidate.from_dict(data)
    assert candidate.first_name == 'John'
    assert candidate.last_name == 'Doe'
    assert candidate.email == 'john@example.com'
    assert candidate.status == 'pending'
    assert candidate.reference_id == 'REF-20240101-ABCD1234'


def test_candidate_name_property():
    """Test Candidate.name property"""
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        gender="Male",
        dob=datetime(1990, 1, 1),
        education="B.Tech",
        experience="5 years",
        assigned_by="hr@example.com"
    )
    assert candidate.name == "John Doe"


def test_candidate_full_name_property():
    """Test Candidate.full_name property"""
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        gender="Male",
        dob=datetime(1990, 1, 1),
        education="B.Tech",
        experience="5 years",
        assigned_by="hr@example.com"
    )
    assert candidate.full_name == "John Doe"


def test_candidate_update_status():
    """Test Candidate.update_status()"""
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        gender="Male",
        dob=datetime(1990, 1, 1),
        education="B.Tech",
        experience="5 years",
        assigned_to="manager@example.com",
        assigned_by="hr@example.com"
    )
    with patch.object(candidate, 'save') as mock_save:
        candidate.update_status("shortlisted")
        assert candidate.status == "shortlisted"
        mock_save.assert_called_once()


def test_candidate_update_feedback():
    """Test Candidate.update_feedback()"""
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        gender="Male",
        dob=datetime(1990, 1, 1),
        education="B.Tech",
        experience="5 years",
        assigned_by="hr@example.com"
    )
    with patch.object(candidate, 'save') as mock_save:
        candidate.update_feedback("Great candidate", "shortlisted")
        assert candidate.feedback == "Great candidate"
        assert candidate.status == "shortlisted"
        mock_save.assert_called_once()


def test_feedback_from_dict():
    """Test Feedback.from_dict()"""
    data = {
        '_id': ObjectId(),
        'candidate_id': 'candidate123',
        'manager_email': 'manager@example.com',
        'feedback_text': 'Good candidate',
        'status': 'shortlisted',
        'created_at': datetime.utcnow()
    }
    feedback = Feedback.from_dict(data)
    assert feedback.candidate_id == 'candidate123'
    assert feedback.manager_email == 'manager@example.com'
    assert feedback.feedback_text == 'Good candidate'
    assert feedback.status == 'shortlisted'


def test_activity_log_from_dict():
    """Test ActivityLog.from_dict()"""
    data = {
        '_id': ObjectId(),
        'user_email': 'user@example.com',
        'action': 'login',
        'target_email': 'admin@example.com',
        'details': 'User logged in',
        'timestamp': datetime.utcnow()
    }
    log = ActivityLog.from_dict(data)
    assert log.user_email == 'user@example.com'
    assert log.action == 'login'
    assert log.target_email == 'admin@example.com'
    assert log.details == 'User logged in'


def test_candidate_save_new():
    """Test Candidate.save() for new candidate"""
    from models_mongo import candidates_collection
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        gender="Male",
        dob=datetime(1990, 1, 1),
        education="B.Tech",
        experience="5 years",
        assigned_by="hr@example.com"
    )
    with patch.object(candidates_collection, 'insert_one') as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        candidate.save()
        assert candidate._id is not None
        mock_insert.assert_called_once()


def test_candidate_save_existing():
    """Test Candidate.save() for existing candidate"""
    from models_mongo import candidates_collection
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        gender="Male",
        dob=datetime(1990, 1, 1),
        education="B.Tech",
        experience="5 years",
        assigned_by="hr@example.com",
        _id=str(ObjectId())
    )
    with patch.object(candidates_collection, 'update_one') as mock_update:
        candidate.save()
        mock_update.assert_called_once()


def test_role_save_new():
    """Test Role.save() for new role"""
    from models_mongo import roles_collection
    role = Role("test@example.com", "manager")
    with patch.object(roles_collection, 'insert_one') as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        role.save()
        assert role._id is not None
        mock_insert.assert_called_once()


def test_role_save_existing():
    """Test Role.save() for existing role"""
    from models_mongo import roles_collection
    role = Role("test@example.com", "manager", _id=str(ObjectId()))
    with patch.object(roles_collection, 'update_one') as mock_update:
        role.save()
        mock_update.assert_called_once()


def test_user_save_new():
    """Test User.save() for new user"""
    from models_mongo import users_collection
    user = User("test@example.com", "Test User", "admin")
    with patch.object(users_collection, 'insert_one') as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        user.save()
        assert user._id is not None
        mock_insert.assert_called_once()


def test_user_save_existing():
    """Test User.save() for existing user"""
    from models_mongo import users_collection
    user = User("test@example.com", "Test User", "admin", _id=str(ObjectId()))
    with patch.object(users_collection, 'update_one') as mock_update:
        user.save()
        mock_update.assert_called_once()


def test_password_reset_token_save_new():
    """Test PasswordResetToken.save() for new token"""
    from models_mongo import password_reset_tokens_collection
    token = PasswordResetToken("user123", "token123", datetime.utcnow() + timedelta(hours=1))
    with patch.object(password_reset_tokens_collection, 'insert_one') as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        token.save()
        assert token._id is not None
        mock_insert.assert_called_once()


def test_password_reset_token_save_existing():
    """Test PasswordResetToken.save() for existing token"""
    from models_mongo import password_reset_tokens_collection
    token = PasswordResetToken("user123", "token123", datetime.utcnow() + timedelta(hours=1), _id=str(ObjectId()))
    with patch.object(password_reset_tokens_collection, 'update_one') as mock_update:
        token.save()
        mock_update.assert_called_once()


def test_activity_log_save_new():
    """Test ActivityLog.save() for new log"""
    from models_mongo import activity_logs_collection
    log = ActivityLog("user@example.com", "login")
    with patch.object(activity_logs_collection, 'insert_one') as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        log.save()
        assert log._id is not None
        mock_insert.assert_called_once()


def test_activity_log_save_existing():
    """Test ActivityLog.save() for existing log"""
    from models_mongo import activity_logs_collection
    log = ActivityLog("user@example.com", "login", _id=str(ObjectId()))
    with patch.object(activity_logs_collection, 'update_one') as mock_update:
        log.save()
        mock_update.assert_called_once()


def test_feedback_save_new():
    """Test Feedback.save() for new feedback"""
    from models_mongo import feedback_collection
    feedback = Feedback("candidate123", "manager@example.com", "Good candidate", "shortlisted")
    with patch.object(feedback_collection, 'insert_one') as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        feedback.save()
        assert feedback._id is not None
        mock_insert.assert_called_once()


def test_feedback_save_existing():
    """Test Feedback.save() for existing feedback"""
    from models_mongo import feedback_collection
    feedback = Feedback("candidate123", "manager@example.com", "Good candidate", "shortlisted", _id=str(ObjectId()))
    with patch.object(feedback_collection, 'update_one') as mock_update:
        feedback.save()
        mock_update.assert_called_once()


def test_feedback_find_all():
    """Test Feedback.find_all()"""
    from models_mongo import feedback_collection
    with patch.object(feedback_collection, 'find') as mock_find:
        mock_find.return_value = [
            {
                '_id': ObjectId(),
                'candidate_id': 'candidate123',
                'manager_email': 'manager@example.com',
                'feedback_text': 'Good',
                'status': 'shortlisted',
                'timestamp': datetime.utcnow()
            }
        ]
        feedbacks = Feedback.find_all()
        assert len(feedbacks) == 1
        assert feedbacks[0].candidate_id == 'candidate123'


def test_candidate_find_by_status():
    """Test Candidate.find_by_status()"""
    from models_mongo import candidates_collection
    with patch.object(candidates_collection, 'find') as mock_find:
        mock_find.return_value = [
            {
                '_id': ObjectId(),
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'phone': '1234567890',
                'gender': 'Male',
                'dob': datetime(1990, 1, 1),
                'education': 'B.Tech',
                'experience': '5 years',
                'assigned_by': 'hr@example.com',
                'status': 'pending'
            }
        ]
        candidates = Candidate.find_by_status('pending')
        assert len(candidates) == 1
        assert candidates[0].first_name == 'John'


def test_candidate_find_by_status_list():
    """Test Candidate.find_by_status_list()"""
    from models_mongo import candidates_collection
    with patch.object(candidates_collection, 'find') as mock_find:
        mock_find.return_value = [
            {
                '_id': ObjectId(),
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'phone': '1234567890',
                'gender': 'Male',
                'dob': datetime(1990, 1, 1),
                'education': 'B.Tech',
                'experience': '5 years',
                'assigned_by': 'hr@example.com',
                'status': 'pending'
            }
        ]
        candidates = Candidate.find_by_status_list(['pending', 'shortlisted'])
        assert len(candidates) == 1
        assert candidates[0].status == 'pending'


def test_candidate_find_all():
    """Test Candidate.find_all()"""
    from models_mongo import candidates_collection
    with patch.object(candidates_collection, 'find') as mock_find:
        mock_find.return_value = [
            {
                '_id': ObjectId(),
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'phone': '1234567890',
                'gender': 'Male',
                'dob': datetime(1990, 1, 1),
                'education': 'B.Tech',
                'experience': '5 years',
                'assigned_by': 'hr@example.com',
                'status': 'pending'
            }
        ]
        candidates = Candidate.find_all()
        assert len(candidates) == 1
        assert candidates[0].first_name == 'John'


def test_user_find_by_role():
    """Test User.find_by_role()"""
    from models_mongo import users_collection
    with patch.object(users_collection, 'find_one') as mock_find:
        mock_find.return_value = {
            '_id': ObjectId(),
            'email': 'test@example.com',
            'name': 'Test User',
            'role': 'admin',
            'password_hash': 'hashed'
        }
        user = User.find_by_role('admin')
        assert user is not None
        assert user.role == 'admin'


def test_user_find_all_by_role():
    """Test User.find_all_by_role()"""
    from models_mongo import users_collection
    with patch.object(users_collection, 'find') as mock_find:
        mock_find.return_value = [
            {
                '_id': ObjectId(),
                'email': 'test@example.com',
                'name': 'Test User',
                'role': 'admin',
                'password_hash': 'hashed'
            }
        ]
        users = User.find_all_by_role('admin')
        assert len(users) == 1
        assert users[0].role == 'admin'


def test_user_count_by_role():
    """Test User.count_by_role()"""
    from models_mongo import users_collection
    with patch.object(users_collection, 'count_documents', return_value=5) as mock_count:
        count = User.count_by_role('admin')
        assert count == 5
        mock_count.assert_called_once_with({'role': 'admin'})


def test_feedback_from_dict():
    """Test Feedback.from_dict()"""
    data = {
        '_id': ObjectId(),
        'candidate_id': 'candidate123',
        'manager_email': 'manager@example.com',
        'feedback_text': 'Good candidate',
        'status': 'shortlisted',
        'overall_impression': 'Positive',
        'communication_rating': 4,
        'technical_rating': 5,
        'problem_solving_rating': 4,
        'cultural_fit_rating': 5,
        'manager_rating': 4.5,
        'rejection_reasons': [],
        'rejection_notes': '',
        'next_review_date': None,
        'timestamp': datetime.utcnow(),
        'created_at': datetime.utcnow()
    }
    feedback = Feedback.from_dict(data)
    assert feedback.candidate_id == 'candidate123'
    assert feedback.manager_email == 'manager@example.com'
    assert feedback.communication_rating == 4
    assert feedback.technical_rating == 5


def test_feedback_delete():
    """Test Feedback.delete()"""
    from models_mongo import feedback_collection
    feedback = Feedback("candidate123", "manager@example.com", "Good candidate", "shortlisted", _id=str(ObjectId()))
    with patch.object(feedback_collection, 'delete_one') as mock_delete:
        result = feedback.delete()
        assert result is True
        mock_delete.assert_called_once()


def test_feedback_delete_no_id():
    """Test Feedback.delete() without _id"""
    feedback = Feedback("candidate123", "manager@example.com", "Good candidate", "shortlisted")
    feedback._id = None
    result = feedback.delete()
    assert result is False


def test_candidate_request_init():
    """Test CandidateRequest initialization"""
    from models_mongo import CandidateRequest
    request_obj = CandidateRequest(
        manager_email="manager@example.com",
        position_title="Software Engineer",
        quantity_needed=5,
        urgency_level="High"
    )
    assert request_obj.manager_email == "manager@example.com"
    assert request_obj.position_title == "Software Engineer"
    assert request_obj.quantity_needed == 5
    assert request_obj.urgency_level == "High"
    assert request_obj.status == "Active"


def test_candidate_request_remaining_count_property():
    """Test CandidateRequest remaining_count property"""
    from models_mongo import CandidateRequest
    request_obj = CandidateRequest(
        manager_email="manager@example.com",
        position_title="Software Engineer",
        quantity_needed=5,
        urgency_level="High"
    )
    request_obj.onboarded_count = 2
    assert request_obj.remaining_count == 3

