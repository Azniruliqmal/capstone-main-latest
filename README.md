# SceneSplit - AI-Powered Film Production Management System

A comprehensive full-stack application for film production management, featuring AI-powered script analysis, intelligent scene breakdown, budget estimation, and production planning tools. Built for filmmakers, producers, and production teams to streamline their workflow from script to screen.

## 🎬 Key Features

### 🤖 AI-Powered Script Analysis
- **Intelligent Script Parsing**: Automatically extracts scenes, characters, locations, and props from scripts
- **Natural Language Processing**: Uses Google Gemini AI for accurate content understanding
- **Multi-Format Support**: Handles PDF, TXT, and FDX script formats
- **Real-time Analysis**: Get instant breakdowns of uploaded scripts

### 📊 Production Management
- **Project Dashboard**: Centralized view of all production projects
- **Scene Navigation**: Interactive scene browser with detailed breakdowns
- **Budget Estimation**: AI-driven budget calculations by category
- **Element Tracking**: Comprehensive tracking of cast, props, and locations

### 💬 AI Assistant
- **Filmmaking Expert**: Get professional advice on production, budgeting, and creative decisions
- **Context-Aware**: Understands your project details for personalized recommendations
- **Interactive Chat**: Ask questions about script analysis, budget planning, or filmmaking best practices

### 📈 Budget Management
- **Category Breakdown**: Visual budget distribution across departments
- **Cost Estimation**: Intelligent cost calculations based on script elements
- **Export Capabilities**: Download detailed budget reports and scene breakdowns

### 🎨 Modern Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Theme**: Professional dark interface optimized for long sessions
- **Smooth Animations**: Polished user experience with fluid transitions

## 🏗️ Architecture

### Backend
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

### Frontend
```
📁 frontend
├── 🎨 src/
│   ├── components/                   # 🧩 Reusable Vue components
│   ├── views/                        # 📄 Main application pages
│   ├── stores/                       # 🗃️ Pinia state management
│   ├── router/                       # 🛣️ Vue Router configuration
│   └── assets/                       # 🖼️ Images, icons, and styles
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **Python** 3.8+ - [Download](https://python.org/)
- **Git** - [Download](https://git-scm.com/)

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Azniruliqmal/Scenesplit-latest2.git
   cd Scenesplit-latest2
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv myvenv
   
   # Activate virtual environment
   # Windows:
   myvenv\Scripts\activate
   # macOS/Linux:
   source myvenv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create environment file
   cp .env.example .env
   # Add your GEMINI_API_KEY to .env file
   
   # Start the backend server
   python main.py
   ```

3. **Frontend Setup** (New Terminal)
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Access the Application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Environment Configuration

Create a `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_CHOICE=gemini-1.5-flash
DATABASE_URL=sqlite:///./script_analysis.db
```

## 📱 How to Use

### 1. Upload a Script
- Click "New Project" to create a new film project
- Upload your script file (PDF, TXT, or FDX format)
- Wait for AI analysis to complete

### 2. Explore Script Breakdown
- Navigate through scenes using the scene browser
- View detailed breakdowns of characters, props, and locations
- Use the "Jump to Scene" dropdown for quick navigation

### 3. Budget Planning
- Review AI-generated budget estimates
- Explore budget breakdown by categories
- Export detailed budget reports

### 4. AI Assistant
- Click the "AI Assistant" button for expert filmmaking advice
- Ask questions about your project, budgeting, or general filmmaking
- Get personalized recommendations based on your script

## 🎯 Demo Projects

The application includes 4 sample projects with complete data:

1. **The Last Guardian** - Fantasy/Adventure (RM 2.5M budget)
2. **Urban Shadows** - Crime/Thriller (RM 1.8M budget)  
3. **Moonlight Serenade** - Romance/Drama (RM 950K budget)
4. **Space Horizon** - Sci-Fi/Adventure (RM 5.2M budget)

## 📊 Key Components

