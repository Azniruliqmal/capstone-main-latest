from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, text
from sqlalchemy.exc import SQLAlchemyError
from database.models import AnalyzedScript, Project, User
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
import logging
import hashlib

logger = logging.getLogger(__name__)

def ensure_users_table(db: Session):
    """Ensure the users table exists with all required columns"""
    try:
        # Check if table exists by trying to query it
        try:
            db.execute(text("SELECT 1 FROM users LIMIT 1")).fetchone()
            logger.info("users table exists")
        except Exception:
            logger.info("Creating users table...")
            
            # Create table with all columns if it doesn't exist
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    full_name VARCHAR(255),
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            db.commit()
            logger.info("users table created successfully")
            
            # Add indexes for better performance
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_email 
                ON users(email);
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_username 
                ON users(username);
            """))
            
            db.commit()
            logger.info("✅ users table created/fixed successfully")
            
    except Exception as e:
        logger.error(f"❌ Error ensuring users table exists: {e}")
        db.rollback()
        raise

def ensure_projects_table(db: Session):
    """Ensure the projects table exists with all required columns"""
    try:
        # Check if table exists by trying to query it
        try:
            db.execute(text("SELECT 1 FROM projects LIMIT 1")).fetchone()
            logger.info("projects table exists")
        except Exception:
            logger.info("Creating projects table...")
            
            # Create table with all columns if it doesn't exist
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS projects (
                    id VARCHAR PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'active',
                    user_id VARCHAR,
                    budget_total FLOAT,
                    estimated_duration_days INTEGER,
                    script_filename VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            db.commit()
            logger.info("projects table created successfully")
            
            # Add indexes for better performance
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_projects_title 
                ON projects(title);
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_projects_status 
                ON projects(status);
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_projects_created_at 
                ON projects(created_at);
            """))
            
            db.commit()
            logger.info("✅ projects table created/fixed successfully")
            
    except Exception as e:
        logger.error(f"❌ Error ensuring projects table exists: {e}")
        db.rollback()
        raise

def ensure_analyzed_scripts_table(db: Session):
    """Ensure the analyzed_scripts table exists with all required columns"""
    try:
        # Check if table exists by trying to query it
        try:
            db.execute(text("SELECT 1 FROM analyzed_scripts LIMIT 1")).fetchone()
            logger.info("analyzed_scripts table exists")
        except Exception:
            logger.info("Creating analyzed_scripts table...")
            
            # Create table with all columns if it doesn't exist
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS analyzed_scripts (
                    id VARCHAR PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255),
                    file_size_bytes INTEGER,
                    script_data JSON,
                    cast_breakdown JSON,
                    cost_breakdown JSON,
                    location_breakdown JSON,
                    props_breakdown JSON,
                    processing_time_seconds FLOAT,
                    api_calls_used INTEGER DEFAULT 2,
                    status VARCHAR(50) DEFAULT 'completed',
                    error_message TEXT,
                    total_scenes INTEGER,
                    total_characters INTEGER,
                    total_locations INTEGER,
                    estimated_budget FLOAT,
                    budget_category VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    project_id VARCHAR
                );
            """))
            
            db.commit()
            logger.info("analyzed_scripts table created successfully")
            
            # Add indexes for better performance
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analyzed_scripts_filename 
                ON analyzed_scripts(filename);
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analyzed_scripts_status 
                ON analyzed_scripts(status);
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analyzed_scripts_created_at 
                ON analyzed_scripts(created_at);
            """))
            
            db.commit()
            logger.info("✅ analyzed_scripts table created/fixed successfully")
            
    except Exception as e:
        logger.error(f"❌ Error ensuring table exists: {e}")
        db.rollback()
        raise

