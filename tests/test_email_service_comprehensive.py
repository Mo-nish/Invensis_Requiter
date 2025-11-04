"""Comprehensive tests for email_service.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from email_service import (
    build_role_assignment_body, build_candidate_assignment_body,
    send_email, send_password_reset_email, send_password_changed_confirmation_email
)


class MockCandidate:
    def __init__(self):
        self.first_name = "Jane"
        self.last_name = "Doe"
        self.experience = 5
        self.email = "jane@example.com"
        self.phone = "1234567890"
        self.reference_id = "REF-123"


def test_build_role_assignment_body_manager():
    """Test build_role_assignment_body for manager role"""
    body = build_role_assignment_body("manager")
    assert "Manager" in body
    assert "/register" in body
    assert "Invensis Hiring Portal" in body


def test_build_role_assignment_body_hr():
    """Test build_role_assignment_body for hr role"""
    body = build_role_assignment_body("hr")
    assert "Hr" in body or "HR" in body
    assert "/register" in body


def test_build_role_assignment_body_admin():
    """Test build_role_assignment_body for admin role"""
    body = build_role_assignment_body("admin")
    assert "Admin" in body
    assert "register" in body.lower()


def test_build_candidate_assignment_body_with_datetime():
    """Test build_candidate_assignment_body with datetime"""
    candidate = MockCandidate()
    interview_date = datetime(2024, 12, 25, 14, 30)
    body = build_candidate_assignment_body(candidate, interview_date)
    assert "Dec" in body or "12" in body
    assert "Jane" in body
    assert "Doe" in body
    assert candidate.email in body
    assert candidate.reference_id in body


def test_build_candidate_assignment_body_without_datetime():
    """Test build_candidate_assignment_body without datetime"""
    candidate = MockCandidate()
    body = build_candidate_assignment_body(candidate, None)
    assert "TBD" in body
    assert candidate.first_name in body
    assert candidate.last_name in body


def test_build_candidate_assignment_body_contains_all_fields():
    """Test build_candidate_assignment_body contains all candidate fields"""
    candidate = MockCandidate()
    body = build_candidate_assignment_body(candidate, None)
    assert candidate.first_name in body
    assert candidate.last_name in body
    assert str(candidate.experience) in body
    assert candidate.email in body
    assert candidate.phone in body
    assert candidate.reference_id in body


def test_send_password_reset_email_format():
    """Test send_password_reset_email email format"""
    with patch('email_service.send_email') as mock_send:
        send_password_reset_email("user@example.com", "John Doe", "token123", "http://localhost:5000")
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "Password Reset" in args[0][0]  # subject
        assert "user@example.com" in str(args[0][1])  # recipients
        assert "token123" in args[0][2]  # body
        assert "localhost:5000" in args[0][2]  # body


def test_send_password_changed_confirmation_email_format():
    """Test send_password_changed_confirmation_email email format"""
    with patch('email_service.send_email') as mock_send:
        send_password_changed_confirmation_email("user@example.com", "John Doe", "http://localhost:5000")
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "Password Successfully Changed" in args[0][0]  # subject
        assert "user@example.com" in str(args[0][1])  # recipients
        assert "localhost:5000" in args[0][2]  # body

