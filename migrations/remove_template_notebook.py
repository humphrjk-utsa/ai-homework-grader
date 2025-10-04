#!/usr/bin/env python3
"""
Migration: Remove template_notebook column from assignments table
Since template notebooks are not being used, we're removing them to simplify the system.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database(db_path="grading_database.db"):
    """Remove template_notebook column from assignments table"""
    
    print(f"🔧 Starting migration: Remove template_notebook")
    print(f"📁 Database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if template_notebook column exists
        cursor.execute("PRAGMA table_info(assignments)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'template_notebook' not in column_names:
            print("✅ template_notebook column doesn't exist, nothing to do")
            conn.close()
            return True
        
        print("📋 Current columns:", column_names)
        
        # SQLite doesn't support DROP COLUMN directly, so we need to:
        # 1. Create new table without template_notebook
        # 2. Copy data
        # 3. Drop old table
        # 4. Rename new table
        
        print("🔄 Creating new table structure...")
        cursor.execute("""
            CREATE TABLE assignments_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                total_points INTEGER,
                rubric TEXT,
                solution_notebook TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("📦 Copying data to new table...")
        cursor.execute("""
            INSERT INTO assignments_new (id, name, description, total_points, rubric, solution_notebook, created_date)
            SELECT id, name, description, total_points, rubric, solution_notebook, created_date
            FROM assignments
        """)
        
        print("🗑️  Dropping old table...")
        cursor.execute("DROP TABLE assignments")
        
        print("✏️  Renaming new table...")
        cursor.execute("ALTER TABLE assignments_new RENAME TO assignments")
        
        conn.commit()
        
        # Verify the change
        cursor.execute("PRAGMA table_info(assignments)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        print("✅ New columns:", new_column_names)
        
        # Get count of assignments
        cursor.execute("SELECT COUNT(*) FROM assignments")
        count = cursor.fetchone()[0]
        print(f"✅ Migrated {count} assignments successfully")
        
        conn.close()
        
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def backup_database(db_path="grading_database.db"):
    """Create a backup of the database before migration"""
    if not os.path.exists(db_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Remove template_notebook")
    print("=" * 60)
    
    # Create backup first
    backup_path = backup_database()
    
    if backup_path:
        print(f"✅ Backup created successfully")
    else:
        print("⚠️  No backup created, proceeding anyway...")
    
    # Run migration
    success = migrate_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        if backup_path:
            print(f"💾 Backup available at: {backup_path}")
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        if backup_path:
            print(f"💾 Restore from backup: {backup_path}")
