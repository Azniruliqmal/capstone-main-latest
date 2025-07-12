"""
File service for handling file uploads and processing
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from database.models import FileUpload
from database.services import FileUploadService
import pdfplumber
import tempfile

class FileService:
    def __init__(self):
        self.upload_dir = Path(os.getenv("UPLOAD_DIRECTORY", "uploads"))
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024  # Convert to bytes
        self.allowed_extensions = {".pdf", ".txt", ".fountain", ".doc", ".docx"}
    
    async def save_uploaded_file(
        self,
        file: UploadFile,
        user_id: str,
        project_id: Optional[str] = None,
        upload_purpose: str = "general"
    ) -> Dict[str, Any]:
        """Save uploaded file and create database record"""
        
        # Validate file
        await self._validate_file(file)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Create database record
            file_record = await FileUploadService.create_file_upload(
                user_id=user_id,
                project_id=project_id,
                filename=unique_filename,
                original_filename=file.filename,
                file_size=len(content),
                file_type=file.content_type,
                file_path=str(file_path),
                upload_purpose=upload_purpose
            )
            
            return {
                "id": file_record.id,
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "file_type": file.content_type
            }
            
        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            )
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from uploaded file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == ".pdf":
                return await self._extract_from_pdf(file_path)
            elif file_extension in [".txt", ".fountain"]:
                return await self._extract_from_text(file_path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Text extraction not supported for {file_extension} files"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text: {str(e)}"
            )
    
    async def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text_content = ""
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
        
        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="No text content found in PDF"
            )
        
        return text_content.strip()
    
    async def _extract_from_text(self, file_path: Path) -> str:
        """Extract text from text file"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
        
        if not content.strip():
            raise HTTPException(
                status_code=400,
                detail="File appears to be empty"
            )
        
        return content.strip()
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete file and database record"""
        # Get file record
        file_record = await FileUpload.find_one(FileUpload.id == file_id)
        
        if not file_record:
            return False
        
        # Check ownership
        if file_record.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        try:
            # Delete physical file
            file_path = Path(file_record.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete database record
            await file_record.delete()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    async def get_file_info(self, file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        file_record = await FileUpload.find_one(FileUpload.id == file_id)
        
        if not file_record:
            return None
        
        # Check access
        if file_record.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        return {
            "id": file_record.id,
            "filename": file_record.filename,
            "original_filename": file_record.original_filename,
            "file_size": file_record.file_size,
            "file_type": file_record.file_type,
            "upload_purpose": file_record.upload_purpose,
            "created_at": file_record.created_at.isoformat(),
            "processed": file_record.processed
        }
