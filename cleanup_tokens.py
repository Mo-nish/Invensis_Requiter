#!/usr/bin/env python3
"""
Script to clean up all password reset tokens
"""

import pymongo
from datetime import datetime

def cleanup_all_tokens():
    try:
        # Connect to MongoDB using environment variable
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = pymongo.MongoClient(MONGODB_URI)
        db = client['invensis']
        
        # Get all tokens
        tokens = list(db.password_reset_tokens.find())
        print(f"Found {len(tokens)} tokens in database")
        
        if tokens:
            print("\nToken details:")
            for token in tokens:
                print(f"- ID: {token.get('_id')}")
                print(f"  User ID: {token.get('user_id')}")
                print(f"  Token: {token.get('token', 'N/A')[:20]}...")
                print(f"  Expires: {token.get('expires_at')}")
                print(f"  Is Used: {token.get('is_used', False)}")
                print(f"  Created: {token.get('created_at')}")
                print()
        
        # Delete all tokens
        result = db.password_reset_tokens.delete_many({})
        print(f"Deleted {result.deleted_count} tokens")
        
        # Verify deletion
        remaining = list(db.password_reset_tokens.find())
        print(f"Remaining tokens: {len(remaining)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Cleaning up all password reset tokens...")
    success = cleanup_all_tokens()
    if success:
        print("✅ Cleanup completed successfully")
    else:
        print("❌ Cleanup failed")
