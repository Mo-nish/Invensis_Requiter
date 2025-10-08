#!/usr/bin/env python3
"""
Migration script to fix file paths in existing candidate records
Removes 'static/' prefix from resume_path and image_path fields
"""

from models_mongo import candidates_collection
from bson import ObjectId

def fix_file_paths():
    """Fix file paths in the database by removing 'static/' prefix"""
    print("🔍 Starting file path migration...")
    print("=" * 60)
    
    # Find all candidates with paths starting with 'static/'
    candidates_to_fix = list(candidates_collection.find({
        '$or': [
            {'resume_path': {'$regex': '^static/'}},
            {'image_path': {'$regex': '^static/'}}
        ]
    }))
    
    print(f"📊 Found {len(candidates_to_fix)} candidates with incorrect file paths")
    
    if len(candidates_to_fix) == 0:
        print("✅ No candidates need fixing. All paths are correct!")
        return
    
    fixed_count = 0
    error_count = 0
    
    for candidate in candidates_to_fix:
        try:
            candidate_id = candidate['_id']
            candidate_name = candidate.get('name', candidate.get('email', 'Unknown'))
            updates = {}
            
            # Fix resume_path
            if 'resume_path' in candidate and candidate['resume_path'].startswith('static/'):
                old_resume_path = candidate['resume_path']
                new_resume_path = old_resume_path.replace('static/', '', 1)
                updates['resume_path'] = new_resume_path
                print(f"  📄 Resume: {old_resume_path} → {new_resume_path}")
            
            # Fix image_path
            if 'image_path' in candidate and candidate['image_path'].startswith('static/'):
                old_image_path = candidate['image_path']
                new_image_path = old_image_path.replace('static/', '', 1)
                updates['image_path'] = new_image_path
                print(f"  🖼️  Image: {old_image_path} → {new_image_path}")
            
            # Update the candidate if there are changes
            if updates:
                result = candidates_collection.update_one(
                    {'_id': candidate_id},
                    {'$set': updates}
                )
                
                if result.modified_count > 0:
                    print(f"✅ Fixed: {candidate_name} (ID: {candidate_id})")
                    fixed_count += 1
                else:
                    print(f"⚠️  No changes made for: {candidate_name}")
            
        except Exception as e:
            print(f"❌ Error fixing candidate {candidate.get('_id')}: {e}")
            error_count += 1
    
    print("=" * 60)
    print(f"🎉 Migration complete!")
    print(f"✅ Fixed: {fixed_count} candidates")
    if error_count > 0:
        print(f"❌ Errors: {error_count} candidates")
    
    return fixed_count

if __name__ == "__main__":
    try:
        fixed = fix_file_paths()
        print(f"\n✨ Successfully migrated {fixed} candidate file paths!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
