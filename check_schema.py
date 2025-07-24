import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()

# Check users table
print("USERS TABLE SCHEMA:")
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'users' 
    ORDER BY ordinal_position
""")
for col in cur.fetchall():
    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
    default = f" DEFAULT {col[3]}" if col[3] else ""
    print(f"  {col[0]}: {col[1]} {nullable}{default}")

print("\nPROJECTS TABLE SCHEMA:")
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'projects' 
    ORDER BY ordinal_position
""")
for col in cur.fetchall():
    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
    default = f" DEFAULT {col[3]}" if col[3] else ""
    print(f"  {col[0]}: {col[1]} {nullable}{default}")

print("\nANALYZED_SCRIPTS TABLE SCHEMA:")
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'analyzed_scripts' 
    ORDER BY ordinal_position
""")
for col in cur.fetchall():
    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
    default = f" DEFAULT {col[3]}" if col[3] else ""
    print(f"  {col[0]}: {col[1]} {nullable}{default}")

# Check indexes
print("\nINDEXES:")
cur.execute("""
    SELECT schemaname, tablename, indexname, indexdef 
    FROM pg_indexes 
    WHERE schemaname = 'public'
""")
for idx in cur.fetchall():
    print(f"  {idx[1]}.{idx[2]}: {idx[3]}")

conn.close()
