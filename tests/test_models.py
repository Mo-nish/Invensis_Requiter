"""Comprehensive tests for models module"""
from datetime import datetime
import uuid
from models import Candidate, User, Role, ActivityLog, Feedback


def test_candidate_generate_reference_id():
    """Test candidate reference ID generation"""
    candidate = Candidate(
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        gender="Male",
        age=25,
        education="B.Tech",
        experience="2 years",
        assigned_by="admin@example.com"
    )
    ref_id = candidate.generate_reference_id()
    assert ref_id.startswith("REF-")
    assert len(ref_id) > 10
    assert datetime.now().strftime('%Y%m%d') in ref_id


def test_candidate_init_with_reference_id():
    """Test candidate initialization with existing reference ID"""
    existing_ref = "REF-20240101-ABCD1234"
    candidate = Candidate(
        reference_id=existing_ref,
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        gender="Male",
        age=25,
        education="B.Tech",
        experience="2 years",
        assigned_by="admin@example.com"
    )
    assert candidate.reference_id == existing_ref


def test_candidate_init_without_reference_id():
    """Test candidate initialization without reference ID (should auto-generate)"""
    candidate = Candidate(
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        gender="Male",
        age=25,
        education="B.Tech",
        experience="2 years",
        assigned_by="admin@example.com"
    )
    assert candidate.reference_id is not None
    assert candidate.reference_id.startswith("REF-")


def test_user_check_password_hash():
    """Test user password hash checking"""
    from werkzeug.security import generate_password_hash, check_password_hash
    
    password = "testpassword123"
    password_hash = generate_password_hash(password)
    
    user = User(
        email="test@example.com",
        name="Test User",
        role="admin",
        password_hash=password_hash
    )
    
    assert user.check_password_hash(password) is True
    assert user.check_password_hash("wrongpassword") is False


def test_user_model_fields():
    """Test User model has all required fields"""
    user = User(
        email="test@example.com",
        name="Test User",
        role="admin",
        password_hash="hashed_password"
    )
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "admin"
    assert user.is_active is True  # Default value


def test_role_model_fields():
    """Test Role model has all required fields"""
    role = Role(
        email="user@example.com",
        role_type="manager"
    )
    assert role.email == "user@example.com"
    assert role.role_type == "manager"
    assert role.is_active is True  # Default value


def test_activity_log_model_fields():
    """Test ActivityLog model has all required fields"""
    log = ActivityLog(
        user_email="user@example.com",
        action="login",
        target_email="admin@example.com",
        details="User logged in"
    )
    assert log.user_email == "user@example.com"
    assert log.action == "login"
    assert log.target_email == "admin@example.com"
    assert log.details == "User logged in"


def test_feedback_model_fields():
    """Test Feedback model has all required fields"""
    feedback = Feedback(
        candidate_id=1,
        manager_email="manager@example.com",
        feedback_text="Good candidate",
        status="shortlisted"
    )
    assert feedback.candidate_id == 1
    assert feedback.manager_email == "manager@example.com"
    assert feedback.feedback_text == "Good candidate"
    assert feedback.status == "shortlisted"

