#!/usr/bin/env python3
"""
Comprehensive Database Analysis for SceneSplit Application
Analyzes the database connection, schema, and application integration
"""

import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_env_config():
    """Analyze environment configuration"""
    logger.info("🔍 ENVIRONMENT CONFIGURATION ANALYSIS")
    logger.info("=" * 50)
    
    config = {
        'DB_USER': os.getenv("DB_USER"),
        'DB_PASSWORD': '***' if os.getenv("DB_PASSWORD") else None,
        'DB_HOST': os.getenv("DB_HOST", "localhost"),
        'DB_PORT': os.getenv("DB_PORT", "5432"),
        'DB_NAME': os.getenv("DB_NAME"),
        'USE_SQLITE': os.getenv("USE_SQLITE", "false").lower() == "true",
        'DB_ECHO': os.getenv("DB_ECHO", "false").lower() == "true",
        'DB_POOL_SIZE': os.getenv("DB_POOL_SIZE", "10"),
        'DB_MAX_OVERFLOW': os.getenv("DB_MAX_OVERFLOW", "20"),
        'DB_POOL_TIMEOUT': os.getenv("DB_POOL_TIMEOUT", "30"),
        'DB_POOL_RECYCLE': os.getenv("DB_POOL_RECYCLE", "3600")
    }
    
    for key, value in config.items():
        logger.info(f"   {key}: {value}")
    
    # Check if PostgreSQL config is complete
    pg_required = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing = [key for key in pg_required if not os.getenv(key)]
    
    if missing:
        logger.warning(f"⚠️  Missing PostgreSQL config: {missing}")
        return False
    else:
        logger.info("✅ PostgreSQL configuration complete")
        return True

def test_raw_connection():
    """Test raw PostgreSQL connection"""
    logger.info("\n🔌 RAW POSTGRESQL CONNECTION TEST")
    logger.info("=" * 50)
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        cur = conn.cursor()
        
        # Get PostgreSQL version
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        logger.info(f"✅ Connection successful!")
        logger.info(f"📊 PostgreSQL Version: {version}")
        
        # Get current database
        cur.execute("SELECT current_database();")
        current_db = cur.fetchone()[0]
        logger.info(f"📁 Current Database: {current_db}")
        
        # Get current user
        cur.execute("SELECT current_user;")
        current_user = cur.fetchone()[0]
        logger.info(f"👤 Current User: {current_user}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Raw connection failed: {e}")
        return False

def analyze_database_schema():
    """Analyze existing database schema"""
    logger.info("\n📋 DATABASE SCHEMA ANALYSIS")
    logger.info("=" * 50)
    
    try:
        # Create SQLAlchemy engine
        encoded_password = quote_plus(os.getenv("DB_PASSWORD"))
        DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{encoded_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Get all tables
        tables = inspector.get_table_names()
        logger.info(f"📋 Found {len(tables)} tables: {tables}")
        
        # Analyze each table
        for table_name in tables:
            logger.info(f"\n📊 Table: {table_name}")
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            logger.info(f"   Columns ({len(columns)}):")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                logger.info(f"     - {col['name']}: {col['type']} {nullable}{default}")
            
            if indexes:
                logger.info(f"   Indexes ({len(indexes)}):")
                for idx in indexes:
                    unique = "UNIQUE " if idx['unique'] else ""
                    logger.info(f"     - {unique}{idx['name']}: {idx['column_names']}")
            
            if foreign_keys:
                logger.info(f"   Foreign Keys ({len(foreign_keys)}):")
                for fk in foreign_keys:
                    logger.info(f"     - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Get row count
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.fetchone()[0]
                logger.info(f"   Row count: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema analysis failed: {e}")
        return False

def test_application_models():
    """Test application database models"""
    logger.info("\n🏗️  APPLICATION MODELS TEST")
    logger.info("=" * 50)
    
    try:
        # Add backend to path
        sys.path.insert(0, './backend')
        
        # Import application modules
        from database.database import engine, check_database_connection, get_database_info
        from database.models import Base, User, Project, AnalyzedScript
        
        # Test connection using app method
        if check_database_connection():
            logger.info("✅ Application database connection: OK")
        else:
            logger.error("❌ Application database connection: FAILED")
            return False
        
        # Get database info
        db_info = get_database_info()
        if 'error' not in db_info:
            logger.info("📊 Database Info from application:")
            for key, value in db_info.items():
                logger.info(f"   {key}: {value}")
        
        # Check models
        logger.info(f"📋 Registered models: {list(Base.metadata.tables.keys())}")
        
        # Test model creation (if tables don't exist)
        logger.info("🛠️  Testing table creation...")
        Base.metadata.create_all(engine)
        logger.info("✅ Tables created/verified successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Application models test failed: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    logger.info("\n🧪 DATABASE OPERATIONS TEST")
    logger.info("=" * 50)
    
    try:
        sys.path.insert(0, './backend')
        from database.database import get_db, engine
        from database.models import User, Project, AnalyzedScript
        from sqlalchemy.orm import Session
        
        # Test session creation
        db_gen = get_db()
        db: Session = next(db_gen)
        
        try:
            # Test user operations
            logger.info("👤 Testing User operations...")
            
            # Check if test user exists
            existing_user = db.query(User).filter(User.email == "test@scenesplit.com").first()
            if existing_user:
                logger.info("   Test user already exists")
                test_user = existing_user
            else:
                # Create test user
                test_user = User(
                    email="test@scenesplit.com",
                    username="testuser",
                    full_name="Test User",
                    hashed_password="hashed_password_here"
                )
                db.add(test_user)
                db.commit()
                logger.info("   ✅ Test user created")
            
            # Test project operations
            logger.info("📁 Testing Project operations...")
            
            # Check if test project exists
            existing_project = db.query(Project).filter(Project.title == "Test Project").first()
            if existing_project:
                logger.info("   Test project already exists")
                test_project = existing_project
            else:
                # Create test project
                test_project = Project(
                    title="Test Project",
                    description="A test project for database validation",
                    user_id=test_user.id
                )
                db.add(test_project)
                db.commit()
                logger.info("   ✅ Test project created")
            
            # Count records
            user_count = db.query(User).count()
            project_count = db.query(Project).count()
            script_count = db.query(AnalyzedScript).count()
            
            logger.info(f"📊 Record counts:")
            logger.info(f"   Users: {user_count}")
            logger.info(f"   Projects: {project_count}")
            logger.info(f"   Analyzed Scripts: {script_count}")
            
            logger.info("✅ Database operations test completed successfully")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Run comprehensive database analysis"""
    logger.info("🚀 SCENESPLIT DATABASE ANALYSIS")
    logger.info("=" * 60)
    
    results = {
        'env_config': analyze_env_config(),
        'raw_connection': test_raw_connection(),
        'schema_analysis': analyze_database_schema(),
        'app_models': test_application_models(),
        'db_operations': test_database_operations()
    }
    
    logger.info("\n📊 ANALYSIS SUMMARY")
    logger.info("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
    
    overall_success = all(results.values())
    
    if overall_success:
        logger.info("\n🎉 ALL TESTS PASSED! Database is ready for SceneSplit application.")
    else:
        logger.info("\n⚠️  Some tests failed. Check the logs above for details.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
