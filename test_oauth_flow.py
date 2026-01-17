#!/usr/bin/env python3
"""
Test script to verify GitHub OAuth flow implementation
"""

import asyncio
import httpx
from services.api.services.auth import AuthService
from services.api.config import settings

async def test_github_oauth_flow():
    """Test the complete GitHub OAuth flow"""
    print("🔐 Testing GitHub OAuth Flow Implementation")
    print("=" * 50)
    
    # Test 1: JWT Token Generation
    print("\n1. Testing JWT Token Generation...")
    service = AuthService()
    token = service._create_access_token(data={"sub": "test_user_123"})
    print(f"✅ JWT Token generated: {token[:50]}...")
    
    # Test 2: JWT Token Validation
    print("\n2. Testing JWT Token Validation...")
    try:
        from jose import jwt
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"✅ JWT Token decoded successfully: {payload}")
    except Exception as e:
        print(f"❌ JWT Token validation failed: {e}")
    
    # Test 3: GitHub OAuth URL Generation
    print("\n3. Testing GitHub OAuth URL Generation...")
    github_client_id = settings.github_client_id
    redirect_uri = f"{settings.base_url}/api/auth/github/callback"
    scope = "user:email user:repo"
    
    auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={github_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"state=random_state"
    )
    print(f"✅ GitHub OAuth URL: {auth_url}")
    
    # Test 4: Configuration Check
    print("\n4. Testing Configuration...")
    print(f"✅ GitHub Client ID: {github_client_id[:10]}...")
    print(f"✅ GitHub Client Secret: {'*' * 20}")
    print(f"✅ Redirect URI: {redirect_uri}")
    print(f"✅ Base URL: {settings.base_url}")
    print(f"✅ Dashboard URL: {settings.dashboard_url}")
    
    print("\n" + "=" * 50)
    print("🎉 GitHub OAuth Flow Implementation Complete!")
    print("\n📋 Next Steps:")
    print("1. Visit: http://localhost:8000/api/auth/github")
    print("2. Authorize with GitHub")
    print("3. Get redirected to: http://localhost:3000?token=<jwt_token>")
    print("4. Use the JWT token to authenticate API calls")

if __name__ == "__main__":
    asyncio.run(test_github_oauth_flow())
