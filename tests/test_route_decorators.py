"""Tests for route decorator functions"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request
from flask_login import current_user


def test_recruiter_required_authenticated():
    """Test recruiter_required decorator with authenticated recruiter"""
    from routes.recruiter_mongo import recruiter_required
    
    @recruiter_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = True
    mock_user.role = "recruiter"
    
    with patch('routes.recruiter_mongo.current_user', mock_user):
        result = test_func()
        assert result == "success"


def test_recruiter_required_not_authenticated():
    """Test recruiter_required decorator with unauthenticated user"""
    from routes.recruiter_mongo import recruiter_required
    from flask import redirect
    
    @recruiter_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = False
    
    with patch('routes.recruiter_mongo.current_user', mock_user):
        with patch('routes.recruiter_mongo.request') as mock_request:
            mock_request.path = "/test"
            mock_request.method = "GET"
            with patch('routes.recruiter_mongo.redirect') as mock_redirect:
                mock_redirect.return_value = "redirected"
                result = test_func()
                assert result == "redirected"


def test_recruiter_required_wrong_role():
    """Test recruiter_required decorator with wrong role"""
    from routes.recruiter_mongo import recruiter_required
    
    @recruiter_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = True
    mock_user.role = "manager"
    
    with patch('routes.recruiter_mongo.current_user', mock_user):
        with patch('routes.recruiter_mongo.request') as mock_request:
            mock_request.path = "/test"
            mock_request.method = "GET"
            with patch('routes.recruiter_mongo.redirect') as mock_redirect:
                mock_redirect.return_value = "redirected"
                result = test_func()
                assert result == "redirected"


def test_manager_required_authenticated():
    """Test manager_required decorator with authenticated manager"""
    from routes.manager_mongo import manager_required
    
    @manager_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = True
    mock_user.role = "manager"
    
    with patch('routes.manager_mongo.current_user', mock_user):
        result = test_func()
        assert result == "success"


def test_manager_required_not_authenticated():
    """Test manager_required decorator with unauthenticated user"""
    from routes.manager_mongo import manager_required
    
    @manager_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = False
    
    with patch('routes.manager_mongo.current_user', mock_user):
        with patch('routes.manager_mongo.redirect') as mock_redirect:
            mock_redirect.return_value = "redirected"
            result = test_func()
            assert result == "redirected"


def test_admin_required_authenticated():
    """Test admin_required decorator with authenticated admin"""
    from routes.admin_mongo import admin_required
    
    @admin_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = True
    mock_user.role = "admin"
    
    with patch('routes.admin_mongo.current_user', mock_user):
        result = test_func()
        assert result == "success"


def test_hr_required_authenticated():
    """Test hr_required decorator with authenticated hr"""
    from routes.hr_mongo import hr_required
    
    @hr_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = True
    mock_user.role = "hr_role"
    
    with patch('routes.hr_mongo.current_user', mock_user):
        result = test_func()
        assert result == "success"


def test_cluster_required_authenticated():
    """Test cluster_required decorator with authenticated cluster"""
    from routes.cluster_mongo import cluster_required
    
    @cluster_required
    def test_func():
        return "success"
    
    mock_user = Mock()
    mock_user.is_authenticated = True
    mock_user.role = "cluster"
    
    with patch('routes.cluster_mongo.current_user', mock_user):
        result = test_func()
        assert result == "success"

