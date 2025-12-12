"""
Migration script to move existing local files to MongoDB GridFS
This helps recover files that are still available locally
"""
import os
from models_mongo import candidates_collection, get_database
from gridfs_storage import upload_file_to_gridfs, is_gridfs_id
from gridfs import GridFS
from bson import ObjectId

def migrate_candidate_files():
    """Migrate all candidate files from local storage to GridFS"""
    print("🔄 Starting file migration to GridFS...")
    print("=" * 60)
    
    # Get all candidates
    candidates = list(candidates_collection.find({}))
    total_candidates = len(candidates)
    print(f"📋 Found {total_candidates} candidates to check")
    
    migrated_resumes = 0
    migrated_images = 0
    skipped_resumes = 0
    skipped_images = 0
    errors = 0
    
    for i, candidate in enumerate(candidates, 1):
        candidate_id = candidate.get('_id')
        candidate_name = candidate.get('name') or candidate.get('first_name', 'Unknown')
        
        print(f"\n[{i}/{total_candidates}] Processing: {candidate_name} ({candidate_id})")
        
        # Migrate resume
        resume_path = candidate.get('resume_path')
        if resume_path:
            # Skip if already GridFS ID or cloud URL
            if is_gridfs_id(resume_path) or resume_path.startswith('http'):
                print(f"  ⏭️  Resume already in GridFS/Cloud: {resume_path[:50]}...")
                skipped_resumes += 1
            else:
                # Try to migrate local file
                local_file_path = None
                
                # Check different possible paths
                possible_paths = [
                    resume_path,  # Original path
                    f"static/{resume_path}",  # With static/ prefix
                    f"static/uploads/{os.path.basename(resume_path)}",  # Full static path
                    os.path.join('static', 'uploads', os.path.basename(resume_path))  # OS path
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        local_file_path = path
                        break
                
                if local_file_path and os.path.exists(local_file_path):
                    try:
                        print(f"  📄 Found resume file: {local_file_path}")
                        
                        # Open and upload file
                        with open(local_file_path, 'rb') as f:
                            from io import BytesIO
                            
                            # Read file data
                            file_data = BytesIO(f.read())
                            file_data.seek(0)
                            
                            # Create a file-like object
                            class FileLike:
                                def __init__(self, data):
                                    self.data = data
                                
                                def read(self, size=-1):
                                    return self.data.read(size)
                                
                                def seek(self, pos):
                                    return self.data.seek(pos)
                            
                            file_obj = FileLike(file_data)
                            
                            # Upload to GridFS
                            success, file_id, gridfs_id = upload_file_to_gridfs(
                                file_obj, 
                                folder='invensis', 
                                file_type='resumes',
                                filename=os.path.basename(local_file_path)
                            )
                            
                            if success:
                                # Update candidate record
                                candidates_collection.update_one(
                                    {'_id': candidate_id},
                                    {'$set': {'resume_path': file_id}}
                                )
                                print(f"  ✅ Resume migrated to GridFS: {file_id}")
                                migrated_resumes += 1
                            else:
                                print(f"  ❌ Failed to migrate resume: {file_id}")
                                errors += 1
                    except Exception as e:
                        print(f"  ❌ Error migrating resume: {str(e)}")
                        errors += 1
                else:
                    print(f"  ⚠️  Resume file not found locally: {resume_path}")
                    skipped_resumes += 1
        
        # Migrate image
        image_path = candidate.get('image_path')
        if image_path:
            # Skip if already GridFS ID or cloud URL
            if is_gridfs_id(image_path) or image_path.startswith('http'):
                print(f"  ⏭️  Image already in GridFS/Cloud: {image_path[:50]}...")
                skipped_images += 1
            else:
                # Try to migrate local file
                local_file_path = None
                
                # Check different possible paths
                possible_paths = [
                    image_path,  # Original path
                    f"static/{image_path}",  # With static/ prefix
                    f"static/uploads/{os.path.basename(image_path)}",  # Full static path
                    os.path.join('static', 'uploads', os.path.basename(image_path))  # OS path
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        local_file_path = path
                        break
                
                if local_file_path and os.path.exists(local_file_path):
                    try:
                        print(f"  🖼️  Found image file: {local_file_path}")
                        
                        # Open and upload file
                        with open(local_file_path, 'rb') as f:
                            from io import BytesIO
                            
                            # Read file data
                            file_data = BytesIO(f.read())
                            file_data.seek(0)
                            
                            # Create a file-like object
                            class FileLike:
                                def __init__(self, data):
                                    self.data = data
                                
                                def read(self, size=-1):
                                    return self.data.read(size)
                                
                                def seek(self, pos):
                                    return self.data.seek(pos)
                            
                            file_obj = FileLike(file_data)
                            
                            # Upload to GridFS
                            success, file_id, gridfs_id = upload_file_to_gridfs(
                                file_obj, 
                                folder='invensis', 
                                file_type='images',
                                filename=os.path.basename(local_file_path)
                            )
                            
                            if success:
                                # Update candidate record
                                candidates_collection.update_one(
                                    {'_id': candidate_id},
                                    {'$set': {'image_path': file_id}}
                                )
                                print(f"  ✅ Image migrated to GridFS: {file_id}")
                                migrated_images += 1
                            else:
                                print(f"  ❌ Failed to migrate image: {file_id}")
                                errors += 1
                    except Exception as e:
                        print(f"  ❌ Error migrating image: {str(e)}")
                        errors += 1
                else:
                    print(f"  ⚠️  Image file not found locally: {image_path}")
                    skipped_images += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary:")
    print(f"  ✅ Resumes migrated: {migrated_resumes}")
    print(f"  ✅ Images migrated: {migrated_images}")
    print(f"  ⏭️  Resumes skipped: {skipped_resumes}")
    print(f"  ⏭️  Images skipped: {skipped_images}")
    print(f"  ❌ Errors: {errors}")
    print("=" * 60)
    
    if migrated_resumes > 0 or migrated_images > 0:
        print("✅ Migration completed successfully!")
    else:
        print("ℹ️  No files were migrated (all files already in GridFS or not found locally)")

if __name__ == '__main__':
    migrate_candidate_files()

