from database.database import get_db, engine
from sqlalchemy import text

# Check if the database file exists and list tables
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = [row[0] for row in result.fetchall()]
    print('Created tables:', tables)
    
    # Check each table's structure
    for table in tables:
        print(f"\nTable: {table}")
        result = conn.execute(text(f"PRAGMA table_info({table});"))
        columns = result.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
