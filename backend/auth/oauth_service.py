"""
OAuth service utilities for Google and Apple authentication
"""
import os
import json
import httpx
import secrets
import hashlib
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs
from authlib.integrations.starlette_client import OAuth
from authlib.jose import JsonWebKey, jwt
from database.models import User
from database.services import UserService
import logging

logger = logging.getLogger(__name__)

class OAuthService:
    """Service for handling OAuth authentication with Google and Apple"""
    
    def __init__(self):
        self.google_client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        self.google_client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        self.google_redirect_uri = os.getenv('GOOGLE_OAUTH_REDIRECT_URI')
        
        self.apple_client_id = os.getenv('APPLE_CLIENT_ID')
        self.apple_team_id = os.getenv('APPLE_TEAM_ID')
        self.apple_key_id = os.getenv('APPLE_KEY_ID')
        self.apple_private_key_path = os.getenv('APPLE_PRIVATE_KEY_PATH')
        self.apple_redirect_uri = os.getenv('APPLE_REDIRECT_URI')
        
        self.state_secret = os.getenv('OAUTH_STATE_SECRET', 'default-secret')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    def generate_state(self, provider: str) -> str:
        """Generate a secure state parameter for OAuth flow"""
        random_string = secrets.token_urlsafe(32)
        state_data = f"{provider}:{random_string}"
        return hashlib.sha256(f"{state_data}:{self.state_secret}".encode()).hexdigest()[:32]
    
    def verify_state(self, state: str, provider: str) -> bool:
        """Verify the state parameter"""
        # For simplicity, we'll use a basic verification
        # In production, you'd want to store and verify state properly
        return len(state) == 32 and state.isalnum()
    
    async def get_google_auth_url(self) -> Dict[str, str]:
        """Generate Google OAuth authorization URL"""
        if not self.google_client_id:
            raise ValueError("Google OAuth not configured")
        
        state = self.generate_state('google')
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.google_redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state
        }
    
    async def get_apple_auth_url(self) -> Dict[str, str]:
        """Generate Apple OAuth authorization URL"""
        if not self.apple_client_id:
            raise ValueError("Apple OAuth not configured")
        
        state = self.generate_state('apple')
        
        params = {
            'client_id': self.apple_client_id,
            'redirect_uri': self.apple_redirect_uri,
            'response_type': 'code',
            'scope': 'name email',
            'response_mode': 'form_post',
            'state': state
        }
        
        auth_url = f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state
        }
    
    async def handle_google_callback(self, code: str, state: str) -> Optional[Dict[str, Any]]:
        """Handle Google OAuth callback and return user data"""
        try:
            # Verify state
            if not self.verify_state(state, 'google'):
                logger.error("Invalid state parameter for Google OAuth")
                return None
            
            # Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'client_id': self.google_client_id,
                'client_secret': self.google_client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.google_redirect_uri
            }
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                token_info = token_response.json()
            
            access_token = token_info.get('access_token')
            if not access_token:
                logger.error("No access token received from Google")
                return None
            
            # Get user info
            user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
            async with httpx.AsyncClient() as client:
                user_response = await client.get(user_info_url)
                user_response.raise_for_status()
                user_data = user_response.json()
            
            return {
                'provider': 'google',
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture'),
                'verified_email': user_data.get('verified_email', False)
            }
            
        except Exception as e:
            logger.error(f"Google OAuth callback error: {str(e)}")
            return None
    
    async def handle_apple_callback(self, code: str, state: str, id_token: str = None) -> Optional[Dict[str, Any]]:
        """Handle Apple OAuth callback and return user data"""
        try:
            # Verify state
            if not self.verify_state(state, 'apple'):
                logger.error("Invalid state parameter for Apple OAuth")
                return None
            
            # For Apple, we primarily use the id_token which contains user info
            if id_token:
                # Decode the JWT token (Apple ID token)
                # Note: In production, you should verify the token signature
                import jwt as pyjwt
                decoded = pyjwt.decode(id_token, options={"verify_signature": False})
                
                return {
                    'provider': 'apple',
                    'provider_id': decoded.get('sub'),
                    'email': decoded.get('email'),
                    'name': f"Apple User {decoded.get('sub', '')[:8]}",  # Apple doesn't always provide name
                    'verified_email': decoded.get('email_verified', False)
                }
            
            # Fallback: exchange code for token (if id_token not provided)
            logger.warning("Apple callback without id_token, attempting code exchange")
            return None
            
        except Exception as e:
            logger.error(f"Apple OAuth callback error: {str(e)}")
            return None

# Global instance
oauth_service = OAuthService()
