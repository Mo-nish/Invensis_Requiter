#!/usr/bin/env python3
"""
Check SQLite database for image path issues
"""

import sqlite3
import os

def check_sqlite_database():
    """Check SQLite database for image path issues"""
    try:
        # Connect to SQLite database
        db_path = 'instance/hiring_tool.db'
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Connected to SQLite database successfully!")
        print("=" * 60)
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tables in database:")
        for table in tables:
            print(f"  📁 {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Check candidates table
        if ('candidate',) in tables:
            print("\n📊 Checking candidates table...")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(candidate);")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Count candidates
            cursor.execute("SELECT COUNT(*) FROM candidate;")
            count = cursor.fetchone()[0]
            print(f"\nTotal candidates: {count}")
            
            if count > 0:
                # Check for candidates with image paths
                cursor.execute("SELECT id, name, image_path FROM candidate WHERE image_path IS NOT NULL AND image_path != '';")
                candidates_with_images = cursor.fetchall()
                
                print(f"\nCandidates with images: {len(candidates_with_images)}")
                
                for candidate in candidates_with_images:
                    candidate_id, name, image_path = candidate
                    print(f"\n👤 Candidate ID: {candidate_id}, Name: {name}")
                    print(f"  📷 Image path: {image_path}")
                    
                    # Check if path is correct
                    if image_path and image_path.startswith('static/uploads/'):
                        print("  ❌ INCORRECT: Path starts with 'static/uploads/'")
                        
                        # Fix the path
                        new_path = image_path.replace('static/uploads/', 'uploads/')
                        print(f"  🔧 Should be: {new_path}")
                        
                        # Update database
                        cursor.execute("UPDATE candidate SET image_path = ? WHERE id = ?", (new_path, candidate_id))
                        print("  ✅ Database updated")
                        
                    elif image_path and image_path.startswith('uploads/'):
                        print("  ✅ CORRECT: Path starts with 'uploads/'")
                        
                        # Check if file exists
                        full_path = os.path.join('static', image_path)
                        if os.path.exists(full_path):
                            print(f"  ✅ File exists at: {full_path}")
                        else:
                            print(f"  ❌ File missing at: {full_path}")
                    else:
                        print(f"  ⚠️  Unknown path format: {image_path}")
                
                # Commit changes
                conn.commit()
                print(f"\n💾 Database changes committed")
        
        # Check users table
        if ('user',) in tables:
            print("\n📊 Checking users table...")
            cursor.execute("SELECT COUNT(*) FROM user;")
            user_count = cursor.fetchone()[0]
            print(f"Total users: {user_count}")
        
        conn.close()
        print("\n🔌 Database connection closed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 SQLite Database Check")
    print("=" * 60)
    check_sqlite_database()
    print("=" * 60)
    print("✅ Database check completed!")
