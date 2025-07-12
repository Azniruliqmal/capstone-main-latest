from fastapi import FastAPI, HTTPException, UploadFile, Depends, File, Query, Body, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
import os
import tempfile
import time
import asyncio
import logging
import json

from database.database import get_db, create_tables, init_database
from database.services import AnalyzedScriptService, ProjectService, UserService
from database.models import AnalyzedScript, Project, User
from main import run_optimized_script_analysis
from api.serializers import ResultSerializer
from api.validators import (
    FileValidator, 
    AnalyzeScriptResponse, 
    DatabaseScriptResponse,
    ScriptListResponse,
    AnalysisValidator,
    SaveAnalysisRequest,
    SaveAnalysisResponse,
    ChatRequest,
    ChatResponse
)
from .middleware import setup_middleware

load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Script Analysis API",
    version="2.1.0",  # Updated version
    description="Comprehensive film script analysis with AI-powered insights and save compatibility"
)

setup_middleware(app)

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Don't raise here to allow app to start even if DB fails initially

# Main route endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Script Analysis API v2.1 is running",
        "status": "healthy",
        "version": "2.1.0",
        "features": [
            "AI-powered script analysis",
            "Save-compatible response structure",
            "Separate analysis and storage endpoints",
            "Database storage with search",
            "Cost and production breakdowns",
            "RESTful API with validation",
            "Comprehensive error handling"
        ]
    }

# Health endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check with database connectivity"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "script-analysis-api",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.1.0"
    }

# Chat endpoint for AI Assistant
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat endpoint for AI Assistant functionality with real AI responses
    """
    try:
        from datetime import datetime
        from agents.utils.gemini_model import get_model
        from pydantic_ai import Agent
        
        # Build conversation history for context
        conversation_context = ""
        if request.history:
            conversation_context = "\n".join([
                f"{'User' if msg.type == 'user' else 'Assistant'}: {msg.content}" 
                for msg in request.history[-5:]  # Last 5 messages for context
            ])
        
        # System prompt for film-making assistant
        system_prompt = """You are a helpful filmmaking AI assistant. Keep responses SHORT, FRIENDLY, and PRACTICAL.

Key expertise:
- Script analysis & breakdowns
- Film budgeting & cost estimation  
- Production planning & workflows
- Equipment & crew recommendations
- Creative storytelling advice

Response guidelines:
- Keep answers under 2-3 sentences when possible
- Be conversational and encouraging
- Give specific, actionable advice
- Mention budget considerations when relevant

For app features, mention:
- Script upload & AI analysis
- Budget estimation tools
- Project management
- Export reports

Always be concise and helpful!"""

        # Create AI agent with film-making expertise
        model = get_model()
        agent = Agent(model=model, system_prompt=system_prompt)
        
        # Prepare the user's message with context
        user_prompt = f"""
{f"Previous context: {conversation_context}" if conversation_context else ""}

Question: {request.message}

