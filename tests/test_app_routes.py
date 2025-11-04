"""Tests for app_mongo.py route handlers"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from flask_login import LoginManager
from models_mongo import User
from bson import ObjectId


def test_index_route_user_counts():
    """Test index route gets user counts"""
    with patch('app_mongo.User.count_by_role') as mock_count:
        mock_count.side_effect = lambda role: {
            'hr_role': 5,
            'recruiter': 3,
            'manager': 10,
            'cluster': 2
        }.get(role, 0)
        
        from app_mongo import app
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert b'hr_count' in response.data or b'5' in response.data


def test_login_route_get():
    """Test login route GET request"""
    from app_mongo import app
    with app.test_client() as client:
        response = client.get('/login')
        assert response.status_code == 200


def test_login_route_post_valid():
    """Test login route POST with valid credentials"""
    from app_mongo import app
    from flask_login import login_user
    
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.role = "admin"
    mock_user.check_password = Mock(return_value=True)
    mock_user.get_id = Mock(return_value=str(ObjectId()))
    mock_user.is_authenticated = True
    
    with patch('app_mongo.User.find_by_email', return_value=mock_user):
        with patch('app_mongo.login_user') as mock_login:
            with patch('app_mongo.create_token') as mock_token:
                mock_token.return_value = "test_token"
                with app.test_client() as client:
                    response = client.post('/login', data={
                        'email': 'test@example.com',
                        'password': 'password123'
                    }, follow_redirects=False)
                    # Should redirect
                    assert response.status_code in [302, 200]


def test_login_route_post_invalid():
    """Test login route POST with invalid credentials"""
    from app_mongo import app
    
    with patch('app_mongo.User.find_by_email', return_value=None):
        with app.test_client() as client:
            response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'wrongpass'
            })
            assert response.status_code == 200


def test_register_route_get():
    """Test register route GET request"""
    from app_mongo import app
    with app.test_client() as client:
        response = client.get('/register')
        assert response.status_code == 200


def test_register_route_get_with_token():
    """Test register route GET with invitation token"""
    from app_mongo import app
    
    with patch('app_mongo.verify_token') as mock_verify:
        mock_verify.return_value = {
            'type': 'invitation',
            'email': 'invited@example.com',
            'role': 'manager'
        }
        with app.test_client() as client:
            response = client.get('/register?token=test_token')
            assert response.status_code == 200


def test_forgot_password_route_post_valid():
    """Test forgot_password route POST with valid email"""
    from app_mongo import app
    
    mock_user = Mock()
    mock_user.get_id = Mock(return_value=str(ObjectId()))
    
    with patch('app_mongo.User.find_by_email', return_value=mock_user):
        with patch('app_mongo.PasswordResetToken.find_by_user_id', return_value=None):
            with patch('app_mongo.PasswordResetToken') as mock_token_class:
                mock_token = Mock()
                mock_token.token = "test_token"
                mock_token.save = Mock()
                mock_token_class.return_value = mock_token
                
                with patch('app_mongo.send_password_reset_email') as mock_send:
                    with app.test_client() as client:
                        response = client.post('/forgot-password', 
                                             json={'email': 'test@example.com'},
                                             content_type='application/json')
                        assert response.status_code == 200
                        data = response.get_json()
                        assert data['success'] is True


def test_forgot_password_route_post_no_email():
    """Test forgot_password route POST without email"""
    from app_mongo import app
    with app.test_client() as client:
        response = client.post('/forgot-password', 
                             json={},
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


def test_forgot_password_route_post_user_not_found():
    """Test forgot_password route POST with non-existent user"""
    from app_mongo import app
    
    with patch('app_mongo.User.find_by_email', return_value=None):
        with app.test_client() as client:
            response = client.post('/forgot-password', 
                                 json={'email': 'nonexistent@example.com'},
                                 content_type='application/json')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True  # Should not reveal user doesn't exist


def test_logout_route():
    """Test logout route"""
    from app_mongo import app
    from flask_login import login_user
    
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.role = "admin"
    mock_user.is_authenticated = True
    mock_user.get_id = Mock(return_value=str(ObjectId()))
    
    with patch('app_mongo.logout_user') as mock_logout:
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(ObjectId())
            response = client.get('/logout', follow_redirects=False)
            # Should redirect
            assert response.status_code in [302, 200]

