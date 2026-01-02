"""
AI CV Suite - FastAPI Backend
Main entry point with CORS, static files, and router registration
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .routers import generation

# Get paths
BACKEND_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
ASSETS_DIR = BACKEND_DIR / "assets"
TEMPLATES_DIR = BACKEND_DIR / "templates"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(">> AI CV Suite Backend Starting...")
    print(f">> Output Directory: {OUTPUT_DIR}")
    print(f">> Assets Directory: {ASSETS_DIR}")
    print(f">> Templates Directory: {TEMPLATES_DIR}")
    
    # Check LLM provider
    llm_provider = "openrouter" if os.getenv("OPENROUTER_API_KEY") else "mock"
    print(f">> LLM Provider: {llm_provider}")
    
    yield
    
    # Shutdown
    print(">> AI CV Suite Backend Shutting Down...")


# Create FastAPI app
app = FastAPI(
    title="AI CV Suite",
    description="Generate batches of realistic PDF résumés with AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite alternate port
        "http://localhost:5175",  # Vite alternate port
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Include routers
app.include_router(generation.router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return JSONResponse(content={
        "name": "AI CV Suite API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /api/generate",
            "status": "GET /api/status",
            "files": "GET /api/files",
            "open_folder": "POST /api/open-folder",
            "health": "GET /api/health"
        }
    })


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return JSONResponse(content={
        "available_endpoints": [
            {"method": "POST", "path": "/api/generate", "description": "Start batch CV generation"},
            {"method": "GET", "path": "/api/status", "description": "Get current batch status"},
            {"method": "GET", "path": "/api/status/{batch_id}", "description": "Get specific batch status"},
            {"method": "GET", "path": "/api/files", "description": "List generated PDF files"},
            {"method": "GET", "path": "/api/files/{filename}", "description": "Download a PDF file"},
            {"method": "DELETE", "path": "/api/files/{filename}", "description": "Delete a PDF file"},
            {"method": "POST", "path": "/api/open-folder", "description": "Open output folder in OS"},
            {"method": "DELETE", "path": "/api/clear", "description": "Clear all generated files"},
            {"method": "GET", "path": "/api/health", "description": "Health check"}
        ]
    })


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