- **Script Analysis**: AI-powered scene breakdown with character, prop, and location extraction
- **Budget Management**: Visual budget tracking with category-wise breakdown
- **Project Dashboard**: Overview of all projects with status tracking
- **Scene Navigation**: Jump to specific scenes with detailed element views

## 🛠️ Technology Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Pinia** - Modern state management for Vue
- **Vite** - Fast build tool and development server
- **Vue Router** - Official router for Vue.js

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Core programming language
- **SQLAlchemy** - SQL toolkit and Object-Relational Mapping
- **SQLite/PostgreSQL** - Database options for data storage
- **Pydantic** - Data validation using Python type annotations

### AI & Machine Learning
- **Google Gemini AI** - Advanced language model for script analysis
- **LangGraph** - Framework for building language agent workflows
- **Pydantic AI** - Type-safe AI agent framework

### Development Tools
- **Git** - Version control system
- **npm/pip** - Package managers
- **ESLint/Prettier** - Code linting and formatting
- **Uvicorn** - ASGI server for FastAPI

## 📊 Demo Projects

Experience the full capabilities with 4 pre-loaded sample projects:

| Project | Genre | Budget | Scenes | Characters |
|---------|--------|--------|---------|------------|
| **The Last Guardian** | Fantasy/Adventure | RM 2.5M | 15+ | 8 |
| **Urban Shadows** | Crime/Thriller | RM 1.8M | 12+ | 6 |
| **Moonlight Serenade** | Romance/Drama | RM 950K | 8+ | 4 |
| **Space Horizon** | Sci-Fi/Adventure | RM 5.2M | 20+ | 10 |

Each demo project includes:
- Complete script breakdown
- Character descriptions and counts
- Location and prop inventories
- Budget estimates by category
- Scene-by-scene analysis

## 🎯 Core Features Deep Dive

### Script Analysis Engine
- **Multi-format parsing**: Supports PDF, TXT, and Final Draft files
- **Intelligent extraction**: Identifies scenes, characters, dialogue, and action lines
- **Location detection**: Automatically categorizes interior/exterior locations
- **Props identification**: Recognizes and catalogs required props and equipment

### Budget Intelligence
- **Category-based estimation**: Breaks down costs by department (Production, Post, Equipment, etc.)
- **Scene-level costing**: Individual scene budget calculations
- **Malaysian film industry rates**: Localized cost estimates for Malaysian productions
- **Export functionality**: Download detailed CSV reports

### AI Assistant Features
- **Filmmaking expertise**: Professional advice on production planning
- **Script consultation**: Guidance on script structure and story development
- **Budget optimization**: Recommendations for cost-effective production
- **Technical support**: Help with equipment and crew requirements

## 🔧 API Endpoints

### Core Endpoints
- `POST /analyze-script-file` - Upload and analyze script files
- `GET /scripts` - Retrieve all analyzed scripts
- `GET /scripts/{id}` - Get specific script analysis
- `POST /chat` - Interact with AI assistant
- `GET /health` - System health check

### Project Management
- `POST /projects` - Create new projects
- `GET /projects` - List all projects
- `PUT /projects/{id}` - Update project details
- `DELETE /projects/{id}` - Remove projects

Full API documentation available at: `http://localhost:8000/docs`

## 🚧 Development

### Project Structure
```
SceneSplit/
├── backend/                 # Python FastAPI backend
│   ├── agents/             # AI analysis agents
│   ├── api/                # API endpoints and middleware
│   ├── database/           # Database models and services
│   ├── graph/              # Workflow orchestration
│   └── main.py             # Application entry point
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Reusable Vue components
│   │   ├── views/          # Page components
│   │   ├── stores/         # Pinia state management
│   │   └── router/         # Vue Router configuration
│   └── public/             # Static assets
└── docs/                   # Documentation files
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/Azniruliqmal/Scenesplit-latest2/issues)
- **Documentation**: Available in the `/docs` folder
- **Email**: Contact the development team for support

## 📄 License

This project is developed as part of an educational capstone project. 

---

**Built with ❤️ for the Malaysian film industry**

*SceneSplit - Empowering filmmakers with intelligent production tools*
