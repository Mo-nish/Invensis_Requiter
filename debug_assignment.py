#!/usr/bin/env python3
"""
Debug script to test assignment functionality
"""

from models_mongo import candidates_collection, Candidate
from bson import ObjectId

def debug_assignment():
    print("🔍 Debugging Assignment Issue...")
    print("=" * 50)
    
    # Check if there are any candidates in the database
    candidates = list(candidates_collection.find())
    print(f"📊 Total candidates in database: {len(candidates)}")
    
    if candidates:
        print("\n📋 Sample candidates:")
        for i, candidate in enumerate(candidates[:3]):
            print(f"  {i+1}. ID: {candidate['_id']}")
            print(f"     Name: {candidate.get('first_name', 'N/A')} {candidate.get('last_name', 'N/A')}")
            print(f"     Email: {candidate.get('email', 'N/A')}")
            print(f"     Status: {candidate.get('status', 'N/A')}")
            print()
        
        # Test find_by_id with the first candidate
        first_candidate = candidates[0]
        candidate_id = str(first_candidate['_id'])
        
        print(f"🧪 Testing find_by_id with ID: {candidate_id}")
        
        try:
            # Test direct MongoDB query
            direct_result = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
            print(f"✅ Direct MongoDB query: {'Found' if direct_result else 'Not found'}")
            
            # Test Candidate.find_by_id method
            candidate_obj = Candidate.find_by_id(candidate_id)
            print(f"✅ Candidate.find_by_id: {'Found' if candidate_obj else 'Not found'}")
            
            if candidate_obj:
                print(f"   Name: {candidate_obj.first_name} {candidate_obj.last_name}")
                print(f"   Email: {candidate_obj.email}")
                print(f"   Status: {candidate_obj.status}")
                
        except Exception as e:
            print(f"❌ Error testing find_by_id: {e}")
    
    else:
        print("❌ No candidates found in database")
        print("💡 You need to add some candidates first")
    
    print("\n" + "=" * 50)
    print("🔧 Next Steps:")
    print("1. Add some candidates if database is empty")
    print("2. Check the candidate ID being passed to assignment")
    print("3. Verify the ObjectId conversion is working")
    print("4. Test the assignment with a valid candidate ID")

if __name__ == "__main__":
    debug_assignment() 