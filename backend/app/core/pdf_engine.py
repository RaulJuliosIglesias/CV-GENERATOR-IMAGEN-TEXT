"""
PDF Engine (HTML Based)
Renders CV as HTML using LeaG76 template.
Phase 5: Generates PDF using Playwright with image optimization.
"""

import os
import base64
import io
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from PIL import Image

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
TEMPLATES_DIR = BACKEND_DIR / "templates"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "pdf").mkdir(exist_ok=True)
(OUTPUT_DIR / "html").mkdir(exist_ok=True)


def compress_image_base64(image_path: str, max_size: int = 200, quality: int = 60) -> str:
    """
    Compress an image and return as base64 string.
    Used to reduce HTML file size for faster PDF generation.
    
    Args:
        image_path: Path to the original image
        max_size: Maximum width/height in pixels (default 200px for CV profile)
        quality: JPEG quality (1-100, default 60 for good balance)
    
    Returns:
        Base64 encoded compressed image as data URI
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize maintaining aspect ratio
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save to buffer as JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)
            
            # Encode to base64
            img_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{img_b64}"
    except Exception as e:
        print(f"WARNING: Image compression failed: {e}")
        # Fallback to original
        try:
            with open(image_path, 'rb') as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
        except:
            return ""


async def render_cv_html(data_dict: dict, image_path: str | None, filename: str, output_dir: Path = None, compress_images: bool = False) -> str:
    """
    Render CV as HTML using Jinja2 template.
    Returns path to the generated HTML file.
    
    Args:
        output_dir: Directory to save HTML file (defaults to OUTPUT_DIR)
        compress_images: If True, compress images for smaller file size (used for PDF)
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
        
    try:
        # Load template
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template('cv_leag76_template.html')
        
        # Prepare context
        context = data_dict.copy()
        
        # Convert image to base64
        if image_path and os.path.exists(image_path):
            if compress_images:
                # Compress for PDF - much smaller file
                context['profile_image'] = compress_image_base64(image_path, max_size=200, quality=60)
            else:
                # Full quality for HTML viewing
                with open(image_path, 'rb') as img:
                    img_b64 = base64.b64encode(img.read()).decode('utf-8')
                    context['profile_image'] = f"data:image/jpeg;base64,{img_b64}"
        elif 'profile_image' not in context:
            context['profile_image'] = ""

        # Render HTML
        html_content = template.render(**context)
        
        # Save HTML file to specified directory
        output_filename = filename.replace('.pdf', '.html')
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


async def render_cv_pdf(data_dict: dict, image_path: str | None, filename: str) -> tuple[str, str]:
    """
    Phase 4+5: Generate HTML and PDF from CV data.
    
    Returns:
        Tuple of (html_path, pdf_path)
    """
    from playwright.async_api import async_playwright
    
    # Phase 4: Generate HTML (full quality for viewing)
    html_output_dir = OUTPUT_DIR / "html"
    html_output_dir.mkdir(exist_ok=True)
    html_path = await render_cv_html(data_dict, image_path, filename, html_output_dir, compress_images=False)
    
    # Phase 5: Generate PDF with compressed images
    pdf_output_dir = OUTPUT_DIR / "pdf"
    pdf_output_dir.mkdir(exist_ok=True)
    
    pdf_filename = filename.replace('.html', '.pdf')
    if not pdf_filename.endswith('.pdf'):
        pdf_filename += '.pdf'
    pdf_path = pdf_output_dir / pdf_filename
    
    print(f"DEBUG: Phase 5 - Generating PDF with Playwright at {pdf_path}")
    
    # Create a temporary HTML with compressed images for PDF generation
    temp_html_dir = OUTPUT_DIR / "temp"
    temp_html_dir.mkdir(exist_ok=True)
    temp_html_path = await render_cv_html(data_dict, image_path, f"temp_{filename}", temp_html_dir, compress_images=True)
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Load the compressed HTML
            file_uri = Path(temp_html_path).absolute().as_uri()
            await page.goto(file_uri, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for content to settle
            await page.wait_for_timeout(1000)
            
            # Generate PDF with A4 format and proper margins
            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={
                    "top": "10mm",
                    "bottom": "10mm",
                    "left": "8mm",
                    "right": "8mm"
                }
            )
            
            await browser.close()
            
        print(f"SUCCESS: Phase 5 - PDF generated with selectable text: {pdf_path.name}")
        
        # Clean up temp file
        try:
            os.remove(temp_html_path)
        except:
            pass
            
        return str(html_path), str(pdf_path)
        
    except Exception as e:
        print(f"ERROR: Phase 5 PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up temp file
        try:
            os.remove(temp_html_path)
        except:
            pass
            
        # Return None for PDF path so caller knows it failed
        return str(html_path), None


async def generate_pdf_from_existing_html(html_filename: str) -> str:
    """
    Generate PDF from an existing HTML file.
    Used for regenerating PDFs for previously created CVs.
    
    Note: This won't have image compression since we're using existing HTML.
    """
    from playwright.async_api import async_playwright
    
    html_path = OUTPUT_DIR / "html" / html_filename
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    
    pdf_output_dir = OUTPUT_DIR / "pdf"
    pdf_output_dir.mkdir(exist_ok=True)
    
    pdf_filename = html_filename.replace('.html', '.pdf')
    pdf_path = pdf_output_dir / pdf_filename
    
    print(f"DEBUG: Regenerating PDF for {html_filename}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            file_uri = html_path.absolute().as_uri()
            await page.goto(file_uri, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(1000)
            
            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "10mm", "bottom": "10mm", "left": "8mm", "right": "8mm"}
            )
            
            await browser.close()
            
        print(f"SUCCESS: PDF regenerated: {pdf_path.name}")
        return str(pdf_path)
        
    except Exception as e:
        print(f"ERROR: PDF regeneration failed: {e}")
        raise
