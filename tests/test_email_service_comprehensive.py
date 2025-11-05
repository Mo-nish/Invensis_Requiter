"""Comprehensive tests for email_service.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from email_service import (
    send_email, send_password_reset_email, send_password_changed_confirmation_email,
    send_role_assignment_email, send_candidate_assignment_email, send_feedback_notification_email
)


class MockCandidate:
    def __init__(self):
        self.first_name = "Jane"
        self.last_name = "Doe"
        self.name = "Jane Doe"
        self.experience = 5
        self.email = "jane@example.com"
        self.phone = "1234567890"
        self.reference_id = "REF-123"
        self.feedback = "Good candidate"


def test_send_role_assignment_email_manager():
    """Test send_role_assignment_email for manager role"""
    with patch('email_service.send_email') as mock_send:
        send_role_assignment_email("manager@example.com", "manager")
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "manager" in args[0][0].lower()  # subject contains role
        assert "manager@example.com" in args[0][1]  # recipients
        assert "/register" in args[0][2]  # body contains register link


def test_send_role_assignment_email_hr():
    """Test send_role_assignment_email for hr role"""
    with patch('email_service.send_email') as mock_send:
        send_role_assignment_email("hr@example.com", "hr")
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "hr" in args[0][0].lower() or "Hr" in args[0][0]  # subject contains role


def test_send_candidate_assignment_email_with_datetime():
    """Test send_candidate_assignment_email with datetime"""
    candidate = MockCandidate()
    interview_date = datetime(2024, 12, 25, 14, 30)
    with patch('email_service.send_email') as mock_send:
        send_candidate_assignment_email("manager@example.com", candidate, interview_date)
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "New Candidate Assigned" in args[0][0]  # subject
        assert "Jane" in args[0][2]  # body contains candidate name
        assert "Doe" in args[0][2]  # body contains candidate name
        assert candidate.email in args[0][2]  # body contains email
        assert candidate.reference_id in args[0][2]  # body contains reference ID


def test_send_candidate_assignment_email_without_datetime():
    """Test send_candidate_assignment_email without datetime"""
    candidate = MockCandidate()
    with patch('email_service.send_email') as mock_send:
        send_candidate_assignment_email("manager@example.com", candidate, None)
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "TBD" in args[0][2]  # body contains TBD for interview date
        assert candidate.first_name in args[0][2]
        assert candidate.last_name in args[0][2]


def test_send_candidate_assignment_email_contains_all_fields():
    """Test send_candidate_assignment_email contains all candidate fields"""
    candidate = MockCandidate()
    with patch('email_service.send_email') as mock_send:
        send_candidate_assignment_email("manager@example.com", candidate, None)
        mock_send.assert_called_once()
        body = mock_send.call_args[0][2]
        assert candidate.first_name in body
        assert candidate.last_name in body
        assert str(candidate.experience) in body
        assert candidate.email in body
        assert candidate.phone in body
        assert candidate.reference_id in body


def test_send_feedback_notification_email():
    """Test send_feedback_notification_email"""
    candidate = MockCandidate()
    with patch('email_service.send_email') as mock_send:
        send_feedback_notification_email("hr@example.com", candidate, "shortlisted")
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "Feedback received" in args[0][0]  # subject
        assert candidate.reference_id in args[0][0]  # subject contains reference ID
        assert "hr@example.com" in args[0][1]  # recipients
        assert candidate.name in args[0][2]  # body contains candidate name


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

