#!/usr/bin/env python3
"""Fix database schema by adding missing columns"""

import sqlite3
import sys

def fix_schema():
    """Add missing encrypted_password column to accounts table"""
    try:
        # Connect to database
        conn = sqlite3.connect('/app/data/igcrawl.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'encrypted_password' not in columns:
            print("Adding encrypted_password column to accounts table...")
            cursor.execute("""
                ALTER TABLE accounts 
                ADD COLUMN encrypted_password TEXT DEFAULT NULL
            """)
            conn.commit()
            print("Column added successfully!")
        else:
            print("Column already exists, no action needed.")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error fixing schema: {e}")
        return False

if __name__ == "__main__":
    success = fix_schema()
    sys.exit(0 if success else 1)