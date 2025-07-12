### Important
* **Create env file**
```
.env

# LLM Configuration
GEMINI_KEY=
MODEL_CHOICE=gemini-2.0-flash

# Database Configuration
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

# Database Pool Settings (optional)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_ECHO=true

# MongoDB
MONGODB_ATLAS_CLUSTER_URI=
MONGODB_DB_NAME=
MONGODB_COLLECTION_NAME=
```
* **Create postgresql DB**
```
<!-- run pgadmin 4 -->
```
* **Create Mongo DB**
```
python mongoDB.create_vectorDB.py
python mongoDB.add_to_vectorDB.py
```
---
### How to test run
* **Create venv**
```
python -m venv myvenv
```
* **Activate venv**
```
myvenv\Scripts\activate
```
* **Install dependencies**
```
pip install -r requirements.txt
```
* **Run endpoint**
```
uvicorn api.api:app --reload
```
* **Run streamlit**
```
streamlit run streamlit_app.py  (analyze and save)
streamlit run streamlit_app2.py (analyze,save and monitor)
streamlit run streamlit_app3.py (analyze,save,monitor and human-in-the-loop)
```
---
### Backend Folder Structure
```
📁 backend
│
├── 🤖 AGENTS/
│   ├── agent/
│   │   └── analyst_agent.py          # 🧠 Main AI agent that analyzes scripts
│   ├── states/
│   │   └── states.py                 # 📋 Data structures for analysis results
│   ├── tools/
│   │   └── pdf_extractor.py          # 📄 Extracts text from PDF files
│   └── utils/
│       └── gemini_model.py           # 🔧 Google Gemini AI model setup
│
├── 🌐 API/
│   ├── api.py                        # 🚀 Main FastAPI server & endpoints
│   ├── middleware.py                 # 🛡️ CORS & security settings
│   ├── serializers.py                # 🔄 Converts data for API/database
│   └── validators.py                 # ✅ Validates incoming requests
│
├── 🗄️ DATABASE/
│   ├── database.py                   # 🔌 PostgreSQL connection setup
│   ├── models.py                     # 📊 Database table definitions
│   └── services.py                   # 💾 Database operations (CRUD)
│
├── 🔄 GRAPH/
│   ├── nodes.py                      # 🎯 Individual workflow steps
│   ├── states.py                     # 📝 Workflow state management
│   └── workflow.py                   # 🔀 Orchestrates analysis flow
│
└── 🏠 main.py                        # 🎬 Entry point & workflow execution
```
---