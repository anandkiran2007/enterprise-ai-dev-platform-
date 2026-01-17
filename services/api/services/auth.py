"""
Authentication service
"""

import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from services.api.schemas.auth import GitHubAuthResponse, UserResponse, TokenResponse
from services.api.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.github_client_id = settings.github_client_id
        self.github_client_secret = settings.github_client_secret
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    async def authenticate_github(self, code: str, redirect_uri: str, db) -> GitHubAuthResponse:
        """Authenticate with GitHub OAuth code"""
        try:
            # Exchange code for access token
            token_data = await self._exchange_github_code(code, redirect_uri)
            
            # Get user information from GitHub
            user_data = await self._get_github_user(token_data["access_token"])
            
            # Get user organizations
            orgs_data = await self._get_github_organizations(token_data["access_token"])
            
            # Create or update user in database
            user = await self._create_or_update_user(user_data, db)
            
            # Generate JWT token
            jwt_token = self._create_access_token(data={"sub": user["id"]})
            
            return GitHubAuthResponse(
                access_token=jwt_token,
                user=user,
                organizations=orgs_data
            )
            
        except Exception as e:
            raise Exception(f"GitHub authentication failed: {str(e)}")
    
    async def get_current_user(self, token: str, db) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            
            # TODO: Get user from database
            # For now, return mock user
            return {
                "id": user_id,
                "email": "user@example.com",
                "name": "GitHub User"
            }
        except JWTError:
            return None
    
    async def refresh_token(self, token: str, db) -> TokenResponse:
        """Refresh access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise JWTError("Invalid token")
            
            # Generate new token
            new_token = self._create_access_token(data={"sub": user_id})
            
            return TokenResponse(
                access_token=new_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60
            )
        except JWTError:
            raise Exception("Invalid refresh token")
    
    async def _exchange_github_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange GitHub OAuth code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": self.github_client_id,
                    "client_secret": self.github_client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"GitHub token exchange failed: {response.text}")
            
            return response.json()
    
    async def _get_github_user(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitHub API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get GitHub user: {response.text}")
            
            return response.json()
    
    async def _get_github_organizations(self, access_token: str) -> list:
        """Get user organizations from GitHub API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user/orgs",
                headers={"Authorization": f"token {access_token}"}
            )
            
            if response.status_code != 200:
                return []
            
            return response.json()
    
    async def _create_or_update_user(self, github_user: Dict[str, Any], db) -> Dict[str, Any]:
        """Create or update user in database"""
        # TODO: Implement database operations
        # For now, return user data from GitHub
        return {
            "id": str(github_user["id"]),
            "email": github_user.get("email", f"{github_user['login']}@users.noreply.github.com"),
            "name": github_user.get("name", github_user["login"]),
            "username": github_user["login"],
            "avatar_url": github_user.get("avatar_url"),
            "github_id": github_user["id"]
        }
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
