import os
import sys

# Add backend directory to path so imports work
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_path)

# Set environment variable for Vercel deployment detection
os.environ['VERCEL'] = '1'

from app.main import app

# Export the app for Vercel
handler = app
