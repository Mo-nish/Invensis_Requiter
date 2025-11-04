"""Tests for app_mongo.py utility functions"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch, MagicMock
from app_mongo import allowed_file, load_user


def test_allowed_file_valid():
    """Test allowed_file() with valid extensions"""
    assert allowed_file("test.pdf") is True
    assert allowed_file("test.PDF") is True  # Case insensitive
    assert allowed_file("test.jpg") is True
    assert allowed_file("test.png") is True
    assert allowed_file("test.jpeg") is True
    assert allowed_file("test.gif") is True


def test_allowed_file_invalid():
    """Test allowed_file() with invalid extensions"""
    assert allowed_file("test.txt") is False
    assert allowed_file("test.exe") is False
    assert allowed_file("test") is False
    assert allowed_file("test.") is False


def test_load_user_with_valid_id():
    """Test load_user() with valid user ID"""
    from models_mongo import User
    from bson import ObjectId
    from unittest.mock import patch
    
    with patch.object(User, 'find_by_id') as mock_find:
        mock_user = Mock()
        mock_find.return_value = mock_user
        result = load_user(str(ObjectId()))
        assert result == mock_user
        mock_find.assert_called_once()


def test_load_user_with_invalid_id():
    """Test load_user() with invalid user ID"""
    from unittest.mock import patch
    from models_mongo import User
    
    with patch.object(User, 'find_by_id', return_value=None):
        result = load_user("invalid_id")
        assert result is None

