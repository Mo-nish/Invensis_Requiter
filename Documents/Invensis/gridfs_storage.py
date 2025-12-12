"""
GridFS Storage Service for Invensis Hiring Portal
Uses MongoDB GridFS for persistent file storage (no external services needed)
"""
from gridfs import GridFS
from werkzeug.utils import secure_filename
import uuid
from bson import ObjectId

# Get MongoDB connection
def get_database():
    """Get MongoDB database connection"""
    from models_mongo import get_database as get_db
    return get_db()

def get_gridfs():
    """Get GridFS instance"""
    db = get_database()
    return GridFS(db)

def upload_file_to_gridfs(file, folder='uploads', file_type='resume', filename=None):
    """
    Upload a file to MongoDB GridFS
    
    Args:
        file: FileStorage object from Flask request, or file-like object with read() and seek() methods
        folder: Folder name (e.g., 'resumes', 'images')
        file_type: Type of file ('resume' or 'image')
        filename: Optional filename (if file doesn't have filename attribute)
    
    Returns:
        tuple: (success: bool, file_id: str or error_message: str, gridfs_id: str or None)
    """
    if not file:
        return False, "No file provided", None
    
    try:
        fs = get_gridfs()
        
        # Get filename
        if hasattr(file, 'filename') and file.filename:
            original_filename = secure_filename(file.filename)
        elif filename:
            original_filename = secure_filename(filename)
        else:
            original_filename = f"file_{uuid.uuid4()}"
        
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Reset file pointer to beginning if possible
        if hasattr(file, 'seek'):
            file.seek(0)
        
        # Get content type
        content_type = 'application/octet-stream'
        if hasattr(file, 'content_type') and file.content_type:
            content_type = file.content_type
        else:
            # Guess from filename
            if original_filename.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif original_filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif original_filename.lower().endswith('.png'):
                content_type = 'image/png'
        
        # Upload to GridFS
        gridfs_id = fs.put(
            file,
            filename=unique_filename,
            content_type=content_type,
            folder=folder,
            file_type=file_type
        )
        
        # Return the GridFS ID as a string
        file_id = str(gridfs_id)
        
        print(f"✅ File uploaded to GridFS: {file_id} (filename: {unique_filename})")
        return True, file_id, file_id
        
    except Exception as e:
        error_msg = f"GridFS upload error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg, None

def get_file_from_gridfs(file_id):
    """
    Get a file from GridFS
    
    Args:
        file_id: GridFS file ID (string or ObjectId)
    
    Returns:
        GridOut object or None
    """
    try:
        fs = get_gridfs()
        
        # Convert string to ObjectId if needed
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        return fs.get(file_id)
    except Exception as e:
        print(f"❌ Error getting file from GridFS: {str(e)}")
        return None

def delete_file_from_gridfs(file_id):
    """
    Delete a file from GridFS
    
    Args:
        file_id: GridFS file ID (string or ObjectId)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        fs = get_gridfs()
        
        # Convert string to ObjectId if needed
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        fs.delete(file_id)
        print(f"✅ File deleted from GridFS: {file_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting file from GridFS: {str(e)}")
        return False

def get_file_url(file_id):
    """
    Get URL for a GridFS file (for use in templates)
    Note: This returns a route URL, not a direct file URL
    
    Args:
        file_id: GridFS file ID (string)
    
    Returns:
        str: URL route for accessing the file
    """
    return f"/gridfs/file/{file_id}"

def is_gridfs_id(file_path):
    """
    Check if a file path is a GridFS ID (24 character hex string)
    
    Args:
        file_path: File path or GridFS ID
    
    Returns:
        bool: True if it's a GridFS ID, False otherwise
    """
    if not file_path:
        return False
    
    # GridFS IDs are 24 character hex strings (ObjectId format)
    if isinstance(file_path, str) and len(file_path) == 24:
        try:
            # Try to convert to ObjectId to validate
            ObjectId(file_path)
            return True
        except:
            return False
    
    return False

def is_cloud_url(file_path):
    """
    Check if a file path is a cloud URL (S3) or local path
    This is for backward compatibility
    
    Args:
        file_path: File path or URL
    
    Returns:
        bool: True if it's a cloud URL, False if local path or GridFS ID
    """
    if not file_path:
        return False
    return file_path.startswith('http://') or file_path.startswith('https://')

