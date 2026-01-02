"""
PDF Engine - Professional CV PDF Generator inspired by LeaG76 design
Two-column layout with profile image, clean typography
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Image as RLImage
import io

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Colors - LeaG76 style
PRIMARY_COLOR = HexColor('#2c2c2c')  # Dark gray
ACCENT_COLOR = HexColor('#666666')   # Medium gray
LIGHT_GRAY = HexColor('#f0f0f0')


def create_circular_image(image_path, size=100):
    """Create a circular cropped image for the profile."""
    from PIL import Image as PILImage, ImageDraw
    
    if not image_path or not os.path.exists(image_path):
        return None
    
    try:
        # Open and resize image
        img = PILImage.open(image_path).convert('RGB')
        img = img.resize((size, size))
        
        # Create circular mask
        mask = PILImage.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask
        output = PILImage.new('RGB', (size, size))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # Save to temp file
        temp_path = OUTPUT_DIR / f"temp_circular_{datetime.now().timestamp()}.png"
        output.save(temp_path, 'PNG')
        return str(temp_path)
    except Exception as e:
        print(f"Error creating circular image: {e}")
        return None


async def render_cv_pdf(data_dict: dict, image_path: str | None, filename: str) -> str:
    """
    Generate a professional CV PDF using LeaG76-inspired two-column layout.
    
    Args:
        data_dict: Dictionary containing all CV data
        image_path: Optional path to the profile image
        filename: Output filename
    
    Returns:
        Full path to the generated PDF file
    """
    output_path = OUTPUT_DIR / filename.replace('.html', '.pdf')
    
    try:
        # Page dimensions
        page_width, page_height = A4
        left_col_width = 7*cm
        right_col_width = page_width - left_col_width
        margin = 0
        
        # Create PDF
        pdf = canvas.Canvas(str(output_path), pagesize=A4)
        
        # Left column background (dark)
        pdf.setFillColor(HexColor('#2c2c2c'))
        pdf.rect(0, 0, left_col_width, page_height, fill=1, stroke=0)
        
        # Right column (white)
        pdf.setFillColor(white)
        pdf.rect(left_col_width, 0, right_col_width, page_height, fill=1, stroke=0)
        
        y_left = page_height - 2*cm
        y_right = page_height - 2*cm
        
        # === LEFT COLUMN ===
        left_x = 1*cm
        
        # Profile Image (circular)
        if image_path:
            circular_img = create_circular_image(image_path, 120)
            if circular_img:
                pdf.drawImage(circular_img, left_x, y_left - 4.5*cm, width=4*cm, height=4*cm, mask='auto')
                y_left -= 5*cm
        
        y_left -= 1*cm
        
        # Name
        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 18)
        name = data_dict.get('name', 'Unknown').upper()
        pdf.drawString(left_x, y_left, name)
        y_left -= 0.8*cm
        
        # Title
        pdf.setFont("Helvetica", 11)
        pdf.drawString(left_x, y_left, data_dict.get('title', ''))
        y_left -= 1.2*cm
        
        # Contact Info
        pdf.setFont("Helvetica", 9)
        pdf.drawString(left_x, y_left, data_dict.get('email', ''))
        y_left -= 0.5*cm
        pdf.drawString(left_x, y_left, data_dict.get('phone', ''))
        y_left -= 1*cm
        
        # PROFILE Section
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(left_x, y_left, "PROFILE")
        y_left -= 0.6*cm
        
        pdf.setFont("Helvetica", 8)
        profile_text = data_dict.get('profile_summary', '')
        # Wrap text
        max_width = left_col_width - 2*cm
        words = profile_text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if pdf.stringWidth(test_line, "Helvetica", 8) < max_width * 28.35:  # points
                line = test_line
            else:
                pdf.drawString(left_x, y_left, line.strip())
                y_left -= 0.4*cm
                line = word + " "
        if line:
            pdf.drawString(left_x, y_left, line.strip())
            y_left -= 0.8*cm
        
        # SKILLS Section
        if data_dict.get('skills'):
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(left_x, y_left, "SKILLS")
            y_left -= 0.6*cm
            
            pdf.setFont("Helvetica", 9)
            for skill in data_dict['skills'][:8]:
                pdf.drawString(left_x, y_left, f"• {skill['name']}")
                y_left -= 0.5*cm
            y_left -= 0.5*cm
        
        # LANGUAGES Section
        if data_dict.get('languages'):
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(left_x, y_left, "LANGUAGES")
            y_left -= 0.6*cm
            
            pdf.setFont("Helvetica", 9)
            for lang in data_dict['languages']:
                pdf.drawString(left_x, y_left, f"• {lang['name']}")
                y_left -= 0.5*cm
        
        # === RIGHT COLUMN ===
        right_x = left_col_width + 1.5*cm
        right_margin = right_x + (right_col_width - 3*cm)
        
        pdf.setFillColor(PRIMARY_COLOR)
        
        # EXPERIENCE Section
        if data_dict.get('experience'):
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(right_x, y_right, "EXPERIENCE")
            y_right -= 0.8*cm
            
            for exp in data_dict['experience']:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(right_x, y_right, exp.get('title', '').upper())
                y_right -= 0.5*cm
                
                pdf.setFont("Helvetica-Oblique", 9)
                pdf.drawString(right_x, y_right, f"{exp.get('company', '')} | {exp.get('years', '')}")
                y_right -= 0.5*cm
                
                pdf.setFont("Helvetica", 9)
                # Wrap description
                desc = exp.get('description', '')
                words = desc.split()
                line = ""
                max_w = (right_margin - right_x) / 28.35 * 72  # convert to points
                for word in words:
                    test = line + word + " "
                    if pdf.stringWidth(test, "Helvetica", 9) < max_w:
                        line = test
                    else:
                        pdf.drawString(right_x, y_right, line.strip())
                        y_right -= 0.4*cm
                        line = word + " "
                if line:
                    pdf.drawString(right_x, y_right, line.strip())
                y_right -= 0.8*cm
            
            y_right -= 0.5*cm
        
        # CERTIFICATES Section
        if data_dict.get('certificates'):
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(right_x, y_right, "CERTIFICATES")
            y_right -= 0.8*cm
            
            for cert in data_dict['certificates']:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(right_x, y_right, cert.get('year', ''))
                y_right -= 0.5*cm
                
                pdf.setFont("Helvetica", 9)
                pdf.drawString(right_x, y_right, cert.get('title', ''))
                if cert.get('honors'):
                    y_right -= 0.4*cm
                    pdf.drawString(right_x, y_right, cert['honors'])
                y_right -= 0.8*cm
            
            y_right -= 0.5*cm
        
        # EDUCATION Section
        if data_dict.get('education'):
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(right_x, y_right, "EDUCATION")
            y_right -= 0.8*cm
            
            for edu in data_dict['education']:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(right_x, y_right, edu.get('degree', ''))
                y_right -= 0.5*cm
                
                pdf.setFont("Helvetica", 9)
                pdf.drawString(right_x, y_right, f"{edu.get('institution', '')} - {edu.get('years', '')}")
                y_right -= 0.8*cm
        
        pdf.save()
        
        # Clean up temp circular image
        if image_path:
            circular_temp = OUTPUT_DIR / f"temp_circular_*.png"
            for temp_file in OUTPUT_DIR.glob("temp_circular_*.png"):
                try:
                    temp_file.unlink()
                except:
                    pass
        
        print(f"✅ PDF generated successfully: {output_path.name}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error generating PDF {filename}: {e}")
        import traceback
        traceback.print_exc()
        raise


def get_sample_cv_data() -> dict:
    """Return sample CV data for testing."""
    return {
        "name": "Lea Gallier",
        "title": "Analyst Developer",
        "email": "leagallier.lag@gmail.com",
        "phone": "06.11.45.11.65",
        "profile_summary": "I'm actually a student in computer science at the University of Le Havre Normandie. This year is my last year of master's degree in computer science at the university. But this year I also joined the IES Ingénierie team by becoming an analyst developer in work-study training.",
        "skills": [
            {"name": "Python", "level": 90},
            {"name": "JavaScript", "level": 85},
            {"name": "React", "level": 80},
            {"name": "Docker", "level": 75},
            {"name": "AWS", "level": 70},
        ],
        "languages": [
            {"name": "French", "level": 5},
            {"name": "English", "level": 4},
        ],
        "experience": [
            {
                "title": "Analyst Programmer",
                "company": "Sandwichcourse | IES Ingénierie",
                "years": "October 2022 - present",
                "description": "Work in this company dedicating the best responsibility in the area that corresponds, delivering the best results for the company and improving productivity."
            },
            {
                "title": "Analyst Programmer",
                "company": "Internship | IES Ingénierie",
                "years": "April 2021 - June 2021",
                "description": "Work in this company dedicating the best responsibility in the area that corresponds, delivering the best results for the company and improving productivity."
            }
        ],
        "education": [
            {
                "degree": "Masters in Computer Science",
                "institution": "Université Le Havre Normandie",
                "years": "2021 - 2023"
            },
            {
                "degree": "Bachelor in Computer Science",
                "institution": "Université Le Havre Normandie",
                "years": "2018 - 2021"
            },
            {
                "degree": "High School diploma in Sciences, speciality Mathematics",
                "institution": "Lycée Guillaume Le Conquérant",
                "years": "with honours"
            }
        ],
        "certificates": [
            {"year": "2023", "title": "Masters in Computer Science", "honors": "with honours"},
            {"year": "2021", "title": "Bachelor in Computer Science", "honors": "with honours"},
            {"year": "2018", "title": "High School diploma in Sciences, speciality Mathematics", "honors": "with honours"}
        ]
    }
