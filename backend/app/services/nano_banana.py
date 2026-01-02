"""
Nano Banana Service - Avatar Image Generation Handler
Mock implementation with architecture ready for real API integration
"""

import asyncio
import os
import random
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import httpx

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = BACKEND_DIR / "assets"

# Ensure assets directory exists
ASSETS_DIR.mkdir(exist_ok=True)

# Color palettes for different ethnicities (used in mock mode)
SKIN_TONES = {
    "asian": ["#f5d0b0", "#e8c49a", "#d4a574", "#c99a5b"],
    "caucasian": ["#ffe0bd", "#ffcd94", "#eac086", "#ffad60"],
    "african": ["#8d5524", "#6b4423", "#4a3728", "#3b2f2f"],
    "hispanic": ["#d4a574", "#c68642", "#a67c52", "#8b6914"],
    "middle-eastern": ["#c68642", "#b5651d", "#a0522d", "#8b4513"],
    "mixed": ["#d4a574", "#c99a5b", "#b5651d", "#a67c52"],
    "any": ["#d4a574", "#e8c49a", "#c68642", "#b5651d"]
}

# Background colors
BG_COLORS = ["#3498db", "#2ecc71", "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c"]


async def generate_avatar(
    gender: str = "any",
    ethnicity: str = "any",
    age_range: str = "25-45",
    origin: str = "any"
) -> str:
    """
    Generate an avatar image for a CV.
    
    In mock mode, creates a stylized placeholder avatar.
    When real API is available, will call Nano Banana API.
    
    Args:
        gender: "male", "female", or "any"
        ethnicity: Ethnicity category for appropriate representation
        age_range: Age range like "25-45"
        origin: Geographic origin
    
    Returns:
        Path to the generated image file
    """
    # Check if mock mode
    mock_mode = os.getenv("NANO_BANANA_MOCK", "true").lower() == "true"
    api_key = os.getenv("NANO_BANANA_API_KEY", "")
    
    if mock_mode or not api_key:
        return await _generate_mock_avatar(gender, ethnicity, age_range, origin)
    else:
        return await _call_nano_banana_api(gender, ethnicity, age_range, origin, api_key)


async def _generate_mock_avatar(
    gender: str,
    ethnicity: str,
    age_range: str,
    origin: str
) -> str:
    """
    Generate a stylized placeholder avatar.
    Creates a simple but distinctive image so PDFs look professional.
    """
    # Simulate network delay (4-8 seconds as specified)
    delay = random.uniform(4, 8)
    await asyncio.sleep(delay)
    
    # Create image
    size = (400, 400)
    
    # Select colors based on ethnicity
    skin_tones = SKIN_TONES.get(ethnicity.lower(), SKIN_TONES["any"])
    skin_color = random.choice(skin_tones)
    bg_color = random.choice(BG_COLORS)
    
    # Create image with gradient background
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple avatar silhouette
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Head (circle)
    head_radius = 80
    head_box = [
        center_x - head_radius,
        center_y - 100 - head_radius,
        center_x + head_radius,
        center_y - 100 + head_radius
    ]
    draw.ellipse(head_box, fill=skin_color)
    
    # Body (rounded rectangle / ellipse)
    body_width = 140
    body_height = 180
    body_box = [
        center_x - body_width // 2,
        center_y - 20,
        center_x + body_width // 2,
        center_y + body_height
    ]
    draw.ellipse(body_box, fill=skin_color)
    
    # Add gender indicator (subtle)
    if gender.lower() == "female":
        # Longer hair indication
        hair_color = "#2c1810" if ethnicity.lower() in ["asian", "african", "hispanic"] else "#8b4513"
        hair_box = [
            center_x - head_radius - 10,
            center_y - 100 - head_radius - 5,
            center_x + head_radius + 10,
            center_y - 60
        ]
        draw.ellipse(hair_box, fill=hair_color)
        # Redraw head on top
        draw.ellipse(head_box, fill=skin_color)
    elif gender.lower() == "male":
        # Short hair
        hair_color = "#2c1810" if ethnicity.lower() in ["asian", "african", "hispanic"] else "#654321"
        hair_box = [
            center_x - head_radius,
            center_y - 100 - head_radius - 5,
            center_x + head_radius,
            center_y - 100 - head_radius + 30
        ]
        draw.ellipse(hair_box, fill=hair_color)
    
    # Add subtle facial features
    eye_y = center_y - 110
    left_eye_x = center_x - 25
    right_eye_x = center_x + 25
    eye_radius = 8
    
    # Eyes
    draw.ellipse([left_eye_x - eye_radius, eye_y - eye_radius, 
                  left_eye_x + eye_radius, eye_y + eye_radius], fill="#2c2c2c")
    draw.ellipse([right_eye_x - eye_radius, eye_y - eye_radius, 
                  right_eye_x + eye_radius, eye_y + eye_radius], fill="#2c2c2c")
    
    # Simple smile
    smile_box = [center_x - 20, center_y - 90, center_x + 20, center_y - 70]
    draw.arc(smile_box, start=0, end=180, fill="#2c2c2c", width=3)
    
    # Generate unique filename
    filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
    filepath = ASSETS_DIR / filename
    
    # Save image
    img = img.convert('RGB')
    img.save(str(filepath), 'JPEG', quality=90)
    
    return str(filepath)


async def _call_nano_banana_api(
    gender: str,
    ethnicity: str,
    age_range: str,
    origin: str,
    api_key: str
) -> str:
    """
    Call the real Nano Banana API for avatar generation.
    This is a placeholder for real API integration.
    """
    # This would be the real API call when Nano Banana is available
    # For now, fall back to mock if API call fails
    
    api_url = os.getenv("NANO_BANANA_API_URL", "https://api.nanobanana.ai/v1/generate")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": f"Professional headshot portrait photo of a {age_range} year old {gender} {ethnicity} person from {origin}, business attire, neutral background, high quality",
                    "style": "photorealistic",
                    "size": "400x400"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result.get("image_url")
                
                if image_url:
                    # Download the image
                    img_response = await client.get(image_url)
                    if img_response.status_code == 200:
                        filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
                        filepath = ASSETS_DIR / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        return str(filepath)
            
            # Fallback to mock
            return await _generate_mock_avatar(gender, ethnicity, age_range, origin)
            
    except Exception as e:
        print(f"Nano Banana API error: {e}")
        # Fallback to mock on any error
        return await _generate_mock_avatar(gender, ethnicity, age_range, origin)


def get_placeholder_avatar() -> str:
    """
    Get or create a default placeholder avatar.
    Used as fallback when all generation methods fail.
    """
    placeholder_path = ASSETS_DIR / "placeholder.jpg"
    
    if not placeholder_path.exists():
        # Create a simple gray placeholder
        img = Image.new('RGB', (400, 400), '#808080')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple avatar silhouette
        center_x, center_y = 200, 200
        
        # Head
        draw.ellipse([120, 60, 280, 220], fill="#a0a0a0")
        # Body
        draw.ellipse([80, 200, 320, 400], fill="#a0a0a0")
        
        img.save(str(placeholder_path), 'JPEG', quality=90)
    
    return str(placeholder_path)
