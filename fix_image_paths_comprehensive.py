#!/usr/bin/env python3
"""
Comprehensive fix for image paths in the database
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hiring_tool"
COLLECTION_NAME = "candidates"

def check_and_fix_image_paths():
    """Check and fix all image path issues"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        print("🔍 Connected to MongoDB successfully!")
        print("=" * 60)
        
        # Find all candidates
        all_candidates = list(collection.find({}))
        print(f"Total candidates in database: {len(all_candidates)}")
        
        # Check image paths
        candidates_with_images = 0
        candidates_with_incorrect_paths = 0
        candidates_with_correct_paths = 0
        
        for candidate in all_candidates:
            candidate_id = candidate.get('_id')
            first_name = candidate.get('first_name', 'Unknown')
            last_name = candidate.get('last_name', 'Unknown')
            image_path = candidate.get('image_path')
            
            print(f"\n👤 Candidate: {first_name} {last_name} (ID: {candidate_id})")
            
            if not image_path:
                print("  📷 No image path")
                continue
                
            candidates_with_images += 1
            print(f"  📷 Image path: {image_path}")
            
            # Check if the path is correct
            if image_path.startswith('static/uploads/'):
                print("  ❌ INCORRECT: Path starts with 'static/uploads/'")
                candidates_with_incorrect_paths += 1
                
                # Fix the path
                new_path = image_path.replace('static/uploads/', 'uploads/')
                print(f"  🔧 Fixing to: {new_path}")
                
                # Update database
                result = collection.update_one(
                    {"_id": candidate_id},
                    {"$set": {"image_path": new_path}}
                )
                
                if result.modified_count > 0:
                    print("  ✅ Database updated successfully")
                else:
                    print("  ❌ Failed to update database")
                    
            elif image_path.startswith('uploads/'):
                print("  ✅ CORRECT: Path starts with 'uploads/'")
                candidates_with_correct_paths += 1
                
                # Check if file actually exists
                full_path = os.path.join('static', image_path)
                if os.path.exists(full_path):
                    print(f"  ✅ File exists at: {full_path}")
                else:
                    print(f"  ❌ File missing at: {full_path}")
                    
            else:
                print(f"  ⚠️  UNKNOWN format: {image_path}")
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY:")
        print(f"  Total candidates: {len(all_candidates)}")
        print(f"  Candidates with images: {candidates_with_images}")
        print(f"  Correct paths: {candidates_with_correct_paths}")
        print(f"  Fixed paths: {candidates_with_incorrect_paths}")
        
        # Check file existence for all candidates
        print(f"\n🔍 Checking file existence...")
        missing_files = 0
        
        for candidate in collection.find({"image_path": {"$exists": True, "$ne": None}}):
            image_path = candidate.get('image_path', '')
            if image_path and image_path.startswith('uploads/'):
                full_path = os.path.join('static', image_path)
                if not os.path.exists(full_path):
                    missing_files += 1
                    print(f"  ❌ Missing file: {full_path}")
                    print(f"     Candidate: {candidate.get('first_name', 'Unknown')} {candidate.get('last_name', 'Unknown')}")
        
        if missing_files == 0:
            print(f"  ✅ All image files exist!")
        else:
            print(f"  ⚠️  {missing_files} image files are missing")
        
        client.close()
        print("\n🔌 Database connection closed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Comprehensive Image Path Fix")
    print("=" * 60)
    check_and_fix_image_paths()
    print("=" * 60)
    print("✅ Image path checking and fixing completed!")
