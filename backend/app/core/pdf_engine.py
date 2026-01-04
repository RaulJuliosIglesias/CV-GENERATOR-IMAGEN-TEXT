"""
PDF Engine (HTML Based)
Renders CV as HTML using LeaG76 template.
Phase 5: Generates PDF using Playwright with image optimization.
"""

import os
import sys
import base64
import io
import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from PIL import Image
import random

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
TEMPLATES_DIR = BACKEND_DIR / "templates"

# Detect Vercel environment
IS_VERCEL = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None

# Ensure output directory exists (skip on Vercel)
if not IS_VERCEL:
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


async def render_cv_html(data_dict: dict, image_path: str | None, filename: str, output_dir: Path = None, compress_images: bool = False, image_size: int = 100, sidebar_color: str = None) -> str:
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
                # Compress for PDF - much smaller file BUT increased size for visibility
                context['profile_image'] = compress_image_base64(image_path, max_size=600, quality=75)
            else:
                # Full quality for HTML viewing
                with open(image_path, 'rb') as img:
                    img_b64 = base64.b64encode(img.read()).decode('utf-8')
                    context['profile_image'] = f"data:image/jpeg;base64,{img_b64}"
        elif 'profile_image' not in context:
            context['profile_image'] = ""

        # Add PDF generation flag
        context['is_pdf_generation'] = True
        
        if sidebar_color:
             context['sidebar_color'] = sidebar_color
        else:
            # Fallback if no color provided
            sidebar_colors = [
                '#E3F2FD', '#D1EAED', '#D4E6F1', '#EBF5FB', # Blues
                '#E8F5E9', '#DCE6D9', '#EAFAF1',            # Greens
                '#FAF2D3', '#FDEBD0', '#E6DDCF',            # Warm
                '#F4ECF7', '#E8DAEF', '#FADBD8',            # Rose/Purple
                '#E5E7E9', '#EAEDED', '#F2F3F4', '#D7DBDD'  # Neutrals
            ]
            context['sidebar_color'] = random.choice(sidebar_colors)

        # Calculate dynamic image styles based on image_size percentage
        # Base size: 260px (Web), 200px (PDF/Scaled)
        scale_factor = image_size / 100.0
        web_size = int(260 * scale_factor)
        pdf_size = int(200 * scale_factor)
        
        context['profile_img_size_web'] = web_size
        context['profile_img_size_pdf'] = pdf_size

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


