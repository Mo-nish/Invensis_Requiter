"""
Cloudinary Configuration and Helper Functions
Handles file uploads and deletions for resumes and images
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

def upload_file_to_cloudinary(file, folder='uploads', resource_type='auto'):
    """
    Upload a file to Cloudinary
    
    Args:
        file: FileStorage object from Flask request.files
        folder: Folder name in Cloudinary (e.g., 'resumes', 'images')
        resource_type: 'image', 'raw' (for PDFs), or 'auto'
    
    Returns:
        tuple: (success: bool, file_url: str or error_message: str, public_id: str)
    """
    try:
        if not file or not file.filename:
            return False, "No file provided", None
        
        if not check_cloudinary_configured():
            return False, "Cloudinary not configured", None
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
        
        file_url = result.get('secure_url')
        public_id = result.get('public_id')
        
        print(f"✅ File uploaded to Cloudinary: {file_url}")
        return True, file_url, public_id
        
    except Exception as e:
        print(f"❌ Cloudinary upload error: {str(e)}")
        return False, f"Upload failed: {str(e)}", None

def delete_file_from_cloudinary(public_id, resource_type='raw'):
    """
    Delete a file from Cloudinary
    
    Args:
        public_id: Cloudinary public_id of the file
        resource_type: 'image', 'raw' (for PDFs), or 'video'
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not public_id:
            return True  # Nothing to delete
        
        if not check_cloudinary_configured():
            return False
        
        # Delete from Cloudinary
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        
        if result.get('result') == 'ok':
            print(f"✅ File deleted from Cloudinary: {public_id}")
            return True
        else:
            print(f"⚠️  Cloudinary delete result: {result}")
            return False
        
    except Exception as e:
        print(f"❌ Cloudinary delete error: {str(e)}")
        return False

def extract_public_id_from_url(cloudinary_url):
    """
    Extract public_id from Cloudinary URL
    
    Args:
        cloudinary_url: Full Cloudinary URL
    
    Returns:
        str: public_id or None
    """
    try:
        if not cloudinary_url or 'cloudinary.com' not in cloudinary_url:
            return None
        
        # URL format: https://res.cloudinary.com/cloud_name/resource_type/upload/v1234567890/folder/filename.ext
        # We want: folder/filename (without extension for raw files)
        
        parts = cloudinary_url.split('/upload/')
        if len(parts) == 2:
            # Get everything after 'upload/'
            path = parts[1]
            # Remove version number (v1234567890/)
            if path.startswith('v'):
                path = '/'.join(path.split('/')[1:])
            # Remove file extension
            public_id = path.rsplit('.', 1)[0]
            return public_id
        
        return None
        
    except Exception as e:
        print(f"❌ Error extracting public_id: {str(e)}")
        return None

def check_cloudinary_configured():
    """Check if Cloudinary is properly configured"""
    return bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

def get_cloudinary_info():
    """Get Cloudinary configuration info for debugging"""
    return {
        'configured': check_cloudinary_configured(),
        'cloud_name': CLOUDINARY_CLOUD_NAME,
        'api_key_set': bool(CLOUDINARY_API_KEY),
        'api_secret_set': bool(CLOUDINARY_API_SECRET)
    }

# Helper function to determine resource type
def get_resource_type(filename):
    """Determine Cloudinary resource type based on file extension"""
    if not filename:
        return 'auto'
    
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']:
        return 'image'
    elif ext in ['pdf', 'doc', 'docx', 'txt', 'csv', 'xls', 'xlsx']:
        return 'raw'
    else:
        return 'auto'

