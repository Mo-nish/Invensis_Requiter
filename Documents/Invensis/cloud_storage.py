"""
Cloud Storage Service for Invensis Hiring Portal
Supports AWS S3 for persistent file storage
"""
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename
import uuid

# S3 Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_REGION = os.getenv('S3_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Check if S3 is configured
def is_s3_configured():
    """Check if S3 credentials are configured"""
    return all([
        S3_BUCKET_NAME,
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY
    ])

# Initialize S3 client
s3_client = None
if is_s3_configured():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=S3_REGION
        )
        print(f"✅ S3 client initialized successfully for bucket: {S3_BUCKET_NAME}")
    except Exception as e:
        print(f"❌ Error initializing S3 client: {str(e)}")
        s3_client = None
else:
    print("⚠️ S3 not configured - using local file storage")
    print(f"   S3_BUCKET_NAME: {'SET' if S3_BUCKET_NAME else 'NOT_SET'}")
    print(f"   AWS_ACCESS_KEY_ID: {'SET' if AWS_ACCESS_KEY_ID else 'NOT_SET'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'SET' if AWS_SECRET_ACCESS_KEY else 'NOT_SET'}")

def upload_file_to_s3(file, folder='uploads', file_type='resume'):
    """
    Upload a file to S3
    
    Args:
        file: FileStorage object from Flask request
        folder: S3 folder path (e.g., 'resumes', 'images')
        file_type: Type of file ('resume' or 'image')
    
    Returns:
        tuple: (success: bool, file_url: str or error_message: str, s3_key: str or None)
    """
    if not is_s3_configured() or not s3_client:
        return False, "S3 not configured", None
    
    if not file or not file.filename:
        return False, "No file provided", None
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        s3_key = f"{folder}/{file_type}/{unique_filename}"
        
        # Reset file pointer to beginning
        file.seek(0)
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                'ContentType': file.content_type or 'application/octet-stream',
                'ACL': 'public-read'  # Make files publicly accessible
            }
        )
        
        # Generate public URL
        file_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        
        print(f"✅ File uploaded to S3: {file_url}")
        return True, file_url, s3_key
        
    except NoCredentialsError:
        error_msg = "AWS credentials not found"
        print(f"❌ {error_msg}")
        return False, error_msg, None
    except ClientError as e:
        error_msg = f"S3 upload error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg, None
    except Exception as e:
        error_msg = f"Unexpected error uploading to S3: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg, None

def delete_file_from_s3(s3_key):
    """
    Delete a file from S3
    
    Args:
        s3_key: S3 object key (path)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not is_s3_configured() or not s3_client:
        return False
    
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        print(f"✅ File deleted from S3: {s3_key}")
        return True
    except ClientError as e:
        print(f"❌ Error deleting file from S3: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error deleting from S3: {str(e)}")
        return False

def get_file_url(s3_key):
    """
    Get public URL for an S3 file
    
    Args:
        s3_key: S3 object key (path)
    
    Returns:
        str: Public URL or None
    """
    if not is_s3_configured():
        return None
    
    return f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

def is_cloud_url(file_path):
    """
    Check if a file path is a cloud URL (S3) or local path
    
    Args:
        file_path: File path or URL
    
    Returns:
        bool: True if it's a cloud URL, False if local path
    """
    if not file_path:
        return False
    return file_path.startswith('http://') or file_path.startswith('https://')

