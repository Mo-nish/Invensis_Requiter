"""Comprehensive tests for cloudinary_config module"""
import os
from unittest.mock import patch, MagicMock
from Documents.Invensis import cloudinary_config


def test_check_cloudinary_configured():
    """Test Cloudinary config check"""
    result = cloudinary_config.check_cloudinary_configured()
    assert isinstance(result, bool)


def test_get_cloudinary_info():
    """Test getting Cloudinary info"""
    info = cloudinary_config.get_cloudinary_info()
    assert 'configured' in info
    assert 'cloud_name' in info
    assert 'api_key_set' in info
    assert 'api_secret_set' in info
    assert isinstance(info['configured'], bool)


def test_get_resource_type_image():
    """Test resource type detection for images"""
    assert cloudinary_config.get_resource_type('test.jpg') == 'image'
    assert cloudinary_config.get_resource_type('test.PNG') == 'image'
    assert cloudinary_config.get_resource_type('test.gif') == 'image'
    assert cloudinary_config.get_resource_type('test.webp') == 'image'


def test_get_resource_type_raw():
    """Test resource type detection for raw files"""
    assert cloudinary_config.get_resource_type('test.pdf') == 'raw'
    assert cloudinary_config.get_resource_type('test.doc') == 'raw'
    assert cloudinary_config.get_resource_type('test.docx') == 'raw'
    assert cloudinary_config.get_resource_type('test.txt') == 'raw'


def test_get_resource_type_auto():
    """Test resource type detection defaults"""
    assert cloudinary_config.get_resource_type('test.unknown') == 'auto'
    assert cloudinary_config.get_resource_type('') == 'auto'
    assert cloudinary_config.get_resource_type(None) == 'auto'


def test_upload_file_to_cloudinary_no_file():
    """Test upload with no file"""
    success, result, public_id = cloudinary_config.upload_file_to_cloudinary(None)
    assert success is False
    assert "No file provided" in result
    assert public_id is None


def test_delete_file_from_cloudinary_no_id():
    """Test delete with no public_id"""
    result = cloudinary_config.delete_file_from_cloudinary(None)
    assert result is True  # Should return True when nothing to delete


def test_extract_public_id_from_url_valid():
    """Test extracting public_id from valid Cloudinary URL"""
    url = "https://res.cloudinary.com/test/raw/upload/v1234567890/uploads/test.pdf"
    public_id = cloudinary_config.extract_public_id_from_url(url)
    assert public_id is not None
    assert 'uploads' in public_id or 'test' in public_id


def test_extract_public_id_from_url_invalid():
    """Test extracting public_id from invalid URL"""
    assert cloudinary_config.extract_public_id_from_url(None) is None
    assert cloudinary_config.extract_public_id_from_url("http://example.com/file.pdf") is None
    assert cloudinary_config.extract_public_id_from_url("") is None


def test_extract_public_id_from_url_no_cloudinary():
    """Test extracting public_id from non-Cloudinary URL"""
    result = cloudinary_config.extract_public_id_from_url("https://example.com/file.pdf")
    assert result is None

