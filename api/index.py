"""
Minimal Vercel API - No backend imports to test basic functionality
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

# Create minimal app
app = FastAPI(title="AI CV Suite API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "platform": "vercel"}

@app.get("/api/models")
async def get_models():
    # Return minimal mock data for now
    return {
        "llm_models": [
            {"id": "openrouter/auto", "name": "Auto (Best Available)", "is_free": True}
        ],
        "image_models": [
            {"id": "bfl/flux-1-dev", "name": "Flux 1 Dev", "speed": "medium"}
        ]
    }

@app.get("/api/config")
async def get_config():
    return {
        "roles": ["Software Developer", "Product Manager", "Data Scientist"],
        "genders": [{"value": "any", "label": "Any Gender"}],
        "ethnicities": [{"value": "any", "label": "Any Ethnicity"}],
        "origins": [{"value": "any", "label": "Any Location"}],
        "expertise_levels": [{"value": "any", "label": "Any Level"}]
    }

@app.get("/api/files")
async def get_files():
    return {"files": [], "message": "File storage not available on Vercel"}

@app.post("/api/generate")
async def generate():
    return JSONResponse(
        status_code=501, 
        content={
            "error": "CV generation requires local deployment",
            "message": "Vercel serverless cannot run Playwright for PDF generation. Please use the local version."
        }
    )

@app.get("/")
async def root():
    return {"name": "AI CV Suite API", "version": "1.0.0", "platform": "vercel"}
