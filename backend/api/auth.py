"""
Authentication API endpoints for OAuth and user management
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import jwt as pyjwt
import os
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from database.database import get_db
from database.services import UserService
from auth.oauth_service import OAuthService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth service instance
oauth_service = OAuthService()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    oauth_provider: Optional[str]
    is_verified: bool
    profile_picture_url: Optional[str]
    created_at: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except pyjwt.ExpiredSignatureError:
        return None
    except pyjwt.JWTError:
        return None


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    try:
        auth_data = await oauth_service.get_google_auth_url()
        return {
            "auth_url": auth_data["auth_url"],
            "state": auth_data["state"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate Google login")


@router.get("/apple")
async def apple_login():
    """Initiate Apple OAuth login"""
    try:
        auth_data = await oauth_service.get_apple_auth_url()
        return {
            "auth_url": auth_data["auth_url"],
            "state": auth_data["state"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating Apple OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate Apple login")


@router.get("/callback/google")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Verify state parameter
        if not oauth_service.verify_state(state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for tokens and get user info
        user_data = await oauth_service.handle_google_callback(code)
        
        if not user_data:
            raise HTTPException(status_code=400, detail="Failed to get user data from Google")
        
        # Check if user exists
        existing_user = UserService.get_user_by_email(db, user_data["email"])
        
        if existing_user:
            # Update OAuth info if this is first OAuth login for existing user
            if not existing_user.oauth_provider:
                UserService.update_user(
                    db,
                    existing_user.id,
                    oauth_provider="google",
                    oauth_id=user_data["id"],
                    is_verified=True
                )
                existing_user = UserService.get_user_by_id(db, existing_user.id)
            
            # Update last login
            UserService.update_last_login(db, existing_user.id)
            user = existing_user
        else:
            # Create new user
            user = UserService.create_user(
                db,
                email=user_data["email"],
                username=user_data.get("name", user_data["email"].split("@")[0]),
                full_name=user_data.get("name"),
                oauth_provider="google",
                oauth_id=user_data["id"],
                profile_picture_url=user_data.get("picture"),
                is_verified=True
            )
            
            if not user:
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create JWT token
        token_data = {
            "sub": user.id,
            "email": user.email,
            "username": user.username
        }
        access_token = create_access_token(token_data)
        
        # Create response data
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            oauth_provider=user.oauth_provider,
            is_verified=user.is_verified,
            profile_picture_url=user.profile_picture_url,
            created_at=user.created_at.isoformat()
        )
        
        # For web apps, redirect to frontend with token and user data
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        user_data_encoded = urlencode({
            'access_token': access_token,
            'user': json.dumps(user_response.dict())
        })
        
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?{user_data_encoded}",
            status_code=302
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.get("/callback/apple")
async def apple_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Apple OAuth callback"""
    try:
        # Verify state parameter
        if not oauth_service.verify_state(state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for tokens and get user info
        user_data = await oauth_service.handle_apple_callback(code)
        
        if not user_data:
            raise HTTPException(status_code=400, detail="Failed to get user data from Apple")
        
        # Check if user exists
        existing_user = UserService.get_user_by_email(db, user_data["email"])
        
        if existing_user:
            # Update OAuth info if this is first OAuth login for existing user
            if not existing_user.oauth_provider:
                UserService.update_user(
                    db,
                    existing_user.id,
                    oauth_provider="apple",
                    oauth_id=user_data["sub"],
                    is_verified=True
                )
                existing_user = UserService.get_user_by_id(db, existing_user.id)
            
            # Update last login
            UserService.update_last_login(db, existing_user.id)
            user = existing_user
        else:
            # Create new user
            user = UserService.create_user(
                db,
                email=user_data["email"],
                username=user_data.get("name", user_data["email"].split("@")[0]),
                full_name=user_data.get("name"),
                oauth_provider="apple",
                oauth_id=user_data["sub"],
                is_verified=True
            )
            
            if not user:
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create JWT token
        token_data = {
            "sub": user.id,
            "email": user.email,
            "username": user.username
        }
        access_token = create_access_token(token_data)
        
        # Create response data
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            oauth_provider=user.oauth_provider,
            is_verified=user.is_verified,
            profile_picture_url=user.profile_picture_url,
            created_at=user.created_at.isoformat()
        )
        
        # For web apps, redirect to frontend with token and user data
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        user_data_encoded = urlencode({
            'access_token': access_token,
            'user': json.dumps(user_response.dict())
        })
        
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?{user_data_encoded}",
            status_code=302
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Apple callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.get("/me")
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Get user from database
        user = UserService.get_user_by_id(db, payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            oauth_provider=user.oauth_provider,
            is_verified=user.is_verified,
            profile_picture_url=user.profile_picture_url,
            created_at=user.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Logged out successfully"}


@router.get("/status")
async def auth_status():
    """Check authentication system status"""
    return {
        "google_configured": bool(os.getenv("GOOGLE_OAUTH_CLIENT_ID")),
        "apple_configured": bool(os.getenv("APPLE_CLIENT_ID")),
        "jwt_configured": bool(JWT_SECRET != "your-secret-key-change-this-in-production")
    }
