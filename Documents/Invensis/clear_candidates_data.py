"""
Script to clear all candidate data from MongoDB database.
This script will delete:
- All candidates from candidates_collection
- All feedback related to candidates from feedback_collection
- All candidate requests from candidate_requests_collection

WARNING: This action cannot be undone. Make sure you have a backup if needed.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')

def clear_candidates_data():
    """Clear all candidate-related data from the database"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client['invensis']
        
        # Get collections
        candidates_collection = db.candidates
        feedback_collection = db.feedback
        candidate_requests_collection = db.candidate_requests
        
        # Count before deletion
        candidates_count = candidates_collection.count_documents({})
        feedback_count = feedback_collection.count_documents({})
        candidate_requests_count = candidate_requests_collection.count_documents({})
        
        print("=" * 60)
        print("CLEARING CANDIDATE DATA FROM DATABASE")
        print("=" * 60)
        print(f"\nCurrent data counts:")
        print(f"  - Candidates: {candidates_count}")
        print(f"  - Feedback records: {feedback_count}")
        print(f"  - Candidate requests: {candidate_requests_count}")
        print("\n" + "=" * 60)
        
        # Confirm deletion
        confirmation = input("\n⚠️  WARNING: This will delete ALL candidate data. This cannot be undone!\n"
                            "Type 'DELETE ALL CANDIDATES' to confirm: ")
        
        if confirmation != 'DELETE ALL CANDIDATES':
            print("\n❌ Deletion cancelled. No data was deleted.")
            return
        
        print("\n🗑️  Starting deletion process...")
        
        # Delete all candidates
        if candidates_count > 0:
            result = candidates_collection.delete_many({})
            print(f"✅ Deleted {result.deleted_count} candidates")
        else:
            print("ℹ️  No candidates to delete")
        
        # Delete all feedback
        if feedback_count > 0:
            result = feedback_collection.delete_many({})
            print(f"✅ Deleted {result.deleted_count} feedback records")
        else:
            print("ℹ️  No feedback records to delete")
        
        # Delete all candidate requests
        if candidate_requests_count > 0:
            result = candidate_requests_collection.delete_many({})
            print(f"✅ Deleted {result.deleted_count} candidate requests")
        else:
            print("ℹ️  No candidate requests to delete")
        
        # Verify deletion
        remaining_candidates = candidates_collection.count_documents({})
        remaining_feedback = feedback_collection.count_documents({})
        remaining_requests = candidate_requests_collection.count_documents({})
        
        print("\n" + "=" * 60)
        print("DELETION COMPLETE")
        print("=" * 60)
        print(f"\nRemaining data counts:")
        print(f"  - Candidates: {remaining_candidates}")
        print(f"  - Feedback records: {remaining_feedback}")
        print(f"  - Candidate requests: {remaining_requests}")
        
        if remaining_candidates == 0 and remaining_feedback == 0 and remaining_requests == 0:
            print("\n✅ All candidate data has been successfully cleared!")
        else:
            print("\n⚠️  Some data may still remain. Please check manually.")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("Please check your MongoDB connection and try again.")
        raise

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CANDIDATE DATA CLEARANCE SCRIPT")
    print("=" * 60)
    print("\nThis script will delete:")
    print("  • All candidates")
    print("  • All feedback records")
    print("  • All candidate requests")
    print("\nThis will NOT delete:")
    print("  • Users")
    print("  • Roles")
    print("  • Activity logs")
    print("  • User emails")
    print("  • Password reset tokens")
    print("=" * 60)
    
    try:
        clear_candidates_data()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")