async def render_cv_pdf(data_dict: dict, image_path: str | None, filename: str, smart_category: bool = False, role: str = None, image_size: int = 100, sidebar_color: str = None) -> tuple[str, str]:
    """
    Phase 4+5: Generate HTML and PDF from CV data.
    
    Args:
        data_dict: CV data dictionary
        image_path: Path to avatar image
        filename: Base filename for output
        smart_category: If True, save PDF in category subfolder based on role
        role: Job role/title for category determination
    
    Returns:
        Tuple of (html_path, pdf_path)
    """
    
    # Phase 4: Generate HTML (full quality for viewing)
    # ------------------------------------------------------------------
    html_output_dir = OUTPUT_DIR / "html"
    html_output_dir.mkdir(exist_ok=True)
    
    # We pass image_size to modify CSS in the template
    html_path = await render_cv_html(data_dict, image_path, filename, output_dir=html_output_dir, compress_images=False, image_size=image_size, sidebar_color=sidebar_color)

    # Phase 5: Generate PDF (from that HTML)
    # ------------------------------------------------------------------
    # We RE-RENDER HTML for PDF specifically if we want different compression/settings
    # But currently we use the existing HTML file with Playwright.
    # Wait, pdf_script uses the HTML file on disk. 
    
    # NOTE: If we wanted different image quality for PDF vs HTML view, we would generate a temporary HTML
    # for PDF generation. But here we share the HTML. 
    # The 'compress_images' param in render_cv_html was intended for specific PDF-only HTMLs.
    # Given we share HTML, let's keep high quality (compress_images=False).
    
    # However, we must ensure the HTML on disk matches the 'smart_category' path logic? 
    # No, smart_category only affects where the FINAL PDF is saved. HTML saved in /output/html is fine.
    
    # Determine PDF Output Path
    pdf_filename = filename.replace('.html', '.pdf')
    if not pdf_filename.endswith('.pdf'):
        pdf_filename += '.pdf'

    if smart_category and role:
        from .role_categories import get_category_for_role, ensure_category_folder
        category = get_category_for_role(role)
        # Create category subfolder if not exists
        pdf_parent_dir = ensure_category_folder(OUTPUT_DIR / "pdf", category)
        pdf_path = pdf_parent_dir / pdf_filename
        print(f"DEBUG: Smart Category ON - Role '{role}' -> Category '{category}'")
    else:
        pdf_output_dir = OUTPUT_DIR / "pdf"
        pdf_output_dir.mkdir(exist_ok=True)
        pdf_path = pdf_output_dir / pdf_filename
    
    print(f"DEBUG: Phase 5 - Generating PDF with Playwright at {pdf_path}")
    
    # Create a temporary HTML with compressed images for PDF generation
    temp_html_dir = OUTPUT_DIR / "temp"
    temp_html_dir.mkdir(exist_ok=True)
    temp_html_path = await render_cv_html(data_dict, image_path, f"temp_{filename}", temp_html_dir, compress_images=True, sidebar_color=sidebar_color)
    
    try:
        # Use run_in_executor with blocking subprocess - more reliable on Windows
        import asyncio
        import subprocess
        
        script_path = BACKEND_DIR / "generate_pdf_script.py"
        
        print(f"DEBUG PDF: Calling script {script_path}")
        print(f"DEBUG PDF: Input HTML: {temp_html_path}")
        print(f"DEBUG PDF: Output PDF: {pdf_path}")
        
        # Run blocking subprocess in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        
        def run_pdf_subprocess():
            return subprocess.run(
                [sys.executable, str(script_path), "--html", str(temp_html_path), "--out", str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
        
        process = await loop.run_in_executor(None, run_pdf_subprocess)
        
        print(f"DEBUG PDF: Return code: {process.returncode}")
        print(f"DEBUG PDF: Stdout: {process.stdout[:500] if process.stdout else 'EMPTY'}")
        print(f"DEBUG PDF: Stderr: {process.stderr[:500] if process.stderr else 'EMPTY'}")
        
        if process.returncode == 0 and "PDF Generation Complete" in process.stdout:
            print(f"SUCCESS: Phase 5 - PDF generated: {pdf_path.name}")
            
            # Clean up temp file
            try:
                os.remove(temp_html_path)
            except:
                pass
                
            return str(html_path), str(pdf_path)
        else:
            raise RuntimeError(f"Subprocess failed. Return code: {process.returncode}. Stderr: {process.stderr}\nStdout: {process.stdout}")
        
    except Exception as e:
        error_msg = f"ERROR: Phase 5 PDF generation failed: {e}"
        print(error_msg)
        
        # Log to file for debugging
        try:
            with open("error.log", "a") as f:
                f.write(f"\n--- {datetime.datetime.now()} ---\n")
                f.write(f"{error_msg}\n")
        except:
            pass
            
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
        # Use run_in_executor with blocking subprocess - more reliable on Windows
        import asyncio
        import subprocess
        
        script_path = BACKEND_DIR / "generate_pdf_script.py"
        
        loop = asyncio.get_event_loop()
        
        def run_pdf_subprocess():
            return subprocess.run(
                [sys.executable, str(script_path), "--html", str(html_path), "--out", str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
        
        process = await loop.run_in_executor(None, run_pdf_subprocess)
        
        if process.returncode == 0 and "PDF Generation Complete" in process.stdout:
            print(f"SUCCESS: PDF regenerated: {pdf_path.name}")
            return str(pdf_path)
        else:
            raise RuntimeError(f"Subprocess failed. Stderr: {process.stderr}\nStdout: {process.stdout}")
        
    except Exception as e:
        print(f"ERROR: PDF regeneration failed: {e}")
        # Log error to file
        try:
            with open("error.log", "a") as f:
                f.write(f"\n--- {datetime.datetime.now()} [REGEN] ---\n")
                f.write(f"ERROR: PDF regeneration failed: {e}\n")
        except:
            pass
        raise
