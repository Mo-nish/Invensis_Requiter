"""Comprehensive tests for models_mongo.py to increase coverage"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId
from models_mongo import (
    User, Role, Candidate, ActivityLog, Feedback, 
    PasswordResetToken, UserEmail, create_token, verify_token,
    get_database
)


def test_user_init():
    """Test User initialization"""
    user = User("test@example.com", "Test User", "admin")
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "admin"
    assert user.is_active is True
    assert user._is_active is True


def test_user_init_with_password_hash():
    """Test User initialization with password hash"""
    user = User("test@example.com", "Test User", "admin", password_hash="hashed")
    assert user.password_hash == "hashed"


def test_user_init_with_id():
    """Test User initialization with _id"""
    user_id = str(ObjectId())
    user = User("test@example.com", "Test User", "admin", _id=user_id)
    assert user._id == user_id


def test_user_to_dict():
    """Test User.to_dict()"""
    user = User("test@example.com", "Test User", "admin")
    data = user.to_dict()
    assert data['email'] == "test@example.com"
    assert data['name'] == "Test User"
    assert data['role'] == "admin"
    assert 'created_at' in data
    assert data['is_active'] is True


def test_user_from_dict():
    """Test User.from_dict()"""
    data = {
        '_id': ObjectId(),
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'admin',
        'password_hash': 'hashed'
    }
    user = User.from_dict(data)
    assert user.email == 'test@example.com'
    assert user.name == 'Test User'
    assert user.role == 'admin'
    assert user.password_hash == 'hashed'


def test_user_from_dict_with_password_field():
    """Test User.from_dict() with password field instead of password_hash"""
    data = {
        '_id': ObjectId(),
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'admin',
        'password': 'hashed'
    }
    user = User.from_dict(data)
    assert user.password_hash == 'hashed'


def test_user_set_password():
    """Test User.set_password()"""
    user = User("test@example.com", "Test User", "admin")
    user.set_password("newpassword123")
    assert user.password_hash is not None
    assert user.password_hash != "newpassword123"  # Should be hashed


def test_user_check_password():
    """Test User.check_password()"""
    user = User("test@example.com", "Test User", "admin")
    user.set_password("testpass123")
    assert user.check_password("testpass123") is True
    assert user.check_password("wrongpass") is False


def test_user_check_password_no_hash():
    """Test User.check_password() when no password hash exists"""
    user = User("test@example.com", "Test User", "admin")
    user.password_hash = None
    assert user.check_password("anything") is False


def test_user_get_id():
    """Test User.get_id()"""
    user_id = str(ObjectId())
    user = User("test@example.com", "Test User", "admin", _id=user_id)
    assert user.get_id() == user_id


def test_user_is_active_property():
    """Test User is_active property"""
    user = User("test@example.com", "Test User", "admin")
    assert user.is_active is True
    user.is_active = False
    assert user.is_active is False
    assert user._is_active is False


def test_user_is_authenticated():
    """Test User is_authenticated property"""
    user = User("test@example.com", "Test User", "admin")
    assert user.is_authenticated is True


def test_password_reset_token_init():
    """Test PasswordResetToken initialization"""
    token = PasswordResetToken("user123", "token123", datetime.utcnow() + timedelta(hours=1))
    assert token.user_id == "user123"
    assert token.token == "token123"
    assert token.is_used is False


def test_password_reset_token_is_expired():
    """Test PasswordResetToken.is_expired()"""
    expired_token = PasswordResetToken("user123", "token123", datetime.utcnow() - timedelta(hours=1))
    assert expired_token.is_expired() is True
    
    valid_token = PasswordResetToken("user123", "token123", datetime.utcnow() + timedelta(hours=1))
    assert valid_token.is_expired() is False


def test_password_reset_token_to_dict():
    """Test PasswordResetToken.to_dict()"""
    token = PasswordResetToken("user123", "token123", datetime.utcnow() + timedelta(hours=1))
    data = token.to_dict()
    assert data['user_id'] == "user123"
    assert data['token'] == "token123"
    assert data['is_used'] is False
    assert 'expires_at' in data


def test_password_reset_token_from_dict():
    """Test PasswordResetToken.from_dict()"""
    data = {
        '_id': ObjectId(),
        'user_id': 'user123',
        'token': 'token123',
        'expires_at': datetime.utcnow() + timedelta(hours=1),
        'is_used': False
    }
    token = PasswordResetToken.from_dict(data)
    assert token.user_id == 'user123'
    assert token.token == 'token123'
    assert token.is_used is False


def test_password_reset_token_mark_as_used():
    """Test PasswordResetToken.mark_as_used()"""
    token = PasswordResetToken("user123", "token123", datetime.utcnow() + timedelta(hours=1))
    with patch.object(token, 'save') as mock_save:
        token.mark_as_used()
        assert token.is_used is True
        mock_save.assert_called_once()


def test_role_init():
    """Test Role initialization"""
    role = Role("test@example.com", "manager")
    assert role.email == "test@example.com"
    assert role.role_type == "manager"
    assert role.is_active is True


def test_role_init_with_assigned_by():
    """Test Role initialization with assigned_by"""
    role = Role("test@example.com", "manager", assigned_by="admin@example.com")
    assert role.assigned_by == "admin@example.com"


def test_role_to_dict():
    """Test Role.to_dict()"""
    role = Role("test@example.com", "manager")
    data = role.to_dict()
    assert data['email'] == "test@example.com"
    assert data['role_type'] == "manager"
    assert data['is_active'] is True
    assert 'assigned_at' in data


def test_role_from_dict():
    """Test Role.from_dict()"""
    data = {
        '_id': ObjectId(),
        'email': 'test@example.com',
        'role_type': 'manager',
        'assigned_by': 'admin@example.com',
        'assigned_at': datetime.utcnow(),
        'is_active': True
    }
    role = Role.from_dict(data)
    assert role.email == 'test@example.com'
    assert role.role_type == 'manager'
    assert role.assigned_by == 'admin@example.com'


def test_activity_log_init():
    """Test ActivityLog initialization"""
    log = ActivityLog("user@example.com", "login")
    assert log.user_email == "user@example.com"
    assert log.action == "login"


def test_activity_log_init_with_details():
    """Test ActivityLog initialization with details"""
    log = ActivityLog("user@example.com", "login", target_email="admin@example.com", details="User logged in")
    assert log.target_email == "admin@example.com"
    assert log.details == "User logged in"


def test_activity_log_to_dict():
    """Test ActivityLog.to_dict()"""
    log = ActivityLog("user@example.com", "login", details="Test")
    data = log.to_dict()
    assert data['user_email'] == "user@example.com"
    assert data['action'] == "login"
    assert data['details'] == "Test"
    assert 'timestamp' in data


def test_feedback_init():
    """Test Feedback initialization"""
    feedback = Feedback("candidate123", "manager@example.com", "Good candidate", "shortlisted")
    assert feedback.candidate_id == "candidate123"
    assert feedback.manager_email == "manager@example.com"
    assert feedback.feedback_text == "Good candidate"
    assert feedback.status == "shortlisted"


def test_feedback_to_dict():
    """Test Feedback.to_dict()"""
    feedback = Feedback("candidate123", "manager@example.com", "Good candidate", "shortlisted")
    data = feedback.to_dict()
    assert data['candidate_id'] == "candidate123"
    assert data['manager_email'] == "manager@example.com"
    assert data['feedback_text'] == "Good candidate"
    assert data['status'] == "shortlisted"
    assert 'created_at' in data


def test_candidate_init():
    """Test Candidate initialization"""
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
    assert candidate.first_name == "John"
    assert candidate.last_name == "Doe"
    assert candidate.email == "john@example.com"
    assert candidate.status == "pending"


def test_candidate_generate_reference_id():
    """Test Candidate.generate_reference_id()"""
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
    ref_id = candidate.generate_reference_id()
    assert ref_id.startswith("REF-")
    assert len(ref_id) > 10


def test_candidate_to_dict():
    """Test Candidate.to_dict()"""
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
    data = candidate.to_dict()
    assert data['first_name'] == "John"
    assert data['last_name'] == "Doe"
    assert data['email'] == "john@example.com"
    assert data['status'] == "pending"
    assert 'reference_id' in data


def test_create_token():
    """Test create_token()"""
    token = create_token("test@example.com")
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token():
    """Test verify_token()"""
    email = "test@example.com"
    token = create_token(email)
    result = verify_token(token)
    assert result == email


def test_verify_token_invalid():
    """Test verify_token() with invalid token"""
    result = verify_token("invalid_token")
    assert result is None


def test_get_database():
    """Test get_database()"""
    db = get_database()
    assert db is not None
    assert db.name == "invensis"


def test_user_email_init():
    """Test UserEmail initialization"""
    user_email = UserEmail("test@example.com")
    assert user_email.email == "test@example.com"
    assert user_email.is_verified is False


def test_user_email_to_dict():
    """Test UserEmail.to_dict()"""
    user_email = UserEmail("test@example.com")
    data = user_email.to_dict()
    assert data['email'] == "test@example.com"
    assert data['is_verified'] is False
    assert 'created_at' in data

