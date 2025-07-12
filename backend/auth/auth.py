"""
Authentication utilities for SceneSplit AI
"""
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from database.models import User, UserRole
from database.services import UserService

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await UserService.get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def register_user(email: str, username: str, password: str, **kwargs) -> User:
    """Register a new user"""
    hashed_password = get_password_hash(password)
    return await UserService.create_user(
        email=email,
        username=username,
        hashed_password=hashed_password,
        **kwargs
    )

async def create_demo_users():
    """Create demo users for testing"""
    demo_users = [
        {
            "email": "admin@scenesplit.ai",
            "username": "admin",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "is_verified": True
        },
        {
            "email": "demo@scenesplit.ai", 
            "username": "demo",
            "password": "demo123",
            "full_name": "Demo User",
            "role": UserRole.DEMO,
            "is_verified": True
        },
        {
            "email": "guest@scenesplit.ai",
            "username": "guest", 
            "password": "guest123",
            "full_name": "Guest User",
            "role": UserRole.GUEST,
            "is_verified": True
        }
    ]
    
    for user_data in demo_users:
        existing_user = await UserService.get_user_by_email(user_data["email"])
        if not existing_user:
            password = user_data.pop("password")
            await register_user(password=password, **user_data)
            print(f"✅ Created demo user: {user_data['username']}")
        else:
            print(f"ℹ️ Demo user already exists: {user_data['username']}")

def generate_api_key(user_id: str) -> str:
    """Generate API key for user"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    data = f"{user_id}:{timestamp}:{SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()

async def validate_api_key(api_key: str) -> Optional[User]:
    """Validate API key and return user"""
    # This is a simple implementation - in production you'd want to store API keys in database
    # For now, we'll just validate format
    if len(api_key) == 64:  # SHA256 hash length
        # In a real implementation, you'd look up the API key in the database
        return None
    return None