Please give a SHORT, helpful response (1-2 sentences preferred). Be friendly and practical.
"""
        
        # Get AI response
        result = await agent.run(user_prompt)
        ai_response = result.data if hasattr(result, 'data') else str(result)
        
        # Determine appropriate actions based on the content
        actions = []
        user_message_lower = request.message.lower()
        
        if any(word in user_message_lower for word in ['budget', 'cost', 'money', 'expense', 'financing']):
            actions = [
                {"label": "View Budget Breakdown", "action": "navigate_budget"},
                {"label": "Export Budget Report", "action": "export_budget"}
            ]
        elif any(word in user_message_lower for word in ['scene', 'script', 'breakdown', 'analysis', 'character']):
            actions = [
                {"label": "View Script Analysis", "action": "navigate_script"},
                {"label": "Upload New Script", "action": "upload_script"}
            ]
        elif any(word in user_message_lower for word in ['project', 'create', 'new', 'manage']):
            actions = [
                {"label": "Create New Project", "action": "create_project"},
                {"label": "View All Projects", "action": "view_projects"}
            ]
        elif any(word in user_message_lower for word in ['export', 'download', 'report', 'save']):
            actions = [
                {"label": "Export Scene Report", "action": "export_scenes"},
                {"label": "Export Budget Report", "action": "export_budget"}
            ]
        
        response_data = {
            "response": ai_response,
            "actions": actions,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"AI chat response generated for message: {request.message[:50]}...")
        return JSONResponse(status_code=200, content=response_data)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        # Fallback to a helpful error message
        fallback_response = {
            "response": "I'm having trouble connecting to the AI service right now. However, I can still help you navigate this application! You can upload scripts for analysis, view budget breakdowns, manage projects, and export reports. What would you like to do?",
            "actions": [
                {"label": "Upload Script", "action": "upload_script"},
                {"label": "View Projects", "action": "view_projects"},
                {"label": "Help & Guide", "action": "show_guide"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        return JSONResponse(status_code=200, content=fallback_response)

# Analysis endpoint
@app.post("/analyze-script", response_model=AnalyzeScriptResponse)
async def analyze_script(
    file: UploadFile = File(...)
):
    """
    Analyze a script PDF file with save-compatible output structure
    """
    
    # Validate file
    validator = FileValidator()
    validator.validate_file(file)
    
    temp_file_path = None
    file_size = 0
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            file_size = validator.validate_file_size(content)
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        start_time = time.time()
        logger.info(f"Starting save-compatible analysis for {file.filename} ({file_size} bytes)")
        
        # Perform analysis with timeout
        try:
            result = await asyncio.wait_for(
                run_optimized_script_analysis(temp_file_path),
                timeout=300.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=408,
                detail="Analysis timed out. Please try with a smaller script."
            )
        
        processing_time = time.time() - start_time
        logger.info(f"Analysis completed in {processing_time:.2f} seconds")
        
        # ✅ FIXED: Extract comprehensive_analysis correctly
        comprehensive_analysis = result.get('comprehensive_analysis')
        
        if not comprehensive_analysis:
            raise HTTPException(
                status_code=500,
                detail="Analysis completed but no comprehensive analysis data found"
            )
        
        # ✅ FIXED: Convert to dict if it's a Pydantic object
        if hasattr(comprehensive_analysis, 'model_dump'):
            analysis_data = comprehensive_analysis.model_dump()
        elif hasattr(comprehensive_analysis, 'dict'):
            analysis_data = comprehensive_analysis.dict()
        else:
            analysis_data = comprehensive_analysis
        
        # Validate analysis result
        try:
            from agents.states.states import ComprehensiveAnalysis
            # Validate by creating a temporary object if analysis_data is a dict
            if isinstance(analysis_data, dict):
                temp_analysis = ComprehensiveAnalysis(**analysis_data)
            else:
                # If it's already a ComprehensiveAnalysis object, use it directly
                temp_analysis = analysis_data
            logger.info("✅ Analysis validation passed")
        except Exception as validation_error:
            logger.warning(f"Analysis validation warning: {validation_error}")
            # Continue despite validation warnings
        
        # Enhanced metadata
        enhanced_metadata = {
            "filename": file.filename,
            "original_filename": file.filename,
            "file_size_bytes": file_size,
            "processing_time_seconds": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "api_calls_used": result.get('api_calls_used', 2)
        }
        
        # ✅ FIXED: Pre-built save request object with correct structure
        save_request_data = {
            "filename": file.filename,
            "original_filename": file.filename,
            "file_size_bytes": file_size,
            "analysis_data": analysis_data,  # ✅ Use the extracted dict
            "processing_time_seconds": round(processing_time, 2),
            "api_calls_used": result.get('api_calls_used', 2)
        }
        
        # ✅ ENHANCED: Response with correct structure
        response_data = {
            "success": True,
            "message": "Script analysis completed successfully",
            
            # Optimization info
            "optimization_info": {
                "actual_calls_used": result.get('api_calls_used', 2),
                "expected_calls": 2
            },
            
            # Enhanced metadata
            "metadata": enhanced_metadata,
            
            # ✅ FIXED: Both keys point to the same correct data
            "data": analysis_data,           # Backward compatibility
            "analysis_data": analysis_data,  # Save endpoint compatibility
            
            # ✅ FIXED: Ready-to-use save request object
            "save_request": save_request_data
        }
        
        logger.info("✅ Analysis completed with save-compatible structure")
        logger.info(f"Analysis data keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        
        return JSONResponse(status_code=200, content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        error_message = str(e)
        
        if "extract" in error_message.lower():
            raise HTTPException(status_code=422, detail=f"PDF extraction failed: {error_message}")
        elif "validation" in error_message.lower():
            raise HTTPException(status_code=422, detail=f"Script validation failed: {error_message}")
        elif "analysis" in error_message.lower():
            raise HTTPException(status_code=500, detail=f"Analysis failed: {error_message}")
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {error_message}")
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")

# Save analyzed script to DB endpoint
@app.post("/save-analysis", response_model=SaveAnalysisResponse)
async def save_analysis_to_database(
    request: SaveAnalysisRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Saving analysis for {request.filename} to database")
        
        # Enhanced validation of analysis data
        try:
            from agents.states.states import ComprehensiveAnalysis
            temp_analysis = ComprehensiveAnalysis(**request.analysis_data)  # ✅ FIXED
            AnalysisValidator.validate_comprehensive_analysis(temp_analysis)
            logger.info("Analysis data validation passed")
        except Exception as validation_error:
            logger.warning(f"Analysis validation warning: {validation_error}")
            # Continue with save despite validation warnings
        
        # Save to database
        saved_script = AnalyzedScriptService.create_analyzed_script(
            db=db,
            filename=request.filename,
            original_filename=request.original_filename or request.filename,
            file_size_bytes=request.file_size_bytes,
            analysis_data=request.analysis_data,  # ✅ FIXED: Direct assignment
            processing_time=request.processing_time_seconds,
            api_calls_used=request.api_calls_used
        )
        
        response_data = {
            "success": True,
            "message": "Analysis saved to database successfully",
            "database_id": saved_script.id,
            "saved_at": saved_script.created_at.isoformat(),
            "metadata": {
                "filename": saved_script.filename,
                "original_filename": saved_script.original_filename,
                "file_size_bytes": saved_script.file_size_bytes,
                "processing_time_seconds": saved_script.processing_time_seconds,
                "api_calls_used": saved_script.api_calls_used,
                "status": saved_script.status,
                "total_scenes": saved_script.total_scenes,
                "estimated_budget": saved_script.estimated_budget,
                "budget_category": saved_script.budget_category
            }
        }
        
        logger.info(f"Analysis saved to database with ID: {saved_script.id}")
        return JSONResponse(status_code=201, content=response_data)
        
    except Exception as e:
        logger.error(f"Failed to save analysis: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save analysis to database: {str(e)}"
        )

# Read all analyzed scripts from DB endpoint
@app.get("/analyzed-scripts", response_model=ScriptListResponse)
async def get_all_analyzed_scripts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    order_by: str = Query("created_at", description="Order by field"),
    order_direction: str = Query("desc", description="Order direction (asc/desc)"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term for filename"),
    db: Session = Depends(get_db)
):
    """Get all analyzed scripts with enhanced filtering and search"""
    
    try:
        if search:
            scripts = AnalyzedScriptService.search_scripts(
                db=db, 
                search_term=search, 
                skip=skip, 
                limit=limit
            )
            total_count = len(scripts)
        elif status_filter:
            scripts = AnalyzedScriptService.get_scripts_by_status(
                db=db,
                status=status_filter,
                skip=skip,
                limit=limit
            )
            total_count = AnalyzedScriptService.get_scripts_count(db, status_filter)
        else:
            scripts = AnalyzedScriptService.get_all_analyzed_scripts(
                db=db, 
                skip=skip, 
                limit=limit, 
                order_by=order_by,
                order_direction=order_direction
            )
            total_count = AnalyzedScriptService.get_scripts_count(db)
        
        return {
            "success": True,
            "data": [script.to_summary_dict() for script in scripts],
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "returned": len(scripts),
                "has_more": (skip + len(scripts)) < total_count
            },
            "search_term": search
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scripts: {str(e)}")

# Read analyzed script from DB by ID
@app.get("/analyzed-scripts/{script_id}", response_model=DatabaseScriptResponse)
async def get_analyzed_script(
    script_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific analyzed script by ID"""
    
    try:
        script = AnalyzedScriptService.get_analyzed_script_by_id(db, script_id)
        
        if not script:
            raise HTTPException(status_code=404, detail="Analyzed script not found")
        
        return {
            "success": True,
            "data": script.to_dict(),
            "message": "Script retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve script: {str(e)}")

