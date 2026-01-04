import os
import sys
import traceback

# Set environment variable for Vercel deployment detection FIRST
os.environ['VERCEL'] = '1'

# Add backend directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
sys.path.insert(0, backend_path)

# Also add the backend/app directory
app_path = os.path.join(backend_path, 'app')
sys.path.insert(0, app_path)

try:
    from app.main import app
    handler = app
except Exception as e:
    # If import fails, create a minimal app that shows the error
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI()
    error_message = f"Import Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    
    @error_app.get("/api/{path:path}")
    @error_app.post("/api/{path:path}")
    async def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": "Backend failed to load", "details": error_message}
        )
    
    handler = error_app
    app = error_app
