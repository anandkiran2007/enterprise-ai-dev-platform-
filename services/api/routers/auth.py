"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from typing import Optional

from services.api.schemas.auth import (
    GitHubAuthRequest, 
    GitHubAuthResponse,
    UserResponse,
    TokenResponse
)
from services.api.services.auth import AuthService
from services.api.database import get_db
from services.api.config import settings

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: Optional[str] = None,
    db=Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    try:
        result = await auth_service.authenticate_github(
            code=code,
            redirect_uri=f"{settings.base_url}/api/auth/github/callback",
            db=db
        )
        
        # Redirect to dashboard with token
        redirect_url = f"{settings.dashboard_url}?token={result.access_token}"
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        # Log the error for debugging
        print(f"GitHub callback error: {str(e)}")
        # Redirect to dashboard with error parameter
        error_url = f"{settings.dashboard_url}?error=auth_failed&message={str(e)}"
        return RedirectResponse(url=error_url, status_code=302)


@router.get("/github")
async def github_auth_redirect():
    """Redirect to GitHub OAuth authorize endpoint"""
    print(f"DEBUG: GitHub auth redirect called")
    return RedirectResponse(url="/api/auth/github/authorize", status_code=302)


@router.get("/github/authorize")
@router.head("/github/authorize")
async def github_authorize():
    """Initiate GitHub OAuth flow"""
    print(f"DEBUG: GitHub authorize called")
    github_client_id = settings.github_client_id
    redirect_uri = f"{settings.base_url}/api/auth/github/callback"
    scope = "user:email user:repo read:org"
    
    auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={github_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"state=random_state"
    )
    
    print(f"DEBUG: Redirecting to: {auth_url}")
    return RedirectResponse(url=auth_url, status_code=302)


@router.post("/github", response_model=GitHubAuthResponse)
async def github_auth(
    request: GitHubAuthRequest,
    db=Depends(get_db)
):
    """Authenticate with GitHub OAuth"""
    try:
        result = await auth_service.authenticate_github(
            code=request.code,
            redirect_uri=request.redirect_uri,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"GitHub authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(security),
    db=Depends(get_db)
):
    """Get current user information"""
    try:
        user = await auth_service.get_current_user(token.credentials, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token: str = Depends(security),
    db=Depends(get_db)
):
    """Refresh access token"""
    try:
        result = await auth_service.refresh_token(token.credentials, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )
