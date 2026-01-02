import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.getcwd())

from app.core.pdf_engine import render_cv_pdf

async def test():
    print("Testing PDF Generation...")
    
    data = {
        "name": "Test User",
        "title": "Software Engineer",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "location": "New York, USA",
        "profile_summary": "Test summary.",
        "skills": {"technical": [{"name": "Python", "level": 90}]},
        "experience": [],
        "education": [],
        "languages": [],
        "interests": ["Coding"]
        # Intentionally missing: social, certificates
    }
    
    filename = "test_cv.html"
    
    try:
        path = await render_cv_pdf(data, None, filename)
        print(f"SUCCESS: {path}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
