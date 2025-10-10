"""
Script to integrate Cloudinary into the Invensis application
This will update routes and templates to use Cloudinary for file storage
"""

import os
import re

def update_recruiter_routes():
    """Update recruiter routes to use Cloudinary for uploads"""
    
    file_path = 'routes/recruiter_mongo.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add cloudinary import at the top (after other imports)
        if 'from cloudinary_config import' not in content:
            # Find the last import line
            import_pattern = r'(from\s+\w+\s+import\s+[^\n]+\n)(?!from|import)'
            content = re.sub(
                import_pattern,
                r'\1from cloudinary_config import upload_file_to_cloudinary, delete_file_from_cloudinary, get_resource_type, check_cloudinary_configured\n',
                content,
                count=1
            )
        
        # Find and update the upload_candidate function
        # Look for the section where files are saved
        old_upload_pattern = r'(resume_file\.save\(resume_path\)|os\.path\.join\(.*?UPLOAD_FOLDER.*?resume.*?\))'
        
        if 'upload_file_to_cloudinary' not in content:
            # Replace local file save with Cloudinary upload
            content = re.sub(
                r'# Save resume file.*?resume_path = .*?\n.*?resume_file\.save\(.*?\)',
                '''# Upload resume to Cloudinary
                    resume_file = request.files.get('resume')
                    if resume_file and resume_file.filename:
                        resource_type = get_resource_type(resume_file.filename)
                        success, resume_url, resume_public_id = upload_file_to_cloudinary(
                            resume_file, 
                            folder='invensis/resumes',
                            resource_type=resource_type
                        )
                        if success:
                            resume_path = resume_url
                            print(f"✅ Resume uploaded to Cloudinary: {resume_url}")
                        else:
                            flash(f"Resume upload failed: {resume_url}", "error")
                            return redirect(url_for('recruiter.dashboard'))
                    else:
                        resume_path = None''',
                content,
                flags=re.DOTALL
            )
            
            # Replace image upload
            content = re.sub(
                r'# Save image file.*?image_path = .*?\n.*?image_file\.save\(.*?\)',
                '''# Upload image to Cloudinary
                    image_file = request.files.get('photo')
                    if image_file and image_file.filename:
                        resource_type = get_resource_type(image_file.filename)
                        success, image_url, image_public_id = upload_file_to_cloudinary(
                            image_file,
                            folder='invensis/images',
                            resource_type=resource_type
                        )
                        if success:
                            image_path = image_url
                            print(f"✅ Image uploaded to Cloudinary: {image_url}")
                        else:
                            image_path = None
                    else:
                        image_path = None''',
                content,
                flags=re.DOTALL
            )
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {str(e)}")
        return False

def update_templates():
    """Update templates to use Cloudinary URLs directly"""
    
    templates = [
        'templates/recruiter/dashboard.html',
        'templates/recruiter/candidates.html',
        'templates/recruiter/candidate_details.html',
        'templates/manager/candidate_details.html',
        'templates/hr/candidate_details.html',
    ]
    
    for template_path in templates:
        if not os.path.exists(template_path):
            print(f"⚠️  Skipping {template_path} (not found)")
            continue
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace url_for('static', filename=candidate.resume_path) with direct URL
            # Old: {{ url_for('static', filename=candidate.resume_path) }}
            # New: {{ candidate.resume_path }}
            
            content = re.sub(
                r'\{\{\s*url_for\([\'"]static[\'"]\s*,\s*filename\s*=\s*candidate\.resume_path\)\s*\}\}',
                '{{ candidate.resume_path }}',
                content
            )
            
            content = re.sub(
                r'\{\{\s*url_for\([\'"]static[\'"]\s*,\s*filename\s*=\s*candidate\.image_path\)\s*\}\}',
                '{{ candidate.image_path }}',
                content
            )
            
            # Also handle photo_path
            content = re.sub(
                r'\{\{\s*url_for\([\'"]static[\'"]\s*,\s*filename\s*=\s*candidate\.photo_path\)\s*\}\}',
                '{{ candidate.photo_path }}',
                content
            )
            
            # Write back
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated {template_path}")
            
        except Exception as e:
            print(f"❌ Error updating {template_path}: {str(e)}")

def create_test_route():
    """Add a test route to verify Cloudinary configuration"""
    
    test_route = '''
@recruiter_bp.route('/test-cloudinary')
@recruiter_required
def test_cloudinary():
    """Test Cloudinary configuration"""
    from cloudinary_config import get_cloudinary_info
    info = get_cloudinary_info()
    return jsonify(info)
'''
    
    print("\n📋 Add this test route to routes/recruiter_mongo.py:")
    print(test_route)

if __name__ == '__main__':
    print("🚀 Starting Cloudinary Integration...\n")
    
    # Update routes
    print("📝 Updating routes...")
    update_recruiter_routes()
    
    # Update templates
    print("\n📝 Updating templates...")
    update_templates()
    
    # Show test route
    print("\n✅ Integration complete!")
    print("\n📋 Next steps:")
    print("1. Review the changes")
    print("2. Test file upload on the dashboard")
    print("3. Verify resume view works without 404")
    print("\n🔧 If uploads fail, check Render environment variables:")
    print("   - CLOUDINARY_CLOUD_NAME=dspnu4jld")
    print("   - CLOUDINARY_API_KEY=192143441554598")
    print("   - CLOUDINARY_API_SECRET=o1ZSjvmZGpaU9rNM9nZQcES8vpk")

