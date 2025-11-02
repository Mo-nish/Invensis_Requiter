#!/usr/bin/env python3
"""
Check the invensis_hiring MongoDB database for any data
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "invensis_hiring"

def check_database():
    """Check the invensis_hiring database"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        print("🔍 Connected to MongoDB successfully!")
        print("=" * 60)
        print(f"Database: {DB_NAME}")
        
        # List all collections
        collections = db.list_collection_names()
        print(f"\nCollections in database:")
        for collection_name in collections:
            print(f"  📁 {collection_name}")
        
        if not collections:
            print("  ❌ No collections found!")
            return
        
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
                    
                    # Show some sample data
                    if collection_name == 'candidates':
                        print(f"  Sample candidate data:")
                        for key, value in list(first_doc.items())[:5]:  # Show first 5 fields
                            print(f"    {key}: {value}")
                    
                    elif collection_name == 'users':
                        print(f"  Sample user data:")
                        for key, value in list(first_doc.items())[:5]:  # Show first 5 fields
                            print(f"    {key}: {value}")
        
        client.close()
        print("\n🔌 Database connection closed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 MongoDB Database Check")
    print("=" * 60)
    check_database()
    print("=" * 60)
    print("✅ Database check completed!")
