import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_ATLAS_CLUSTER_URI'))
db_name = os.getenv('MONGODB_DB_NAME', 'scenesplit_ai')
collection_name = os.getenv('MONGODB_COLLECTION_NAME', 'cost_collection_pdf')

print("🔍 MongoDB Vector Database Verification")
print("=" * 50)

# List databases
print('📊 Available databases:')
for db in client.list_database_names():
    print(f'  - {db}')

# Check if our database exists
if db_name in client.list_database_names():
    print(f'\n✅ Database "{db_name}" exists!')
    
    # List collections in our database
    db = client[db_name]
    collections = db.list_collection_names()
    print(f'\n📁 Collections in "{db_name}":')
    for collection in collections:
        print(f'  - {collection}')
        
    # Check our specific collection
    if collection_name in collections:
        print(f'\n✅ Collection "{collection_name}" exists!')
        collection = db[collection_name]
        
        # Get collection stats
        try:
            stats = db.command('collStats', collection_name)
            print(f'\n📈 Collection Stats:')
            print(f'  - Document count: {stats.get("count", 0)}')
            print(f'  - Storage size: {stats.get("storageSize", 0)} bytes')
            print(f'  - Indexes: {stats.get("nindexes", 0)}')
        except Exception as e:
            print(f'\n⚠️ Could not get stats: {e}')
        
        # List indexes
        try:
            indexes = list(collection.list_indexes())
            print(f'\n🔍 Indexes:')
            for idx in indexes:
                print(f'  - {idx.get("name", "unnamed")}: {idx.get("key", {})}')
        except Exception as e:
            print(f'\n⚠️ Could not list indexes: {e}')
    else:
        print(f'\n⚠️ Collection "{collection_name}" not found')
else:
    print(f'\n⚠️ Database "{db_name}" not found')

print(f'\n🎯 Vector Database Status: {"✅ READY" if db_name in client.list_database_names() else "❌ NOT READY"}')
client.close()
