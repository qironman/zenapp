"""FastAPI application entry point."""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers import books, chapters, agent, prompts
from .auth import LoginRequest, Token, authenticate_user, create_access_token

app = FastAPI(
    title="ZenApp API",
    description="Backend for ZenApp markdown book editor",
    version="0.1.0",
)

# CORS for development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://zenapp.tianzent.com",
        "https://zenapp.share.zrok.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router)
app.include_router(chapters.router)
app.include_router(agent.router)
app.include_router(prompts.router)


@app.post("/api/login", response_model=Token)
def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    username = authenticate_user(request.username, request.password)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Serve frontend static files in production
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA for all non-API routes."""
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
