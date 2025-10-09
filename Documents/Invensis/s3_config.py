"""
AWS S3 Configuration and Helper Functions
Handles file uploads, downloads, and deletions for resumes and images
"""

import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename

load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME', 'invensis-hiring-portal')
AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-1')

# Initialize S3 client
s3_client = None

def get_s3_client():
    """Get or create S3 client"""
    global s3_client
    if s3_client is None:
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            print("WARNING: AWS credentials not configured. File uploads will fail.")
            return None
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION
        )
    return s3_client

def upload_file_to_s3(file, folder='uploads'):
    """
    Upload a file to S3 bucket
    
    Args:
        file: FileStorage object from Flask request.files
        folder: Folder name in S3 bucket (e.g., 'resumes', 'images')
    
    Returns:
        tuple: (success: bool, file_url: str or error_message: str)
    """
    try:
        if not file or not file.filename:
            return False, "No file provided"
        
        client = get_s3_client()
        if not client:
            return False, "S3 not configured"
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        s3_key = f"{folder}/{unique_filename}"
        
        # Upload file to S3
        client.upload_fileobj(
            file,
            AWS_S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'public-read'  # Make file publicly accessible
            }
        )
        
        # Generate file URL
        file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/{s3_key}"
        
        print(f"✅ File uploaded to S3: {file_url}")
        return True, file_url
        
    except ClientError as e:
        print(f"❌ S3 upload error: {str(e)}")
        return False, f"S3 upload failed: {str(e)}"
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return False, f"Upload failed: {str(e)}"

def delete_file_from_s3(file_url):
    """
    Delete a file from S3 bucket
    
    Args:
        file_url: Full S3 URL of the file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not file_url:
            return True  # Nothing to delete
        
        client = get_s3_client()
        if not client:
            return False
        
        # Extract S3 key from URL
        # URL format: https://bucket-name.s3.region.amazonaws.com/folder/filename
        if AWS_S3_BUCKET_NAME in file_url:
            s3_key = file_url.split(f"{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/")[1]
            
            # Delete file from S3
            client.delete_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=s3_key
            )
            
            print(f"✅ File deleted from S3: {s3_key}")
            return True
        else:
            print(f"⚠️  File URL doesn't match S3 bucket: {file_url}")
            return False
        
    except ClientError as e:
        print(f"❌ S3 delete error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Delete error: {str(e)}")
        return False

def get_file_from_s3(s3_key):
    """
    Get a file from S3 bucket
    
    Args:
        s3_key: S3 key of the file (e.g., 'uploads/filename.pdf')
    
    Returns:
        bytes: File content or None if error
    """
    try:
        client = get_s3_client()
        if not client:
            return None
        
        # Download file from S3
        response = client.get_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=s3_key
        )
        
        return response['Body'].read()
        
    except ClientError as e:
        print(f"❌ S3 download error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return None

def check_s3_configured():
    """Check if S3 is properly configured"""
    return bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_S3_BUCKET_NAME)

def get_s3_info():
    """Get S3 configuration info for debugging"""
    return {
        'configured': check_s3_configured(),
        'bucket': AWS_S3_BUCKET_NAME,
        'region': AWS_S3_REGION,
        'access_key_set': bool(AWS_ACCESS_KEY_ID),
        'secret_key_set': bool(AWS_SECRET_ACCESS_KEY)
    }

