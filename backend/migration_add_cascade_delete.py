#!/usr/bin/env python3
"""
Migration to add cascade delete to relationships.
This will recreate the foreign key constraints with CASCADE DELETE.
"""

import sqlite3
import os
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent / "instagram_intel.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Start transaction
        conn.execute("BEGIN")
        
        # Drop existing foreign key constraints and recreate with CASCADE DELETE
        # For SQLite, we need to recreate the tables
        
        # 1. Create new tables with CASCADE DELETE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrapes_new (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                scrape_type TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                followers_count INTEGER,
                following_count INTEGER,
                new_followers INTEGER,
                lost_followers INTEGER,
                followers_scraped INTEGER,
                following_scraped INTEGER,
                is_partial BOOLEAN DEFAULT 0,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                job_id TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS followers_new (
                id INTEGER PRIMARY KEY,
                scrape_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                full_name TEXT,
                profile_pic_url TEXT,
                is_verified BOOLEAN DEFAULT 0,
                is_private BOOLEAN DEFAULT 0,
                follower_count INTEGER,
                following_count INTEGER,
                type TEXT NOT NULL,
                status TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (scrape_id) REFERENCES scrapes(id) ON DELETE CASCADE,
                UNIQUE(scrape_id, username, type)
            )
        """)
        
        # 2. Copy data from old tables to new tables
        cursor.execute("""
            INSERT INTO scrapes_new 
            SELECT * FROM scrapes
        """)
        
        cursor.execute("""
            INSERT INTO followers_new 
            SELECT * FROM followers
        """)
        
        # 3. Drop old tables
        cursor.execute("DROP TABLE followers")
        cursor.execute("DROP TABLE scrapes")
        
        # 4. Rename new tables to original names
        cursor.execute("ALTER TABLE scrapes_new RENAME TO scrapes")
        cursor.execute("ALTER TABLE followers_new RENAME TO followers")
        
        # 5. Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_scrapes_account_id ON scrapes(account_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_followers_scrape_id ON followers(scrape_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_followers_username ON followers(username)")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()