#!/usr/bin/env python3
"""
Fix existing image paths in the database to ensure they work with url_for('static', filename=...)
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "invensis_hiring"
COLLECTION_NAME = "candidates"

def fix_image_paths():
    """Fix image paths in the database"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        print("Connected to MongoDB successfully!")
        
        # Find all candidates with image_path
        candidates = collection.find({"image_path": {"$exists": True, "$ne": None}})
        
        fixed_count = 0
        total_count = 0
        
        for candidate in candidates:
            total_count += 1
            current_path = candidate.get('image_path', '')
            
            if not current_path:
                continue
                
            print(f"Candidate: {candidate.get('first_name', 'Unknown')} {candidate.get('last_name', 'Unknown')}")
            print(f"  Current image_path: {current_path}")
            
            # Check if the path needs fixing
            if current_path.startswith('static/uploads/'):
                # Remove 'static/' prefix
                new_path = current_path.replace('static/uploads/', 'uploads/')
                print(f"  Fixed path: {new_path}")
                
                # Update the database
                result = collection.update_one(
                    {"_id": candidate["_id"]},
                    {"$set": {"image_path": new_path}}
                )
                
                if result.modified_count > 0:
                    fixed_count += 1
                    print(f"  ✅ Updated in database")
                else:
                    print(f"  ❌ Failed to update database")
                    
            elif current_path.startswith('uploads/'):
                print(f"  ✅ Path is already correct")
            else:
                print(f"  ⚠️  Unknown path format: {current_path}")
            
            print()
        
        print(f"Summary:")
        print(f"  Total candidates with images: {total_count}")
        print(f"  Fixed paths: {fixed_count}")
        print(f"  Already correct: {total_count - fixed_count}")
        
        # Also check if the actual files exist
        print(f"\nChecking file existence...")
        missing_files = 0
        
        for candidate in collection.find({"image_path": {"$exists": True, "$ne": None}}):
            image_path = candidate.get('image_path', '')
            if image_path:
                full_path = os.path.join('static', image_path)
                if not os.path.exists(full_path):
                    missing_files += 1
                    print(f"  ❌ Missing file: {full_path} for candidate {candidate.get('first_name', 'Unknown')} {candidate.get('last_name', 'Unknown')}")
        
        if missing_files == 0:
            print(f"  ✅ All image files exist!")
        else:
            print(f"  ⚠️  {missing_files} image files are missing")
        
        client.close()
        print("\nDatabase connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Fixing Image Paths in Database...")
    print("=" * 50)
    fix_image_paths()
    print("=" * 50)
    print("✅ Image path fixing completed!")
