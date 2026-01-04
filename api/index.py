import os
import sys

# Set environment variable for Vercel deployment detection FIRST
os.environ['VERCEL'] = '1'

# Minimal FastAPI app for testing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="AI CV Suite API - Vercel")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test if we can import the backend
import_status = {}

try:
    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
    sys.path.insert(0, backend_path)
    import_status["backend_path"] = backend_path
    import_status["backend_exists"] = os.path.exists(backend_path)
    
    # Try importing step by step
    try:
        from app.services.roles_service import get_all_config
        import_status["roles_service"] = "OK"
    except Exception as e:
        import_status["roles_service"] = str(e)
    
    try:
        from app.services.llm_service import get_available_models as get_llm_models
        import_status["llm_service"] = "OK"
    except Exception as e:
        import_status["llm_service"] = str(e)
        
    try:
        from app.services.krea_service import get_available_models as get_image_models
        import_status["krea_service"] = "OK"
    except Exception as e:
        import_status["krea_service"] = str(e)

except Exception as e:
    import_status["error"] = str(e)

@app.get("/api/health")
async def health():
    return {"status": "ok", "vercel": True, "imports": import_status}

@app.get("/api/models")
async def get_models():
    if import_status.get("llm_service") == "OK" and import_status.get("krea_service") == "OK":
        from app.services.llm_service import get_available_models as get_llm_models
        from app.services.krea_service import get_available_models as get_image_models
        return {
            "llm_models": await get_llm_models(),
            "image_models": get_image_models()
        }
    return JSONResponse(status_code=500, content={"error": "Import failed", "details": import_status})

@app.get("/api/config")
async def get_config():
    if import_status.get("roles_service") == "OK":
        from app.services.roles_service import get_all_config
        return get_all_config()
    return JSONResponse(status_code=500, content={"error": "Import failed", "details": import_status})

@app.get("/api/files")
async def get_files():
    # No file system on Vercel
    return {"files": [], "message": "File storage not available on Vercel"}

@app.post("/api/generate")
async def generate():
    return JSONResponse(
        status_code=501, 
        content={"error": "CV generation not available on Vercel (requires Playwright). Use local version."}
    )

@app.get("/api/{path:path}")
async def catch_all(path: str):
    return {"path": path, "imports": import_status}

handler = app
