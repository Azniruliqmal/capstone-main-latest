#!/usr/bin/env python3
"""
Quick test to verify OAuth imports work
"""
try:
    from api.auth import router
    print("✅ OAuth router imported successfully")
    
    from auth.oauth_service import OAuthService
    print("✅ OAuth service imported successfully")
    
    from database.models import User
    print("✅ User model imported successfully")
    
    print("🎉 All OAuth components working!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
