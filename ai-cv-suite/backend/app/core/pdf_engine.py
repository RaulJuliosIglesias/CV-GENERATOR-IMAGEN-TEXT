"""
PDF Engine - HTML to PDF CV renderer using Playwright
Works reliably on Windows without GTK dependencies
"""

import os
import base64
import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BACKEND_DIR / "templates"
OUTPUT_DIR = BACKEND_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Flag to track if playwright is available
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


def get_image_as_base64(image_path: str) -> str:
    """Convert an image file to base64 data URL for embedding in HTML."""
    if not image_path or not os.path.exists(image_path):
        return ""
    
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode("utf-8")
    
    # Determine MIME type
    ext = Path(image_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    mime_type = mime_types.get(ext, "image/jpeg")
    
    return f"data:{mime_type};base64,{img_data}"


def render_html(data_dict: dict, image_path: str | None) -> str:
    """Render the CV template to HTML string."""
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("cv_template.html")
    
    # Process image
    if image_path and os.path.exists(image_path):
        data_dict["profile_image"] = get_image_as_base64(image_path)
    elif not data_dict.get("profile_image"):
        data_dict["profile_image"] = ""
    
    # Render HTML
    return template.render(**data_dict)


async def render_cv_pdf_async(data_dict: dict, image_path: str | None, filename: str) -> str:
    """
    Render a CV PDF from the provided data using Playwright.
    
    Args:
        data_dict: Dictionary containing all CV data
        image_path: Optional path to the profile image
        filename: Output filename (without path)
    
    Returns:
        Full path to the generated PDF file
    """
    html_content = render_html(data_dict, image_path)
    output_path = OUTPUT_DIR / filename
    
    if PLAYWRIGHT_AVAILABLE:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            await page.set_content(html_content, wait_until="networkidle")
            
            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "0",
                    "right": "0",
                    "bottom": "0",
                    "left": "0"
                }
            )
            
            await browser.close()
    else:
        # Fallback: save as HTML if Playwright not available
        html_path = output_path.with_suffix('.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"⚠️ Playwright not available, saved as HTML: {html_path}")
        return str(html_path)
    
    return str(output_path)


def render_cv_pdf(data_dict: dict, image_path: str | None, filename: str) -> str:
    """
    Synchronous wrapper for PDF rendering.
    """
    return asyncio.run(render_cv_pdf_async(data_dict, image_path, filename))


def get_sample_cv_data() -> dict:
    """Return sample CV data for testing."""
    return {
        "name": "John Doe",
        "title": "Senior Software Developer",
        "email": "john.doe@email.com",
        "phone": "+1 555-123-4567",
        "profile_summary": "Passionate software developer with 8+ years of experience in building scalable web applications.",
        "skills": [
            {"name": "Python", "level": 90},
            {"name": "JavaScript", "level": 85},
            {"name": "React", "level": 80},
        ],
        "languages": [
            {"name": "English", "level": 5},
            {"name": "Spanish", "level": 3},
        ],
        "experience": [
            {
                "title": "Senior Software Developer",
                "company": "Tech Corp",
                "years": "2020 - Present",
                "description": "Leading development teams."
            }
        ],
        "education": [
            {
                "degree": "Master's in Computer Science",
                "institution": "MIT",
                "years": "2015 - 2017"
            }
        ],
        "certificates": [
            {"year": "2023", "title": "AWS Solutions Architect", "honors": "Professional"}
        ],
        "interests": [
            {"name": "Open Source", "icon": "fa-code-branch"},
            {"name": "Gaming", "icon": "fa-gamepad"}
        ],
        "social": [
            {"platform": "GitHub", "username": "@johndoe", "url": "https://github.com/johndoe", "icon": "fa-github"}
        ]
    }
