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
(OUTPUT_DIR / "pdf").mkdir(exist_ok=True)
(OUTPUT_DIR / "html").mkdir(exist_ok=True)

async def render_cv_html(data_dict: dict, image_path: str | None, filename: str, output_dir: Path = None) -> str:
    """
    Render CV as HTML using Jinja2 template.
    Returns path to the generated HTML file.
    
    Args:
        output_dir: Directory to save HTML file (defaults to OUTPUT_DIR)
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
        
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
        
        # Save HTML file to specified directory
        output_filename = filename.replace('.pdf', '.html') # Ensure extension
        output_path = Path(output_dir) / output_filename
        
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
    Generate PDF from HTML using Playwright (Headless Browser).
    This ensures exact rendering, selectable text, and proper pagination.
    """
    # 1. First generate the HTML (source) in html/ subfolder
    html_output_dir = OUTPUT_DIR / "html"
    html_output_dir.mkdir(exist_ok=True)
    
    html_path = await render_cv_html(data_dict, image_path, filename, html_output_dir)
    
    # 2. Define PDF Output Path in pdf/ subfolder
    pdf_output_dir = OUTPUT_DIR / "pdf"
    pdf_output_dir.mkdir(exist_ok=True)
    
    pdf_filename = filename.replace('.html', '.pdf')
    if not pdf_filename.endswith('.pdf'):
        pdf_filename += '.pdf'
        
    pdf_path = pdf_output_dir / pdf_filename
    
    print(f"DEBUG: Generating PDF using Playwright at {pdf_path}")
    
    # 3. Use Playwright to render PDF
    from playwright.async_api import async_playwright
    
    try:
        async with async_playwright() as p:
            # Launch browser (chromium is standard)
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Load the HTML file
            # Need absolute file URI
            file_uri = Path(html_path).absolute().as_uri()
            await page.goto(file_uri, wait_until="networkidle")
            
            # Inject CSS to force A4 and print styles calculation if needed
            # (Already handled by @media print in template, but good to be safe)
            
            # Generate PDF
            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "0mm",    # Margins handled by CSS
                    "bottom": "0mm", 
                    "left": "0mm",
                    "right": "0mm"
                }
            )
            
            await browser.close()
            
        print(f"SUCCESS: CV PDF generated: {pdf_path.name}")
        return str(pdf_path)
        
    except Exception as e:
        print(f"ERROR: Playwright PDF generation failed: {e}")
        # Fallback: Return HTML path so user can at least print it
        print("FALLBACK: Returning HTML path.")
        return html_path
