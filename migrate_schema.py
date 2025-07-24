#!/usr/bin/env python3
"""
Database Schema Migration Script
Updates the existing PostgreSQL schema to match the current SQLAlchemy models
"""

import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_database():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def check_column_exists(cur, table_name, column_name):
    """Check if a column exists in a table"""
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """, (table_name, column_name))
    return cur.fetchone()[0] > 0

def add_missing_project_columns(cur):
    """Add missing columns to projects table"""
    logger.info("🔧 Updating projects table schema...")
    
    columns_to_add = [
        ("estimated_duration_days", "INTEGER"),
        ("script_filename", "VARCHAR(255)")
    ]
    
    for column_name, column_type in columns_to_add:
        if not check_column_exists(cur, 'projects', column_name):
            sql = f"ALTER TABLE projects ADD COLUMN {column_name} {column_type}"
            cur.execute(sql)
            logger.info(f"   ✅ Added column: {column_name}")
        else:
            logger.info(f"   ⏭️  Column already exists: {column_name}")

def add_missing_script_columns(cur):
    """Add missing columns to analyzed_scripts table"""
    logger.info("🔧 Updating analyzed_scripts table schema...")
    
    columns_to_add = [
        ("cast_breakdown", "JSON"),
        ("cost_breakdown", "JSON"),
        ("location_breakdown", "JSON"),
        ("props_breakdown", "JSON"),
        ("processing_time_seconds", "DOUBLE PRECISION"),
        ("api_calls_used", "INTEGER DEFAULT 2"),
        ("error_message", "TEXT"),
        ("total_scenes", "INTEGER"),
        ("total_characters", "INTEGER"),
        ("total_locations", "INTEGER"),
        ("estimated_budget", "DOUBLE PRECISION"),
        ("budget_category", "VARCHAR(20)")
    ]
    
    for column_name, column_type in columns_to_add:
        if not check_column_exists(cur, 'analyzed_scripts', column_name):
            sql = f"ALTER TABLE analyzed_scripts ADD COLUMN {column_name} {column_type}"
            cur.execute(sql)
            logger.info(f"   ✅ Added column: {column_name}")
        else:
            logger.info(f"   ⏭️  Column already exists: {column_name}")

def add_missing_indexes(cur):
    """Add missing indexes for performance"""
    logger.info("🔧 Adding missing indexes...")
    
    indexes_to_add = [
        ("idx_projects_title", "projects", "title"),
        ("idx_projects_status", "projects", "status"),
        ("idx_projects_created_at", "projects", "created_at"),
        ("idx_analyzed_scripts_filename", "analyzed_scripts", "filename"),
        ("idx_analyzed_scripts_status", "analyzed_scripts", "status"),
        ("idx_analyzed_scripts_project_id", "analyzed_scripts", "project_id")
    ]
    
    for index_name, table_name, column_name in indexes_to_add:
        # Check if index already exists
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE indexname = %s
        """, (index_name,))
        
        if cur.fetchone()[0] == 0:
            sql = f"CREATE INDEX {index_name} ON {table_name} ({column_name})"
            cur.execute(sql)
            logger.info(f"   ✅ Added index: {index_name}")
        else:
            logger.info(f"   ⏭️  Index already exists: {index_name}")

def update_column_defaults(cur):
    """Update column defaults to match models"""
    logger.info("🔧 Updating column defaults...")
    
    # Update users table defaults
    updates = [
        ("users", "is_active", "boolean", "TRUE"),
        ("projects", "status", "varchar(50)", "'active'"),
        ("analyzed_scripts", "status", "varchar(50)", "'completed'"),
        ("analyzed_scripts", "api_calls_used", "integer", "2")
    ]
    
    for table_name, column_name, data_type, default_value in updates:
        if check_column_exists(cur, table_name, column_name):
            try:
                sql = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT {default_value}"
                cur.execute(sql)
                logger.info(f"   ✅ Updated default for {table_name}.{column_name}")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not update default for {table_name}.{column_name}: {e}")

def verify_schema_update(cur):
    """Verify the schema updates were successful"""
    logger.info("✅ Verifying schema updates...")
    
    # Check projects table
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'projects' 
        ORDER BY ordinal_position
    """)
    project_columns = [row[0] for row in cur.fetchall()]
    logger.info(f"   Projects columns: {project_columns}")
    
    # Check analyzed_scripts table
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'analyzed_scripts' 
        ORDER BY ordinal_position
    """)
    script_columns = [row[0] for row in cur.fetchall()]
    logger.info(f"   Analyzed scripts columns: {script_columns}")
    
    # Check indexes
    cur.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        ORDER BY indexname
    """)
    indexes = [row[0] for row in cur.fetchall()]
    logger.info(f"   Indexes: {indexes}")

def main():
    """Main migration function"""
    logger.info("🚀 Starting database schema migration...")
    
    try:
        # Connect to database
        conn = connect_to_database()
        cur = conn.cursor()
        
        try:
            # Perform migrations
            add_missing_project_columns(cur)
            add_missing_script_columns(cur)
            add_missing_indexes(cur)
            update_column_defaults(cur)
            
            # Commit changes
            conn.commit()
            logger.info("💾 All changes committed successfully")
            
            # Verify updates
            verify_schema_update(cur)
            
            logger.info("🎉 Database schema migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Migration failed, rolling back: {e}")
            raise
            
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
