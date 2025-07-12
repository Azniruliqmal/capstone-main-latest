"""
Project management routes for SceneSplit AI
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from database.models import User, Project, ProjectStatus
from database.services import (
    ProjectService, SceneService, CharacterService, 
    LocationService, PropsService, BudgetService
)
from routes.auth import get_current_user
from services.file_service import FileService

router = APIRouter(prefix="/projects", tags=["projects"])

# Request Models
class ProjectCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class SceneCreateRequest(BaseModel):
    scene_number: int
    title: str
    description: Optional[str] = None
    scene_type: str
    location: str
    time_of_day: str
    characters: List[str] = []
    props: List[str] = []

# Response Models
class ProjectResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    status: ProjectStatus
    created_at: str
    updated_at: str
    budget_total: Optional[float]
    estimated_duration_days: Optional[int]

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int

def project_to_dict(project: Project) -> dict:
    """Convert Project model to dictionary"""
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "owner_id": project.owner_id,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "budget_total": project.budget_total,
        "estimated_duration_days": project.estimated_duration_days,
        "script_filename": project.script_filename,
        "collaborators": project.collaborators,
        "tags": project.tags
    }

@router.post("/", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    project = await ProjectService.create_project(
        title=request.title,
        description=request.description,
        owner_id=current_user.id
    )
    
    return ProjectResponse(**project_to_dict(project))

@router.get("/", response_model=ProjectListResponse)
async def get_projects(current_user: User = Depends(get_current_user)):
    """Get user's projects"""
    owned_projects = await ProjectService.get_projects_by_owner(current_user.id)
    collaborated_projects = await ProjectService.get_projects_by_collaborator(current_user.id)
    
    all_projects = owned_projects + collaborated_projects
    # Remove duplicates
    unique_projects = {p.id: p for p in all_projects}.values()
    
    project_list = [ProjectResponse(**project_to_dict(p)) for p in unique_projects]
    
    return ProjectListResponse(
        projects=project_list,
        total=len(project_list)
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project by ID"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to this project
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ProjectResponse(**project_to_dict(project))

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update project"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is owner
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can update project"
        )
    
    # Update project
    update_data = {k: v for k, v in request.dict().items() if v is not None}
    updated_project = await ProjectService.update_project(project_id, **update_data)
    
    return ProjectResponse(**project_to_dict(updated_project))

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete project"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is owner
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete project"
        )
    
    success = await ProjectService.delete_project(project_id)
    
    if success:
        return {"message": "Project deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

@router.post("/{project_id}/upload-script")
async def upload_script(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload script file to project"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Process file upload
        file_service = FileService()
        file_info = await file_service.save_uploaded_file(
            file=file,
            user_id=current_user.id,
            project_id=project_id,
            upload_purpose="script"
        )
        
        # Extract text content
        script_content = await file_service.extract_text_from_file(file_info["file_path"])
        
        # Update project with script content
        await ProjectService.update_project(
            project_id,
            script_content=script_content,
            script_filename=file.filename
        )
        
        return {
            "message": "Script uploaded successfully",
            "file_info": file_info,
            "content_length": len(script_content)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload script: {str(e)}"
        )

@router.get("/{project_id}/scenes")
async def get_project_scenes(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project scenes"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    scenes = await SceneService.get_scenes_by_project(project_id)
    return {"scenes": [scene.dict() for scene in scenes]}

@router.get("/{project_id}/characters")
async def get_project_characters(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project characters"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    characters = await CharacterService.get_characters_by_project(project_id)
    return {"characters": [character.dict() for character in characters]}

@router.get("/{project_id}/budget")
async def get_project_budget(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project budget"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    budget_items = await BudgetService.get_budget_by_project(project_id)
    total_budget = await BudgetService.get_total_budget(project_id)
    
    return {
        "budget_items": [item.dict() for item in budget_items],
        "total_budget": total_budget
    }

@router.get("/{project_id}/analysis")
async def get_project_analysis(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project analysis data"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to this project
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "project_id": project.id,
        "title": project.title,
        "analysis_data": project.analysis_data or {},
        "script_filename": project.script_filename
    }

@router.put("/{project_id}/analysis")
async def update_project_analysis(
    project_id: str,
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update project analysis data"""
    project = await ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to this project
    if project.owner_id != current_user.id and current_user.id not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update analysis data
    updated_project = await ProjectService.update_project(
        project_id, 
        analysis_data=analysis_data
    )
    
    return {
        "message": "Analysis data updated successfully",
        "project_id": project.id,
        "analysis_data": updated_project.analysis_data
    }
