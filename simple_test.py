import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Get credentials from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

print(f"Testing connection to: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

try:
    # Test connection
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    # Test query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ PostgreSQL connection successful!")
    print(f"📊 Version: {version[0]}")
    
    # Check existing tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    
    if tables:
        print(f"📋 Existing tables: {[t[0] for t in tables]}")
    else:
        print("📋 No tables found")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
