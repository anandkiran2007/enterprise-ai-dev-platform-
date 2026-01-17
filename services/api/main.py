"""
FastAPI Gateway for Enterprise AI Development Platform
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from contextlib import asynccontextmanager

from services.api.database import init_db
from services.api.routers import auth, organizations, projects, repositories, features, agents, integration
from services.api.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Enterprise AI Development Platform",
    description="AI-powered development platform for enterprise multi-repo systems",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
app.include_router(features.router, prefix="/api/features", tags=["features"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(integration.router, prefix="/api/integration", tags=["coding-tool-integration"])


@app.get("/")
async def root():
    return {
        "message": "Enterprise AI Development Platform API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}


if __name__ == "__main__":
    uvicorn.run(
        "services.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
