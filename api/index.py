import os
import sys

# Add backend directory to path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.main import app

# Vercel expects a handler, but FastAPI app instance works directly with @vercel/python
