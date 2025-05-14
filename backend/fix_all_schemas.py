#!/usr/bin/env python3
"""Fix all database schemas by adding missing columns"""

import sqlite3
import sys

def fix_all_schemas():
    """Add all missing columns to database tables"""
    try:
        # Connect to database
        conn = sqlite3.connect('/app/data/igcrawl.db')
        cursor = conn.cursor()
        
        # Fix accounts table
        cursor.execute("PRAGMA table_info(accounts)")
        account_columns = [column[1] for column in cursor.fetchall()]
        
        if 'encrypted_password' not in account_columns:
            print("Adding encrypted_password column to accounts table...")
            cursor.execute("""
                ALTER TABLE accounts 
                ADD COLUMN encrypted_password TEXT DEFAULT NULL
            """)
            conn.commit()
            print("accounts table: encrypted_password column added successfully!")
            
        # Fix scrapes table
        cursor.execute("PRAGMA table_info(scrapes)")
        scrape_columns = [column[1] for column in cursor.fetchall()]
        
        columns_to_add = [
            ('followers_scraped', 'INTEGER DEFAULT NULL'),
            ('following_scraped', 'INTEGER DEFAULT NULL'),
            ('is_partial', 'INTEGER DEFAULT 0')  # SQLite uses INTEGER for boolean
        ]
        
        for column_name, column_def in columns_to_add:
            if column_name not in scrape_columns:
                print(f"Adding {column_name} column to scrapes table...")
                cursor.execute(f"""
                    ALTER TABLE scrapes 
                    ADD COLUMN {column_name} {column_def}
                """)
                conn.commit()
                print(f"scrapes table: {column_name} column added successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error fixing schema: {e}")
        return False

if __name__ == "__main__":
    success = fix_all_schemas()
    sys.exit(0 if success else 1)