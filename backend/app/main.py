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

# Load environment variables from correct path
BACKEND_DIR_INIT = Path(__file__).parent.parent
ENV_PATH = BACKEND_DIR_INIT / ".env"

# Manual .env reader (bypasses broken load_dotenv)
def load_env_manually(env_path: Path):
    """Manually read .env file and set environment variables."""
    if not env_path.exists():
        print(f"WARNING: .env file not found at {env_path}")
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
                    print(f"DEBUG: Set {key}={value[:15]}..." if len(value) > 15 else f"DEBUG: Set {key}={value}")
    except Exception as e:
        print(f"ERROR reading .env: {e}")

# Load using manual reader
load_env_manually(ENV_PATH)

# Debug: Confirm API key loaded at startup
_api_key = os.getenv("OPENROUTER_API_KEY", "")
print(f"DEBUG MAIN: .env path: {ENV_PATH} (exists: {ENV_PATH.exists()})")
print(f"DEBUG MAIN: OPENROUTER_API_KEY loaded: {'YES (' + _api_key[:8] + '...)' if _api_key and len(_api_key) > 8 else 'NO/EMPTY'}")

from .routers import generation

# Get paths
BACKEND_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
ASSETS_DIR = BACKEND_DIR / "assets"
TEMPLATES_DIR = BACKEND_DIR / "templates"

# Detect Vercel environment
IS_VERCEL = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None

# Ensure directories exist (skip on Vercel - read-only filesystem)
if not IS_VERCEL:
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
origins = ["*"]  # Allow all origins for development to avoid CORS issues

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories - skip on Vercel (no persistent filesystem)
if not IS_VERCEL:
    app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
    if (OUTPUT_DIR / "html").exists():
        app.mount("/html", StaticFiles(directory=str(OUTPUT_DIR / "html")), name="html")
    if (OUTPUT_DIR / "pdf").exists():
        app.mount("/pdf", StaticFiles(directory=str(OUTPUT_DIR / "pdf")), name="pdf")
    if (OUTPUT_DIR / "prompts").exists():
        app.mount("/prompts", StaticFiles(directory=str(OUTPUT_DIR / "prompts")), name="prompts")
    if (OUTPUT_DIR / "avatars").exists():
        app.mount("/avatars", StaticFiles(directory=str(OUTPUT_DIR / "avatars")), name="avatars")
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Import config service
from .services.roles_service import get_all_config

@app.get("/api/config")
async def get_config():
    """Get all configuration options from centralized database.
    
    Returns roles, genders, ethnicities, origins, expertise_levels.
    Frontend should fetch this on mount to populate dropdowns.
    """
    print("DEBUG API: /api/config endpoint called")
    config = get_all_config()
    print(f"DEBUG API: Serving config with {len(config.get('roles', []))} roles")
    print(f"DEBUG API: Serving config with {len(config.get('roles', []))} roles")
    return JSONResponse(content=config)

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Railway/Docker deployments."""
    return {"status": "ok", "service": "ai-cv-suite"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# Include routers - Load generation router AFTER config just in case
print("DEBUG MAIN: Loading generation router...")
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