class AnalyzedScriptService:
    
    @staticmethod
    def create_analyzed_script(
        db: Session,
        filename: str,
        original_filename: str,
        file_size_bytes: int,
        analysis_data: Dict[str, Any],
        processing_time: Optional[float] = None,
        api_calls_used: int = 2,
        project_id: Optional[str] = None  # Added project_id parameter
    ) -> AnalyzedScript:
        """Create a new analyzed script record with automatic table creation"""
        
        # Ensure table exists before any operation
        ensure_analyzed_scripts_table(db)
        
        try:
            # Extract analysis data safely
            extracted_data = AnalyzedScriptService._extract_analysis_data(analysis_data)
            
            # Extract metadata for quick access
            metadata = AnalyzedScriptService._extract_metadata(extracted_data)
            
            analyzed_script = AnalyzedScript(
                id=str(uuid.uuid4()),
                filename=filename,
                original_filename=original_filename,
                file_size_bytes=file_size_bytes,
                project_id=project_id,  # Added project_id
                script_data=extracted_data.get('script_data'),
                cast_breakdown=extracted_data.get('cast_breakdown'),
                cost_breakdown=extracted_data.get('cost_breakdown'),
                location_breakdown=extracted_data.get('location_breakdown'),
                props_breakdown=extracted_data.get('props_breakdown'),
                processing_time_seconds=processing_time,
                api_calls_used=api_calls_used,
                status="completed",
                total_scenes=metadata.get('total_scenes'),
                total_characters=metadata.get('total_characters'),
                total_locations=metadata.get('total_locations'),
                estimated_budget=metadata.get('estimated_budget'),
                budget_category=metadata.get('budget_category')
            )
            
            db.add(analyzed_script)
            db.commit()
            db.refresh(analyzed_script)
            
            logger.info(f"Successfully created analyzed script: {analyzed_script.id}")
            return analyzed_script
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create analyzed script: {str(e)}")
            
            # Create error record
            error_script = AnalyzedScript(
                id=str(uuid.uuid4()),
                filename=filename,
                original_filename=original_filename,
                file_size_bytes=file_size_bytes,
                processing_time_seconds=processing_time,
                api_calls_used=api_calls_used,
                status="error",
                error_message=str(e)
            )
            
            try:
                db.add(error_script)
                db.commit()
                db.refresh(error_script)
                return error_script
            except Exception as db_error:
                db.rollback()
                logger.error(f"Failed to create error record: {str(db_error)}")
                raise Exception(f"Database operation failed: {str(e)}")
    
    @staticmethod
    def _extract_analysis_data(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Safely extract analysis data from various formats"""
        
        try:
            # ✅ FIXED: Handle the correct structure
            if isinstance(analysis_data, dict):
                # Check if it's already in the correct format
                if all(key in analysis_data for key in ['script_data', 'cast_breakdown', 'cost_breakdown', 'location_breakdown', 'props_breakdown']):
                    logger.info("✅ Analysis data already in correct format")
                    return analysis_data
                
                # Handle nested 'data' key
                if 'data' in analysis_data:
                    comprehensive_analysis = analysis_data['data']
                else:
                    comprehensive_analysis = analysis_data.get('comprehensive_analysis', analysis_data)
            else:
                comprehensive_analysis = analysis_data
            
            # Handle Pydantic objects
            if hasattr(comprehensive_analysis, 'model_dump'):
                result = comprehensive_analysis.model_dump()
            elif hasattr(comprehensive_analysis, 'dict'):
                result = comprehensive_analysis.dict()
            elif isinstance(comprehensive_analysis, dict):
                result = comprehensive_analysis
            else:
                logger.warning(f"Unexpected analysis data format: {type(comprehensive_analysis)}")
                return {}
            
            logger.info(f"✅ Extracted analysis data with keys: {list(result.keys())}")
            return result
                
        except Exception as e:
            logger.error(f"Failed to extract analysis data: {str(e)}")
            return {}
    
    @staticmethod
    def _extract_metadata(analysis_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata for quick access"""
        
        metadata = {}
        
        try:
            # Extract script metadata
            script_data = analysis_dict.get('script_data', {})
            if script_data:
                scenes = script_data.get('scenes', [])
                metadata['total_scenes'] = len(scenes)
                metadata['total_characters'] = len(script_data.get('total_characters', []))
                metadata['total_locations'] = len(script_data.get('total_locations', []))
            
            # Extract cost metadata
            cost_data = analysis_dict.get('cost_breakdown', {})
            if cost_data:
                metadata['estimated_budget'] = cost_data.get('total_costs', 0.0)
                metadata['budget_category'] = cost_data.get('budget_category', 'Medium')
            
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {str(e)}")
        
        return metadata
    
    @staticmethod
    def get_all_analyzed_scripts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[AnalyzedScript]:
        """Get all analyzed scripts with improved pagination and sorting"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            query = db.query(AnalyzedScript)
            
            # Apply ordering
            if order_direction.lower() == "desc":
                if order_by == "created_at":
                    query = query.order_by(desc(AnalyzedScript.created_at))
                elif order_by == "filename":
                    query = query.order_by(desc(AnalyzedScript.filename))
                elif order_by == "processing_time":
                    query = query.order_by(desc(AnalyzedScript.processing_time_seconds))
                elif order_by == "budget":
                    query = query.order_by(desc(AnalyzedScript.estimated_budget))
            else:
                if order_by == "created_at":
                    query = query.order_by(asc(AnalyzedScript.created_at))
                elif order_by == "filename":
                    query = query.order_by(asc(AnalyzedScript.filename))
                elif order_by == "processing_time":
                    query = query.order_by(asc(AnalyzedScript.processing_time_seconds))
                elif order_by == "budget":
                    query = query.order_by(asc(AnalyzedScript.estimated_budget))
            
            return query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_analyzed_scripts: {str(e)}")
            raise Exception(f"Failed to retrieve scripts: {str(e)}")
    
    @staticmethod
    def get_analyzed_script_by_id(db: Session, script_id: str) -> Optional[AnalyzedScript]:
        """Get analyzed script by ID with error handling"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            return db.query(AnalyzedScript).filter(AnalyzedScript.id == script_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_analyzed_script_by_id: {str(e)}")
            raise Exception(f"Failed to retrieve script {script_id}: {str(e)}")
    
    @staticmethod
    def delete_analyzed_script(db: Session, script_id: str) -> bool:
        """Delete analyzed script by ID with transaction management"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            script = db.query(AnalyzedScript).filter(AnalyzedScript.id == script_id).first()
            if script:
                db.delete(script)
                db.commit()
                logger.info(f"Successfully deleted script: {script_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in delete_analyzed_script: {str(e)}")
            raise Exception(f"Failed to delete script {script_id}: {str(e)}")
    
    @staticmethod
    def get_scripts_count(db: Session, status_filter: Optional[str] = None) -> int:
        """Get total count of analyzed scripts with optional status filter"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            query = db.query(AnalyzedScript)
            if status_filter:
                query = query.filter(AnalyzedScript.status == status_filter)
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_scripts_count: {str(e)}")
            return 0
    
    @staticmethod
    def search_scripts(
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        search_fields: Optional[List[str]] = None
    ) -> List[AnalyzedScript]:
        """Enhanced search scripts with multiple field support"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            if search_fields is None:
                search_fields = ['filename', 'original_filename']
            
            query = db.query(AnalyzedScript)
            
            # Build search conditions
            conditions = []
            for field in search_fields:
                if hasattr(AnalyzedScript, field):
                    field_attr = getattr(AnalyzedScript, field)
                    conditions.append(field_attr.ilike(f"%{search_term}%"))
            
            if conditions:
                # Use OR condition for multiple fields
                from sqlalchemy import or_
                query = query.filter(or_(*conditions))
            
            return query.order_by(desc(AnalyzedScript.created_at)).offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in search_scripts: {str(e)}")
            return []
    
    @staticmethod
    def get_scripts_by_status(
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnalyzedScript]:
        """Get scripts filtered by status"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            return db.query(AnalyzedScript).filter(
                AnalyzedScript.status == status
            ).order_by(desc(AnalyzedScript.created_at)).offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_scripts_by_status: {str(e)}")
            return []
    
    @staticmethod
    def get_scripts_statistics(db: Session) -> Dict[str, Any]:
        """Get database statistics"""
        
        # Ensure table exists before querying
        ensure_analyzed_scripts_table(db)
        
        try:
            total_scripts = db.query(AnalyzedScript).count()
            completed_scripts = db.query(AnalyzedScript).filter(
                AnalyzedScript.status == "completed"
            ).count()
            error_scripts = db.query(AnalyzedScript).filter(
                AnalyzedScript.status == "error"
            ).count()
            
            # Average processing time
            avg_processing_time = db.query(
                func.avg(AnalyzedScript.processing_time_seconds)
            ).filter(AnalyzedScript.status == "completed").scalar()
            
            # Total file size
            total_file_size = db.query(
                func.sum(AnalyzedScript.file_size_bytes)
            ).scalar()
            
            return {
                "total_scripts": total_scripts,
                "completed_scripts": completed_scripts,
                "error_scripts": error_scripts,
                "success_rate": (completed_scripts / total_scripts * 100) if total_scripts > 0 else 0,
                "average_processing_time": float(avg_processing_time) if avg_processing_time else 0,
                "total_file_size_mb": (total_file_size / (1024 * 1024)) if total_file_size else 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_scripts_statistics: {str(e)}")
            return {}
    
    @staticmethod
    def get_analyzed_scripts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[AnalyzedScript]:
        """Get analyzed scripts with pagination (alias for get_all_analyzed_scripts)"""
        return AnalyzedScriptService.get_all_analyzed_scripts(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
    
    @staticmethod
    def get_analyzed_scripts_count(db: Session) -> int:
        """Get total count of analyzed scripts (alias for get_scripts_count)"""
        return AnalyzedScriptService.get_scripts_count(db)
    
class UserService:
    """Service class for user operations"""
    
    @staticmethod
    def create_user(db: Session, email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
        """Create a new user"""
        try:
            # Hash password (simple hash for demo - use proper hashing in production)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hashed_password
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created successfully: {user.email}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Failed to create user: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                hashed_input = hashlib.sha256(password.encode()).hexdigest()
                # Compare the stored hash with the input hash
                stored_hash = str(user.hashed_password)  # Convert to string for comparison
                if stored_hash == hashed_input:
                    return user
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

class ProjectService:
    """Service class for project operations"""
    
    @staticmethod
    def create_project(db: Session, title: str, description: Optional[str] = None, user_id: Optional[str] = None) -> Project:
        """Create a new project"""
        # Ensure table exists before any operation
        ensure_projects_table(db)
        
        try:
            project = Project(
                title=title,
                description=description,
                user_id=user_id
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            logger.info(f"Project created successfully: {project.title}")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Failed to create project: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_projects(db: Session, user_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects with optional user filtering"""
        # Ensure table exists before any operation
        ensure_projects_table(db)
        
        query = db.query(Project)
        if user_id:
            query = query.filter(Project.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def update_project(db: Session, project_id: str, **kwargs) -> Optional[Project]:
        """Update project fields"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            # Let SQLAlchemy handle updated_at automatically through onupdate
            db.commit()
            db.refresh(project)
            logger.info(f"Project updated successfully: {project.title}")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Failed to update project: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        """Delete project and all associated scripts"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            db.delete(project)
            db.commit()
            logger.info(f"Project deleted successfully: {project_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete project: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_projects_count(db: Session, user_id: Optional[str] = None) -> int:
        """Get total count of projects"""
        query = db.query(Project)
        if user_id:
            query = query.filter(Project.user_id == user_id)
        return query.count()