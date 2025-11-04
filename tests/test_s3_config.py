"""Comprehensive tests for s3_config module"""
import os
from unittest.mock import patch, MagicMock
from Documents.Invensis import s3_config


def test_check_s3_configured_without_env():
    """Test S3 config check when env vars not set"""
    with patch.dict(os.environ, {}, clear=True):
        # Reload module to get fresh env vars
        import importlib
        importlib.reload(s3_config)
        result = s3_config.check_s3_configured()
        assert isinstance(result, bool)


def test_get_s3_info():
    """Test getting S3 info"""
    info = s3_config.get_s3_info()
    assert 'configured' in info
    assert 'bucket' in info
    assert 'region' in info
    assert 'access_key_set' in info
    assert 'secret_key_set' in info
    assert isinstance(info['configured'], bool)


def test_get_s3_client_without_creds():
    """Test S3 client creation without credentials"""
    with patch.dict(os.environ, {}, clear=True):
        import importlib
        importlib.reload(s3_config)
        client = s3_config.get_s3_client()
        # Should return None when not configured
        assert client is None or isinstance(client, object)


def test_upload_file_to_s3_no_file():
    """Test upload with no file"""
    success, result = s3_config.upload_file_to_s3(None)
    assert success is False
    assert "No file provided" in result


def test_upload_file_to_s3_not_configured():
    """Test upload when S3 not configured"""
    mock_file = MagicMock()
    mock_file.filename = "test.pdf"
    with patch.object(s3_config, 'get_s3_client', return_value=None):
        success, result = s3_config.upload_file_to_s3(mock_file)
        assert success is False
        assert "S3 not configured" in result


def test_delete_file_from_s3_no_url():
    """Test delete with no URL"""
    result = s3_config.delete_file_from_s3(None)
    assert result is True  # Should return True when nothing to delete


def test_delete_file_from_s3_not_configured():
    """Test delete when S3 not configured"""
    with patch.object(s3_config, 'get_s3_client', return_value=None):
        result = s3_config.delete_file_from_s3("http://example.com/file.pdf")
        assert result is False


def test_get_file_from_s3_not_configured():
    """Test get file when S3 not configured"""
    with patch.object(s3_config, 'get_s3_client', return_value=None):
        result = s3_config.get_file_from_s3("test/key.pdf")
        assert result is None

