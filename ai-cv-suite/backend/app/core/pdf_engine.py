"""
PDF Engine (HTML Based)
Renders CV as HTML using LeaG76 template for client-side PDF generation.
"""

import os
import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
TEMPLATES_DIR = BACKEND_DIR / "templates"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

async def render_cv_html(data_dict: dict, image_path: str | None, filename: str) -> str:
    """
    Render CV as HTML using Jinja2 template.
    Returns path to the generated HTML file.
    """
    try:
        # Load template
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template('cv_leag76_template.html')
        
        # Prepare context
        context = data_dict.copy()
        
        # Convert image to base64 if exists
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                img_b64 = base64.b64encode(img.read()).decode('utf-8')
                context['profile_image'] = f"data:image/jpeg;base64,{img_b64}"
        elif 'profile_image' not in context:
            # Fallback or placeholder if needed, or handle in template
            context['profile_image'] = ""

        # Render HTML
        html_content = template.render(**context)
        
        # Save HTML file
        output_filename = filename.replace('.pdf', '.html') # Ensure extension
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"SUCCESS: CV HTML generated: {output_path.name}")
        return str(output_path)
        
    except Exception as e:
        print(f"ERROR rendering HTML: {e}")
        import traceback
        traceback.print_exc()
        raise e

async def render_cv_pdf(data_dict: dict, image_path: str | None, filename: str) -> str:
    """
    Legacy/Fallback wrapper. 
    In this new architecture, we generate HTML. 
    The 'pdf_path' in Task will point to this HTML for now, 
    or we can generate a dummy PDF if strictly required.
    For now, return the HTML path as the PDF path (client handles export).
    """
    return await render_cv_html(data_dict, image_path, filename)