# Delete analyzed script from DB by ID
@app.delete("/analyzed-scripts/{script_id}", response_model=DatabaseScriptResponse)
async def delete_analyzed_script(
    script_id: str,
    db: Session = Depends(get_db)
):
    """Delete an analyzed script by ID"""
    
    try:
        deleted = AnalyzedScriptService.delete_analyzed_script(db, script_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Analyzed script not found")
        
        return {
            "success": True,
            "message": f"Analyzed script {script_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete script: {str(e)}")
    


# Manual human-in-the-loop
from .validators import HumanFeedbackRequest, HumanFeedbackResponse

@app.post("/provide-feedback/{script_id}", response_model=HumanFeedbackResponse)
async def provide_human_feedback(
    script_id: str,
    feedback: HumanFeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Provide human feedback for a specific analysis
    This can trigger re-analysis if needed
    """
    try:
        # Get the script from database
        script = AnalyzedScriptService.get_analyzed_script_by_id(db, script_id)
        
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # If feedback indicates issues and re-analysis is requested
        if not feedback.approved and feedback.request_reanalysis:
            logger.info(f"Re-analysis requested for script {script_id}")
            
            # Create workflow state from stored data
            workflow_state = {
                "pdf_path": f"temp_reanalysis_{script_id}",  # You'd need to handle file storage
                "comprehensive_analysis": script.to_dict(),
                "human_feedback_provided": True,
                "feedback_text": feedback.feedback_text,
                "feedback_approved": feedback.approved,
                "force_human_review": False,
                "status": "reanalysis_requested"
            }
            
            # Run workflow again (optional - only if you want automatic re-analysis)
            # workflow = create_workflow()
            # updated_result = await workflow.ainvoke(workflow_state)
            
            # Update database record
            setattr(script, 'status', "pending_revision")
            setattr(script, 'error_message', f"Human feedback: {feedback.feedback_text}")
            db.commit()
            
            return {
                "success": True,
                "message": "Feedback received. Re-analysis can be triggered manually.",
                "script_id": script_id,
                "feedback_processed": True,
                "action_taken": "marked_for_revision",
                "status": "pending_revision"
            }
        
        else:
            # Just record the feedback
            setattr(script, 'status', "completed_with_feedback" if feedback.approved else "needs_attention")
            if feedback.feedback_text:
                existing_error = script.error_message or ""
                setattr(script, 'error_message', f"{existing_error}\nHuman feedback: {feedback.feedback_text}".strip())
            
            db.commit()
            
            return {
                "success": True,
                "message": "Feedback recorded successfully",
                "script_id": script_id,
                "feedback_processed": True,
                "action_taken": "feedback_recorded",
                "status": script.status
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process feedback for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

# Helper function while waiting for human_feedback
@app.get("/scripts-awaiting-feedback", response_model=ScriptListResponse)
async def get_scripts_awaiting_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get scripts that are awaiting human feedback"""
    
    try:
        scripts = AnalyzedScriptService.get_scripts_by_status(
            db=db,
            status="awaiting_human_feedback",
            skip=skip,
            limit=limit
        )
        
        total_count = AnalyzedScriptService.get_scripts_count(db, "awaiting_human_feedback")
        
        return {
            "success": True,
            "data": [script.to_summary_dict() for script in scripts],
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "returned": len(scripts),
                "has_more": (skip + len(scripts)) < total_count
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve scripts awaiting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scripts: {str(e)}")

# =============================================
# PROJECT MANAGEMENT ENDPOINTS
# =============================================

# Pydantic models for request/response
class CreateProjectRequest(BaseModel):
    title: str
    description: Optional[str] = None

class UpdateProjectRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    budget_total: Optional[float] = None
    estimated_duration_days: Optional[int] = None

class ProjectResponse(BaseModel):
    success: bool
    project: Dict[str, Any]
    message: str

class ProjectListResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    pagination: Dict[str, Any]

# Authentication models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    access_token: str
    user: Dict[str, Any]

# =============================================
# AUTHENTICATION ENDPOINTS
# =============================================

@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    try:
        user = UserService.authenticate_user(db, request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate simple token (in production, use proper JWT)
        token = f"token_{user.id}_{int(time.time())}"
        
        return {
            "success": True,
            "access_token": token,
            "user": user.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """User registration endpoint"""
    try:
        # Check if user exists
        existing_user = UserService.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user = UserService.create_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name
        )
        
        # Generate simple token
        token = f"token_{user.id}_{int(time.time())}"
        
        return {
            "success": True,
            "access_token": token,
            "user": user.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.get("/auth/profile")
async def get_profile():
    """Get user profile (simplified)"""
    # In production, extract user from JWT token
    return {
        "success": True,
        "user": {
            "id": "demo_user",
            "email": "demo@example.com",
            "username": "demo_user",
            "full_name": "Demo User"
        }
    }

# =============================================
# PROJECT ENDPOINTS
# =============================================

@app.post("/create-project-with-script", response_model=ProjectResponse)
async def create_project_with_script(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Create a new project with script analysis"""
    try:
        # Create project
        project = ProjectService.create_project(
            db=db,
            title=title,
            description=description
        )
        
        # Analyze script
        validator = FileValidator()
        validator.validate_file(file)
        
        temp_file_path = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Run analysis
            result = await run_optimized_script_analysis(temp_file_path)
            
            # Extract analysis data
            comprehensive_analysis = result.get('comprehensive_analysis')
            if comprehensive_analysis:
                if hasattr(comprehensive_analysis, 'model_dump'):
                    analysis_data = comprehensive_analysis.model_dump()
                elif hasattr(comprehensive_analysis, 'dict'):
                    analysis_data = comprehensive_analysis.dict()
                else:
                    analysis_data = comprehensive_analysis
            else:
                analysis_data = {}
            
            # Save analysis linked to project
            script = AnalyzedScriptService.create_analyzed_script(
                db=db,
                filename=file.filename or "unknown.pdf",
                original_filename=file.filename or "unknown.pdf",
                file_size_bytes=len(content),
                analysis_data=analysis_data if isinstance(analysis_data, dict) else analysis_data.__dict__,
                processing_time=result.get('total_processing_time'),
                api_calls_used=result.get('api_calls_used') or 2,
                project_id=str(project.id)
            )
            
            # Update project with script info
            ProjectService.update_project(
                db=db,
                project_id=str(project.id),
                script_filename=file.filename or "unknown.pdf",
                budget_total=script.estimated_budget,
                estimated_duration_days=30  # Default estimate
            )
            
            # Refresh project to get updated data
            updated_project = ProjectService.get_project_by_id(db, str(project.id))
            
            return {
                "success": True,
                "project": updated_project.to_dict() if updated_project else project.to_dict(),
                "message": "Project created and script analyzed successfully"
            }
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")

@app.get("/projects/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all projects"""
    try:
        projects = ProjectService.get_projects(db=db, skip=skip, limit=limit)
        total = ProjectService.get_projects_count(db)
        
        # Convert projects to dict and add demo scriptBreakdown if missing
        project_data = []
        for project in projects:
            project_dict = project.to_dict()
            
            # If project doesn't have scriptBreakdown, add demo data
            if 'scriptBreakdown' not in project_dict or not project_dict['scriptBreakdown']:
                project_dict['scriptBreakdown'] = {
                    "scenes": [
                        {
                            "number": 1,
                            "heading": f"EXT. LOCATION - DAY",
                            "location": "Demo Location",
                            "time": "DAY",
                            "characters": ["CHARACTER A", "CHARACTER B"],
                            "props": ["Prop 1", "Prop 2"],
                            "wardrobe": ["Costume 1", "Costume 2"],
                            "sfx": ["Sound 1", "Sound 2"],
                            "notes": f"Demo scene for {project.title}",
                            "budget": "Medium",
                            "dialogues": [
                                "CHARACTER A: This is a demo dialogue.",
                                "CHARACTER B: This is another demo dialogue."
                            ],
                            "estimatedDuration": "2-3 minutes"
                        },
                        {
                            "number": 2,
                            "heading": f"INT. INTERIOR - NIGHT",
                            "location": "Demo Interior",
                            "time": "NIGHT",
                            "characters": ["CHARACTER A", "CHARACTER C"],
                            "props": ["Interior Prop 1", "Interior Prop 2"],
                            "wardrobe": ["Night Costume 1", "Night Costume 2"],
                            "sfx": ["Night Sound 1", "Night Sound 2"],
                            "notes": f"Second demo scene for {project.title}",
                            "budget": "Low",
                            "dialogues": [
                                "CHARACTER A: We need to find the solution.",
                                "CHARACTER C: I think I know what we need to do."
                            ],
                            "estimatedDuration": "3-4 minutes"
                        }
                    ]
                }
            
            project_data.append(project_dict)
        
        # If no projects in database, return demo data
        if not projects or len(projects) == 0:
            demo_projects = [
                {
                    "id": "demo-1",
                    "title": "The Last Guardian",
                    "description": "An epic fantasy adventure film about a mystical guardian protecting an ancient kingdom.",
                    "status": "active",
                    "user_id": "demo-user",
                    "budget_total": 2500000,
                    "estimated_duration_days": 90,
                    "script_filename": "the_last_guardian.pdf",
                    "created_at": "2024-01-15T00:00:00Z",
                    "updated_at": "2024-12-20T00:00:00Z",
                    "scripts_count": 1,
                    "scriptBreakdown": {
                        "scenes": [
                            {
                                "number": 1,
                                "heading": "EXT. ANCIENT FOREST - DAY",
                                "location": "Ancient Forest",
                                "time": "DAY",
                                "characters": ["LYRA", "GUARDIAN SPIRIT"],
                                "props": ["Ancient sword", "Mystical crystal", "Ancient tome"],
                                "wardrobe": ["Warrior armor", "Mystical robes"],
                                "sfx": ["Wind sounds", "Mystical energy"],
                                "notes": "Opening scene where Lyra discovers the ancient guardian spirit in the sacred forest.",
                                "budget": "High",
                                "dialogues": [
                                    "LYRA: I can feel the ancient power calling to me.",
                                    "GUARDIAN SPIRIT: You have been chosen, young warrior.",
                                    "LYRA: But I am not ready for this responsibility.",
                                    "GUARDIAN SPIRIT: Readiness comes through trials, not through waiting."
                                ],
                                "estimatedDuration": "3-4 minutes"
                            },
                            {
                                "number": 2,
                                "heading": "INT. LYRA'S COTTAGE - NIGHT",
                                "location": "Cottage", 
                                "time": "NIGHT",
                                "characters": ["LYRA", "ELDER WOMAN"],
                                "props": ["Fireplace", "Old books", "Healing herbs"],
                                "wardrobe": ["Simple dress", "Elder robes"],
                                "sfx": ["Fire crackling", "Night sounds"],
                                "notes": "Lyra returns home to seek wisdom from the village elder.",
                                "budget": "Medium",
                                "dialogues": [
                                    "ELDER WOMAN: The spirits have spoken to you, haven't they?",
                                    "LYRA: How did you know?",
                                    "ELDER WOMAN: I have seen the signs. The kingdom needs its guardian.",
                                    "LYRA: I don't know if I can fulfill this destiny."
                                ],
                                "estimatedDuration": "2-3 minutes"
                            }
                        ]
                    }
                }
            ]
            
            return {
                "success": True,
                "data": demo_projects,
                "pagination": {
                    "skip": 0,
                    "limit": len(demo_projects),
                    "total": len(demo_projects),
                    "has_more": False
                }
            }
        
        return {
            "success": True,
            "data": project_data,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": (skip + limit) < total
            }
        }
    except Exception as e:
        logger.error(f"Failed to retrieve projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get a specific project"""
    try:
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "project": project.to_dict(),
            "message": "Project retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")

@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: Session = Depends(get_db)
):
    """Update a project with flexible fields"""
    try:
        # Convert request to dict and filter out None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")
        
        project = ProjectService.update_project(
            db=db,
            project_id=project_id,
            **update_data
        )
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "project": project.to_dict(),
            "message": "Project updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update project")

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete a project"""
    try:
        success = ProjectService.delete_project(db, project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "message": "Project deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

@app.get("/projects/{project_id}/analysis")
async def get_project_analysis(project_id: str, db: Session = Depends(get_db)):
    """Get project analysis data"""
    try:
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get the latest script analysis for this project
        scripts = project.analyzed_scripts
        if not scripts:
            raise HTTPException(status_code=404, detail="No analysis found for this project")
        
        # Get the most recent script
        latest_script = scripts[0]  # Assuming they're ordered by creation date
        
        return {
            "success": True,
            "analysis": latest_script.to_dict(),
            "message": "Analysis retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")

# =============================================
# ALTERNATIVE SCRIPT ANALYSIS ENDPOINTS
# =============================================

@app.post("/analyze-script-file")
async def analyze_script_file(file: UploadFile = File(...)):
    """Alternative endpoint for script file analysis (frontend compatibility)"""
    # This redirects to the main analyze-script endpoint
    return await analyze_script(file)

@app.post("/analyze-script-text")
async def analyze_script_text(request: Dict[str, str] = Body(...)):
    """Analyze script from text content"""
    # This is a placeholder - in production, you'd handle text analysis
    return {
        "success": False,
        "message": "Text analysis not implemented yet. Please use file upload.",
        "error": "TEXT_ANALYSIS_NOT_IMPLEMENTED"
    }

# =============================================
# SCRIPTS ENDPOINTS
# =============================================

@app.get("/scripts/", response_model=ScriptListResponse)
async def get_analyzed_scripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all analyzed scripts"""
    try:
        scripts = AnalyzedScriptService.get_analyzed_scripts(db=db, skip=skip, limit=limit)
        total = AnalyzedScriptService.get_analyzed_scripts_count(db)
        
        return {
            "success": True,
            "data": [script.to_dict() for script in scripts],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": (skip + limit) < total
            }
        }
    except Exception as e:
        logger.error(f"Failed to retrieve analyzed scripts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analyzed scripts")

@app.get("/scripts/{script_id}")
async def get_analyzed_script(script_id: str, db: Session = Depends(get_db)):
    """Get a specific analyzed script"""
    try:
        script = AnalyzedScriptService.get_analyzed_script_by_id(db, script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        return {
            "success": True,
            "script": script.to_dict(),
            "message": "Script retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve script: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve script")