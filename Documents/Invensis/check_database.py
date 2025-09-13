#!/usr/bin/env python3
"""
Check what collections exist in the database and their contents
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hiring_tool"

def check_database():
    """Check database structure and contents"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        print("🔍 Connected to MongoDB successfully!")
        print("=" * 60)
        
        # List all collections
        collections = db.list_collection_names()
        print(f"Collections in database '{DB_NAME}':")
        for collection_name in collections:
            print(f"  📁 {collection_name}")
        
        print("\n" + "=" * 60)
        
        # Check each collection
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"\n📊 Collection: {collection_name}")
            print(f"  Total documents: {count}")
            
            if count > 0:
                # Show first document structure
                first_doc = collection.find_one()
                if first_doc:
                    print(f"  First document keys: {list(first_doc.keys())}")
                    
                    # Check for image-related fields
                    image_fields = [key for key in first_doc.keys() if 'image' in key.lower() or 'photo' in key.lower()]
                    if image_fields:
                        print(f"  Image-related fields: {image_fields}")
                        for field in image_fields:
                            value = first_doc.get(field)
                            if value:
                                print(f"    {field}: {value}")
        
        client.close()
        print("\n🔌 Database connection closed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔍 Database Structure Check")
    print("=" * 60)
    check_database()
    print("=" * 60)
    print("✅ Database check completed!")
