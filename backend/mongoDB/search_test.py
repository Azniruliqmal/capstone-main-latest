import os
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Vector Search with Added Documents")
print("=" * 60)

# Initialize components
api_key = os.getenv("GEMINI_KEY")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
DB_NAME = os.getenv("MONGODB_DB_NAME", "scenesplit_ai")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "cost_collection_pdf")
ATLAS_VECTOR_SEARCH_INDEX_NAME = "cost-index-pdf"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

# Initialize vector store
vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)

# Test queries to see what documents were added
test_queries = [
    "cost analysis",
    "budget planning",
    "financial planning",
    "production costs",
    "script analysis"
]

print(f"📊 Collection has {MONGODB_COLLECTION.count_documents({})} documents")

for query in test_queries:
    print(f"\n🔍 Searching for: '{query}'")
    try:
        results = vector_store.similarity_search(query, k=2)
        
        if results:
            for i, doc in enumerate(results):
                print(f"   {i+1}. Content preview: {doc.page_content[:150]}...")
                if hasattr(doc, 'metadata') and doc.metadata:
                    print(f"      Metadata: {doc.metadata}")
        else:
            print("   No results found")
            
    except Exception as e:
        print(f"   Error: {e}")

print(f"\n✅ Vector search testing completed!")
client.close()
