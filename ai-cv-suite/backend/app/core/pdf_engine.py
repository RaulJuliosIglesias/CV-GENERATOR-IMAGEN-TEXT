"""
PDF Engine - Jinja2 + WeasyPrint based CV renderer
Adapted from LeaG76/cv-generator template structure
"""

import os
import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BACKEND_DIR / "templates"
OUTPUT_DIR = BACKEND_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


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


def render_cv_pdf(data_dict: dict, image_path: str | None, filename: str) -> str:
    """
    Render a CV PDF from the provided data.
    
    Args:
        data_dict: Dictionary containing all CV data (name, skills, experience, etc.)
        image_path: Optional path to the profile image
        filename: Output filename (without path)
    
    Returns:
        Full path to the generated PDF file
    """
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("cv_template.html")
    
    # Process image
    if image_path and os.path.exists(image_path):
        data_dict["profile_image"] = get_image_as_base64(image_path)
    elif not data_dict.get("profile_image"):
        # Use placeholder if no image provided
        data_dict["profile_image"] = ""
    
    # Render HTML
    html_content = template.render(**data_dict)
    
    # Setup fonts
    font_config = FontConfiguration()
    
    # Load CSS
    css_path = TEMPLATES_DIR / "style.css"
    css = CSS(filename=str(css_path), font_config=font_config) if css_path.exists() else None
    
    # Generate PDF
    output_path = OUTPUT_DIR / filename
    html = HTML(string=html_content, base_url=str(TEMPLATES_DIR))
    
    if css:
        html.write_pdf(str(output_path), stylesheets=[css], font_config=font_config)
    else:
        html.write_pdf(str(output_path), font_config=font_config)
    
    return str(output_path)


def get_sample_cv_data() -> dict:
    """Return sample CV data for testing."""
    return {
        "name": "John Doe",
        "title": "Senior Software Developer",
        "email": "john.doe@email.com",
        "phone": "+1 555-123-4567",
        "profile_summary": "Passionate software developer with 8+ years of experience in building scalable web applications. Expert in Python, JavaScript, and cloud technologies.",
        "skills": [
            {"name": "Python", "level": 90},
            {"name": "JavaScript", "level": 85},
            {"name": "React", "level": 80},
            {"name": "AWS", "level": 75},
            {"name": "Docker", "level": 70}
        ],
        "languages": [
            {"name": "English", "level": 5},
            {"name": "Spanish", "level": 3},
            {"name": "French", "level": 2}
        ],
        "experience": [
            {
                "title": "Senior Software Developer",
                "company": "Tech Corp",
                "years": "2020 - Present",
                "description": "Leading a team of 5 developers in building microservices architecture for enterprise clients."
            },
            {
                "title": "Software Developer",
                "company": "StartUp Inc",
                "years": "2017 - 2020",
                "description": "Full-stack development using React and Node.js for SaaS products."
            }
        ],
        "education": [
            {
                "degree": "Master's in Computer Science",
                "institution": "MIT",
                "years": "2015 - 2017"
            },
            {
                "degree": "Bachelor's in Computer Science",
                "institution": "Stanford University",
                "years": "2011 - 2015"
            }
        ],
        "certificates": [
            {"year": "2023", "title": "AWS Solutions Architect", "honors": "Professional"},
            {"year": "2022", "title": "Google Cloud Engineer", "honors": "Associate"},
            {"year": "2021", "title": "Kubernetes Administrator", "honors": "CKA"}
        ],
        "interests": [
            {"name": "Open Source", "icon": "fa-code-branch"},
            {"name": "AI/ML", "icon": "fa-robot"},
            {"name": "Gaming", "icon": "fa-gamepad"},
            {"name": "Travel", "icon": "fa-plane"}
        ],
        "social": [
            {"platform": "GitHub", "username": "@johndoe", "url": "https://github.com/johndoe", "icon": "fa-github"},
            {"platform": "LinkedIn", "username": "johndoe", "url": "https://linkedin.com/in/johndoe", "icon": "fa-linkedin"}
        ]
    }
