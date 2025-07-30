from fastapi import FastAPI, HTTPException, UploadFile, Depends, File, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import desc
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
from agents.agent.chatbot_agent import chatbot_agent

from database.database import get_db, create_tables
from database.services import AnalyzedScriptService
from database.models import AnalyzedScript
from main import run_optimized_script_analysis
from .serializers import ResultSerializer
from .validators import (
    FileValidator, 
    AnalyzeScriptResponse, 
    DatabaseScriptResponse,
    ScriptListResponse,
    AnalysisValidator,
    SaveAnalysisRequest,
    SaveAnalysisResponse,
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
        db.execute("SELECT 1")
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
            # Validate by creating a temporary object
            temp_analysis = ComprehensiveAnalysis(**analysis_data)
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

            data_to_return = {
            "success": True,
            "data": [
                {**s, 'filename': s['filename'].split('.')[0]} 
                for s in (script.to_summary_dict() for script in scripts)
                     ],
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "returned": len(scripts),
                "has_more": (skip + len(scripts)) < total_count
            },
            "search_term": search
        }
            
          #  print(data_to_return['data'][0]['filename'].split('.')[0])
        
        # update_data = data_to_return['data'][0]['filename'].split('.')[0]
        return data_to_return
        
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

# Update analyzed script status
@app.put("/analyzed-scripts/{script_id}", response_model=DatabaseScriptResponse)
async def update_analyzed_script(
    script_id: str,
    request: dict,
    db: Session = Depends(get_db)
):
    """Update an analyzed script (primarily for status changes)"""
    
    try:
        # Get the current script
        script = AnalyzedScriptService.get_analyzed_script_by_id(db, script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Analyzed script not found")
        
        # Extract allowed update fields
        allowed_fields = ['status', 'title', 'description']
        update_data = {}
        
        for field in allowed_fields:
            if field in request:
                if field == 'status':
                    # Map frontend status to backend status
                    frontend_status = request[field].upper()
                    backend_status_map = {
                        'ACTIVE': 'pending_review',
                        'REVIEW': 'pending_review', 
                        'COMPLETED': 'completed',
                        'ERROR': 'error'
                    }
                    update_data['status'] = backend_status_map.get(frontend_status, 'pending_review')
                elif field == 'title':
                    # Update filename for title changes
                    update_data['filename'] = request[field]
                # Note: description is not stored in AnalyzedScript model
        
        # Update the script
        updated_script = AnalyzedScriptService.update_analyzed_script(db, script_id, **update_data)
        
        if not updated_script:
            raise HTTPException(status_code=404, detail="Failed to update script")
        
        return {
            "success": True,
            "message": f"Script {script_id} updated successfully",
            "data": updated_script.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update script: {str(e)}")


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
            script.status = "pending_revision"
            script.error_message = f"Human feedback: {feedback.feedback_text}"
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
            script.status = "completed_with_feedback" if feedback.approved else "needs_attention"
            if feedback.feedback_text:
                existing_error = script.error_message or ""
                script.error_message = f"{existing_error}\nHuman feedback: {feedback.feedback_text}".strip()
            
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
    
class ChatRequest(BaseModel):
    message: str

async def llm_based_fallback_response(user_message: str, script_data: dict, script_title: str) -> str:
    """Use LLM to analyze script data and provide intelligent responses"""
    try:
        # Import a simple LLM model for fallback
        from agents.utils.gemini_model import get_model
        from pydantic_ai import Agent
        
        # Extract scene data for analysis
        scenes_data = []
        if script_data and isinstance(script_data, dict):
            # Try different paths to find scenes
            if 'script_data' in script_data and 'scenes' in script_data['script_data']:
                scenes_data = script_data['script_data']['scenes']
            elif 'scenes' in script_data:
                scenes_data = script_data['scenes']
            elif 'script_breakdown' in script_data:
                scenes_data = script_data['script_breakdown'].get('scenes', [])
        
        # Count unique characters if this is a character-related question
        character_count = 0
        unique_characters = set()
        if scenes_data and ('cast' in user_message.lower() or 'character' in user_message.lower() or 'how many' in user_message.lower()):
            for scene in scenes_data:
                characters = scene.get('characters_present', scene.get('characters', []))
                if characters:
                    unique_characters.update(characters)
            character_count = len(unique_characters)
        
        # Create a specialized analysis agent
        analysis_prompt = f"""
You are a script analysis expert. You have been given complete script analysis data for '{script_title}' and need to answer the user's question by carefully analyzing the provided data.

IMPORTANT: You must read through and analyze the actual scene breakdown data provided to answer questions accurately.

The user asked: "{user_message}"

Script Analysis Summary:
- Script Title: {script_title}
- Number of scenes: {len(scenes_data)}
- Number of unique characters found: {character_count}
- Unique characters: {list(unique_characters) if unique_characters else 'None found'}

Here is the complete script analysis data:
{json.dumps(script_data, indent=2)[:3000]}... (truncated for performance)

Scene breakdown preview (first 3 scenes):
{json.dumps(scenes_data[:3] if scenes_data else [], indent=2)}

Instructions:
1. For character/cast questions: The script has {character_count} unique characters: {list(unique_characters) if unique_characters else 'none found'}
2. For questions about scenes with same locations and characters, analyze each scene's location and character list
3. For budget questions, look at cost breakdown data
4. For location questions, analyze location data from scenes
5. Provide specific, accurate answers based on the actual data
6. Be conversational and helpful

Answer the user's question based on your analysis of this script data. Be specific and reference actual scene numbers, character names, locations, and other data from the analysis.
"""
        
        # Create a simple agent for analysis
        analysis_agent = Agent(
            model=get_model(),
            system_prompt="You are a script analysis expert who carefully analyzes script data to answer user questions accurately."
        )
        
        # Get LLM response
        response = await analysis_agent.run(analysis_prompt)
        
        # Extract response text
        if hasattr(response, 'data'):
            return str(response.data)
        elif hasattr(response, 'content'):
            return str(response.content)
        else:
            return str(response)
            
    except Exception as fallback_error:
        logger.error(f"LLM fallback failed: {str(fallback_error)}")
        
        # Try to give a specific answer for character questions using extracted data
        if character_count > 0 and ('cast' in user_message.lower() or 'character' in user_message.lower() or 'how many' in user_message.lower()):
            return f"Based on the script analysis for '{script_title}', there are {character_count} characters in this script: {', '.join(list(unique_characters))}."
        
        # Only use hardcoded fallback as last resort
        return generate_simple_fallback_response(user_message, script_data, script_title)

def analyze_scenes_with_same_location_and_characters(scenes_data: list, script_title: str) -> str:
    """Analyze scenes that have the same location with the exact same characters"""
    if not scenes_data:
        return f"No scene data available for '{script_title}'"
    
    # Group scenes by location and characters
    location_character_groups = {}
    
    for scene in scenes_data:
        # Get scene info
        scene_num = scene.get("scene_number", scene.get("number", "Unknown"))
        location = scene.get("location", scene.get("scene_location", "Unknown Location"))
        characters = scene.get("characters_present", scene.get("characters", []))
        scene_header = scene.get("scene_header", scene.get("heading", f"Scene {scene_num}"))
        
        # Normalize location and characters for comparison
        location_normalized = location.strip().upper() if location else "UNKNOWN"
        characters_set = frozenset(char.strip().upper() for char in characters if char) if characters else frozenset()
        
        # Create a key combining location and characters
        key = (location_normalized, characters_set)
        
        if key not in location_character_groups:
            location_character_groups[key] = []
        
        location_character_groups[key].append({
            "scene_number": scene_num,
            "scene_header": scene_header,
            "location": location,
            "characters": characters
        })
    
    # Find groups with multiple scenes
    matching_groups = []
    for (location, characters_set), scenes in location_character_groups.items():
        if len(scenes) > 1 and location != "UNKNOWN" and len(characters_set) > 0:
            matching_groups.append({
                "location": location,
                "characters": sorted(list(characters_set)),
                "scenes": scenes,
                "scene_count": len(scenes)
            })
    
    # Generate response
    if not matching_groups:
        return f"In '{script_title}', no scenes share the exact same location with the exact same characters. Each scene appears to have a unique combination of location and cast."
    
    response = f"In '{script_title}', I found {len(matching_groups)} location(s) where multiple scenes involve the same characters:\n\n"
    
    total_matching_scenes = 0
    for group in matching_groups:
        total_matching_scenes += group["scene_count"]
        location_name = group["location"].title() if group["location"] != "UNKNOWN" else "Unknown Location"
        
        response += f"📍 **{location_name}**\n"
        response += f"   Characters: {', '.join(group['characters'])}\n"
        response += f"   Scenes ({group['scene_count']}):\n"
        
        for scene in group["scenes"]:
            response += f"   • Scene {scene['scene_number']}: {scene['scene_header']}\n"
        response += "\n"
    
    response += f"**Summary**: {total_matching_scenes} scenes total involve the same location with the exact same characters across {len(matching_groups)} different location(s)."
    
    return response

def generate_simple_fallback_response(user_message: str, script_data: dict, script_title: str) -> str:
    """Last resort fallback when both main chatbot and LLM fallback fail"""
    return f"I'm experiencing technical difficulties analyzing '{script_title}'. Both my main AI system and backup analysis are currently unavailable. Please try your question again in a moment, or contact support if the issue persists."

@app.post("/chat/{script_id}")
async def chat_about_script(
    script_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat about a specific analyzed script with intelligent conversation capability"""
    
    try:
        logger.info(f"Chat request for script {script_id}: {request.message}")
        
        # Get the script analysis
        script = AnalyzedScriptService.get_analyzed_script_by_id(db, script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # Get full script analysis data
        script_data = script.to_dict()
        logger.info(f"Script data keys: {list(script_data.keys())}")
        
        # Extract the comprehensive analysis from script data
        comprehensive_analysis = script_data.get('comprehensive_analysis') or script_data.get('analysis_data')
        if not comprehensive_analysis:
            logger.warning("No comprehensive analysis found in script data")
            comprehensive_analysis = script_data
        
        # Prepare comprehensive context for chatbot
        context = {
            "script_analysis": script_data,
            "comprehensive_analysis": comprehensive_analysis,
            "user_message": request.message,
            "script_title": script.filename or script.original_filename,
            "script_id": script_id
        }
        
        # Import the helper function
        from agents.agent.chatbot_agent import get_script_analysis_context
        
        # Create a detailed prompt that includes script context and full data
        script_title = script.filename or script.original_filename
        script_context = get_script_analysis_context(comprehensive_analysis)
        
        # Extract scene data for specific analysis
        scenes_data = []
        if comprehensive_analysis and isinstance(comprehensive_analysis, dict):
            # Try different paths to find scenes
            if 'script_data' in comprehensive_analysis and 'scenes' in comprehensive_analysis['script_data']:
                scenes_data = comprehensive_analysis['script_data']['scenes']
            elif 'scenes' in comprehensive_analysis:
                scenes_data = comprehensive_analysis['scenes']
            elif 'script_breakdown' in comprehensive_analysis:
                scenes_data = comprehensive_analysis['script_breakdown'].get('scenes', [])
        
        logger.info(f"Found {len(scenes_data)} scenes for analysis")
        
        prompt = f"""You are chatting with a user about their analyzed script titled "{script_title}".

User's message: {request.message}

Script Analysis Summary:
{script_context}

IMPORTANT: You have access to the complete script analysis data. For specific questions about scenes, characters, locations, or budget, analyze the actual data provided.

Script Details:
- Title: {script_title}
- Number of scenes: {len(scenes_data)}
- Script ID: {script_id}

Scene Data Available: {json.dumps(scenes_data[:3] if scenes_data else [], indent=2)}... (showing first 3 scenes)

Full Analysis Data Available:
{json.dumps(comprehensive_analysis, indent=2)[:2000]}... (truncated for brevity)

Instructions:
1. For questions about cast/characters, count unique characters across all scenes
2. For questions about scenes with same locations and characters, analyze each scene's location and character list  
3. For budget questions, look at cost breakdown data
4. For location questions, analyze location data from scenes
5. Provide specific answers with scene numbers, character names, and other details from the analysis
6. Be conversational and helpful while being accurate to the data

Please provide a helpful response that addresses the user's question using the actual script analysis data."""

        # Get chatbot response with enhanced error handling
        try:
            logger.info("🤖 Calling main chatbot agent...")
            logger.info(f"🤖 User message: {request.message}")
            logger.info(f"🤖 Script context preview: {script_context[:500]}...")
            
            response = await chatbot_agent.run(prompt, deps=context)
            logger.info(f"🤖 Chatbot response type: {type(response)}")
            
            # Extract response text properly
            response_text = ""
            if hasattr(response, 'data'):
                response_text = str(response.data)
            elif hasattr(response, 'content'):
                response_text = str(response.content)
            elif hasattr(response, 'message'):
                response_text = str(response.message)
            else:
                response_text = str(response)
            
            logger.info(f"✅ Main chatbot SUCCESS: {response_text[:200]}...")
            
            return {
                "success": True,
                "response": response_text,
                "script_id": script_id,
                "script_title": script_title
            }
            
        except Exception as agent_error:
            logger.error(f"❌ Main chatbot FAILED: {str(agent_error)}")
            logger.info("🔄 Trying LLM-based fallback...")
            
            # Use LLM-based fallback that actually analyzes the script data
            try:
                fallback_response = await llm_based_fallback_response(request.message, comprehensive_analysis, script_title)
                logger.info(f"✅ LLM fallback SUCCESS: {fallback_response[:200]}...")
                
                return {
                    "success": True,
                    "response": fallback_response,
                    "script_id": script_id,
                    "script_title": script_title,
                    "fallback": True
                }
            except Exception as fallback_error:
                logger.error(f"❌ LLM fallback FAILED: {str(fallback_error)}")
                logger.info("🆘 Using last resort fallback...")
                
                last_resort = generate_simple_fallback_response(request.message, comprehensive_analysis, script_title)
                return {
                    "success": True,
                    "response": last_resort,
                    "script_id": script_id,
                    "script_title": script_title,
                    "last_resort": True
                }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/test-llm")
async def test_llm_connection():
    """Test the LLM connection"""
    try:
        logger.info("Testing LLM connection...")
        
        # Test chatbot agent initialization
        test_prompt = "Say 'Hello, I am your film production assistant!' in a friendly way."
        test_context = {"script_analysis": {"test": "data"}}
        
        response = await chatbot_agent.run(test_prompt, deps=test_context)
        
        response_text = ""
        if hasattr(response, 'data'):
            response_text = str(response.data)
        elif hasattr(response, 'content'):
            response_text = str(response.content)
        else:
            response_text = str(response)
        
        return {
            "success": True,
            "message": "LLM connection successful",
            "test_response": response_text,
            "model_info": str(chatbot_agent.model)
        }
        
    except Exception as e:
        logger.error(f"LLM test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "LLM connection failed"
        }
