#!/usr/bin/env python3
"""
Direct file patcher for Cloudinary integration
Handles large files that timeout with normal tools
"""

import os
import sys

def patch_recruiter_routes():
    """Patch recruiter_mongo.py to use Cloudinary"""
    
    file_path = 'routes/recruiter_mongo.py'
    print(f"📝 Patching {file_path}...")
    
    try:
        # Read file in chunks to handle large size
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Find import section and add cloudinary import
        import_added = False
        for i, line in enumerate(lines):
            if 'from flask import' in line and not import_added:
                # Find the end of imports
                j = i
                while j < len(lines) and (lines[j].startswith('from ') or lines[j].startswith('import ') or lines[j].strip() == ''):
                    j += 1
                # Insert cloudinary import
                if 'from cloudinary_config import' not in ''.join(lines):
                    lines.insert(j, 'from cloudinary_config import upload_file_to_cloudinary, delete_file_from_cloudinary, get_resource_type, check_cloudinary_configured\n')
                    print("  ✅ Added Cloudinary imports")
                    import_added = True
                break
        
        # Find and patch upload_candidate function
        in_upload_function = False
        patched_resume = False
        patched_image = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect upload_candidate function
            if 'def upload_candidate' in line:
                in_upload_function = True
                print("  📍 Found upload_candidate function")
            
            # Patch resume upload
            if in_upload_function and not patched_resume:
                if 'resume_file.save(' in line or ('resume_path' in line and 'os.path.join' in line and 'uploads' in line):
                    # Replace with Cloudinary upload
                    indent = len(line) - len(line.lstrip())
                    cloudinary_code = [
                        ' ' * indent + '# Upload resume to Cloudinary\n',
                        ' ' * indent + 'resume_path = None\n',
                        ' ' * indent + 'resume_public_id = None\n',
                        ' ' * indent + 'if resume_file and resume_file.filename:\n',
                        ' ' * (indent + 4) + 'resource_type = get_resource_type(resume_file.filename)\n',
                        ' ' * (indent + 4) + 'success, resume_url, resume_public_id = upload_file_to_cloudinary(\n',
                        ' ' * (indent + 8) + 'resume_file,\n',
                        ' ' * (indent + 8) + "folder='invensis/resumes',\n",
                        ' ' * (indent + 8) + 'resource_type=resource_type\n',
                        ' ' * (indent + 4) + ')\n',
                        ' ' * (indent + 4) + 'if success:\n',
                        ' ' * (indent + 8) + 'resume_path = resume_url\n',
                        ' ' * (indent + 8) + 'print(f"✅ Resume uploaded: {resume_url}")\n',
                        ' ' * (indent + 4) + 'else:\n',
                        ' ' * (indent + 8) + 'flash(f"Resume upload failed: {resume_url}", "error")\n',
                    ]
                    lines[i:i+1] = cloudinary_code
                    patched_resume = True
                    print("  ✅ Patched resume upload")
                    i += len(cloudinary_code)
                    continue
            
            # Patch image upload
            if in_upload_function and not patched_image:
                if 'image_file.save(' in line or ('image_path' in line and 'os.path.join' in line and 'uploads' in line):
                    # Replace with Cloudinary upload
                    indent = len(line) - len(line.lstrip())
                    cloudinary_code = [
                        ' ' * indent + '# Upload image to Cloudinary\n',
                        ' ' * indent + 'image_path = None\n',
                        ' ' * indent + 'image_public_id = None\n',
                        ' ' * indent + 'if image_file and image_file.filename:\n',
                        ' ' * (indent + 4) + 'resource_type = get_resource_type(image_file.filename)\n',
                        ' ' * (indent + 4) + 'success, image_url, image_public_id = upload_file_to_cloudinary(\n',
                        ' ' * (indent + 8) + 'image_file,\n',
                        ' ' * (indent + 8) + "folder='invensis/images',\n",
                        ' ' * (indent + 8) + 'resource_type=resource_type\n',
                        ' ' * (indent + 4) + ')\n',
                        ' ' * (indent + 4) + 'if success:\n',
                        ' ' * (indent + 8) + 'image_path = image_url\n',
                        ' ' * (indent + 8) + 'print(f"✅ Image uploaded: {image_url}")\n',
                    ]
                    lines[i:i+1] = cloudinary_code
                    patched_image = True
                    print("  ✅ Patched image upload")
                    i += len(cloudinary_code)
                    continue
            
            i += 1
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Successfully patched {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error patching {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def patch_template(template_path):
    """Patch a template to use Cloudinary URLs directly"""
    
    if not os.path.exists(template_path):
        print(f"  ⚠️  Skipping {template_path} (not found)")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Replace url_for('static', filename=candidate.resume_path) with candidate.resume_path
        content = content.replace(
            "url_for('static', filename=candidate.resume_path)",
            "candidate.resume_path"
        )
        content = content.replace(
            'url_for("static", filename=candidate.resume_path)',
            'candidate.resume_path'
        )
        
        # Replace image_path
        content = content.replace(
            "url_for('static', filename=candidate.image_path)",
            "candidate.image_path"
        )
        content = content.replace(
            'url_for("static", filename=candidate.image_path)',
            'candidate.image_path'
        )
        
        # Replace photo_path
        content = content.replace(
            "url_for('static', filename=candidate.photo_path)",
            "candidate.photo_path"
        )
        content = content.replace(
            'url_for("static", filename=candidate.photo_path)',
            'candidate.photo_path'
        )
        
        if content != original:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Patched {template_path}")
            return True
        else:
            print(f"  ℹ️  No changes needed in {template_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error patching {template_path}: {e}")
        return False

def main():
    print("🚀 Cloudinary Integration Patcher\n")
    print("=" * 60)
    
    # Patch routes
    print("\n📝 Step 1: Patching routes...")
    patch_recruiter_routes()
    
    # Patch templates
    print("\n📝 Step 2: Patching templates...")
    templates = [
        'templates/recruiter/dashboard.html',
        'templates/recruiter/candidates.html',
        'templates/recruiter/candidate_details.html',
        'templates/manager/candidate_details.html',
        'templates/hr/candidate_details.html',
        'templates/hr/candidates.html',
    ]
    
    for template in templates:
        patch_template(template)
    
    print("\n" + "=" * 60)
    print("✅ Patching complete!")
    print("\n📋 Next steps:")
    print("1. Review the changes: git diff")
    print("2. Test locally: python run.py")
    print("3. Commit and push: git add . && git commit -m 'Integrate Cloudinary' && git push")
    print("4. Deploy on Render (Manual Deploy)")
    print("\n🎉 After deployment, resumes will work permanently!")

if __name__ == '__main__':
    main()

