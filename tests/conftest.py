"""Pytest configuration for test collection"""
import pytest
import os


def pytest_ignore_collect(path, config):
    """Ignore specific test files that should not be collected"""
    path_str = str(path)
    
    # Ignore deleted test files
    ignored_files = [
        'test_chatbot_config.py',
        'test_s3_config.py',
        'test_cloudinary_config.py',
        'test_chatbot.py',
        'test_reset_password_flow.py',
        'test_forgot_password.py',
        'test_email_builders.py'
    ]
    
    for ignored_file in ignored_files:
        if ignored_file in path_str:
            return True
    
    return False

