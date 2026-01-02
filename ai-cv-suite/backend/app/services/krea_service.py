"""
Krea Image Service - Real Krea API Integration
Supports multiple image generation models with different speeds and compute costs
"""

import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = BACKEND_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# Krea API Configuration
KREA_API_URL = "https://api.krea.ai/v1/images/generations"

# Available models with their properties
KREA_MODELS = {
    "flux": {
        "name": "Flux",
        "description": "Fastest and cheapest model",
        "images": 4,
        "time": "5s",
        "compute_units": 3,
        "model_id": "flux"
    },
    "krea-1": {
        "name": "Krea 1",
        "description": "Fast creative model, best for aesthetic images and photorealism",
        "images": 4,
        "time": "8s",
        "compute_units": 6,
        "model_id": "krea-1"
    },
    "flux-1-krea": {
        "name": "Flux.1 Krea",
        "description": "Distilled and open sourced version of Krea 1",
        "images": 4,
        "time": "8s",
        "compute_units": 5,
        "model_id": "flux-1-krea"
    },
    "z-image": {
        "name": "Z Image",
        "description": "Fast high quality image model from Alibaba",
        "images": 2,
        "time": "5s",
        "compute_units": 2,
        "model_id": "z-image"
    },
    "seedream-3": {
        "name": "Seedream 3",
        "description": "New fast, high-quality model from ByteDance",
        "images": 2,
        "time": "5s",
        "compute_units": 24,
        "model_id": "seedream-3"
    },
    "seedream-4": {
        "name": "Seedream 4",
        "description": "High quality model for photorealism and text rendering",
        "images": 2,
        "time": "20s",
        "compute_units": 24,
        "model_id": "seedream-4"
    },
    "seedream-4.5": {
        "name": "Seedream 4.5",
        "description": "Latest high quality model for photorealism and text rendering",
        "images": 2,
        "time": "20s",
        "compute_units": 32,
        "model_id": "seedream-4.5"
    },
    "imagen-4-fast": {
        "name": "Imagen 4 Fast",
        "description": "Google's fastest image model",
        "images": 2,
        "time": "17s",
        "compute_units": 16,
        "model_id": "imagen-4-fast"
    },
    "imagen-4": {
        "name": "Imagen 4",
        "description": "Google's current generation image model",
        "images": 2,
        "time": "32s",
        "compute_units": 32,
        "model_id": "imagen-4"
    },
    "imagen-4-ultra": {
        "name": "Imagen 4 Ultra",
        "description": "Google's best image model",
        "images": 2,
        "time": "30s",
        "compute_units": 47,
        "model_id": "imagen-4-ultra"
    },
    "flux-2": {
        "name": "Flux 2",
        "description": "FLUX.2 [dev] with enhanced realism and native editing",
        "images": 2,
        "time": "10s",
        "compute_units": 20,
        "model_id": "flux-2"
    },
    "flux-2-pro": {
        "name": "Flux 2 Pro",
        "description": "BFL's next generation model with improved quality",
        "images": 2,
        "time": "15s",
        "compute_units": 60,
        "model_id": "flux-2-pro"
    },
    "qwen": {
        "name": "Qwen",
        "description": "Great text rendering and prompt adherence",
        "images": 2,
        "time": "15s",
        "compute_units": 9,
        "model_id": "qwen"
    },
    "qwen-image-2512": {
        "name": "Qwen Image 2512",
        "description": "Enhanced realism, finer natural detail, and improved text rendering",
        "images": 2,
        "time": "15s",
        "compute_units": 9,
        "model_id": "qwen-image-2512"
    },
    "ideogram-3": {
        "name": "Ideogram 3.0",
        "description": "Highly aesthetic, general-purpose model",
        "images": 2,
        "time": "18s",
        "compute_units": 54,
        "model_id": "ideogram-3"
    },
    "kling-01": {
        "name": "Kling O1",
        "description": "High quality image model with reference support",
        "images": 2,
        "time": "30s",
        "compute_units": 22,
        "model_id": "kling-01"
    },
    "runway-gen-4": {
        "name": "Runway Gen-4",
        "description": "Cinematic image model with references",
        "images": 2,
        "time": "60s",
        "compute_units": 40,
        "model_id": "runway-gen-4"
    },
    "flux-1.1-pro": {
        "name": "Flux 1.1 Pro",
        "description": "Advanced yet efficient model from BFL",
        "images": 2,
        "time": "11s",
        "compute_units": 31,
        "model_id": "flux-1.1-pro"
    },
    "flux-1.1-pro-ultra": {
        "name": "Flux 1.1 Pro Ultra",
        "description": "BFL's highest quality text to image model",
        "images": 2,
        "time": "18s",
        "compute_units": 47,
        "model_id": "flux-1.1-pro-ultra"
    },
    "flux-kontext": {
        "name": "Flux Kontext",
        "description": "Frontier model designed for image editing, optimized for Krea",
        "images": 2,
        "time": "5s",
        "compute_units": 6,
        "model_id": "flux-kontext"
    },
    "flux-kontext-pro": {
        "name": "Flux Kontext Pro",
        "description": "Frontier model designed for image editing",
        "images": 2,
        "time": "16s",
        "compute_units": 32,
        "model_id": "flux-kontext-pro"
    },
    "wan-2.2": {
        "name": "Wan 2.2",
        "description": "Slow model with great ultra-realistic textures for aesthetic outputs",
        "images": 2,
        "time": "20s",
        "compute_units": 30,
        "model_id": "wan-2.2"
    },
    "chatgpt-image": {
        "name": "ChatGPT Image",
        "description": "Highest quality with best prompt adherence, ideal for logos, icons, and text",
        "images": 2,
        "time": "60s",
        "compute_units": 184,
        "model_id": "chatgpt-image"
    },
    "chatgpt-image-1.5": {
        "name": "ChatGPT Image 1.5",
        "description": "Highest quality with best prompt adherence, ideal for logos, icons, and text",
        "images": 2,
        "time": "60s",
        "compute_units": 184,
        "model_id": "chatgpt-image-1.5"
    },
    "nano-banana": {
        "name": "Nano Banana",
        "description": "Smart model, best for image editing",
        "images": 2,
        "time": "10s",
        "compute_units": 32,
        "model_id": "nano-banana"
    },
    "nano-banana-pro": {
        "name": "Nano Banana Pro",
        "description": "Newer model with native 4K image generation and editing capabilities",
        "images": 2,
        "time": "30s",
        "compute_units": 119,
        "model_id": "nano-banana-pro"
    }
}


def get_available_models() -> list[dict]:
    """Return list of available image models with their properties."""
    return [
        {
            "id": model_id,
            **model_info
        }
        for model_id, model_info in KREA_MODELS.items()
    ]


async def generate_avatar(
    gender: str = "any",
    ethnicity: str = "any",
    age_range: str = "25-45",
    origin: str = "any",
    model: Optional[str] = None
) -> str:
    """
    Generate an avatar image using Krea API.
    
    Args:
        gender: "male", "female", or "any"
        ethnicity: Ethnicity category for appropriate representation
        age_range: Age range like "25-45"
        origin: Geographic origin
        model: Krea model ID to use (defaults to env var DEFAULT_IMAGE_MODEL)
    
    Returns:
        Path to the generated image file
    """
    api_key = os.getenv("KREA_API_KEY", "")
    
    if not api_key or api_key == "your-krea-api-key-here":
        print("⚠️ No Krea API key found, using mock avatar")
        return await _generate_mock_avatar(gender, ethnicity)
    
    # Use provided model or default
    model_id = model or os.getenv("DEFAULT_IMAGE_MODEL", "flux")
    
    # Build the prompt for professional headshot
    gender_text = gender if gender != "any" else "professional"
    ethnicity_text = f"{ethnicity} " if ethnicity != "any" else ""
    
    prompt = (
        f"Professional corporate headshot portrait of a {age_range} year old "
        f"{gender_text} {ethnicity_text}person, "
        f"business attire, neutral studio background, high quality photography, "
        f"LinkedIn profile photo style, well-lit, sharp focus, friendly expression"
    )
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                KREA_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Get the image URL from response
                if "data" in result and len(result["data"]) > 0:
                    image_data = result["data"][0]
                    image_url = image_data.get("url") or image_data.get("image_url")
                    
                    if image_url:
                        # Download and save the image
                        img_response = await client.get(image_url)
                        if img_response.status_code == 200:
                            filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
                            filepath = ASSETS_DIR / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            
                            print(f"✅ Avatar generated with {model_id}: {filename}")
                            return str(filepath)
                
                # If we got here, try to extract image differently (Krea API variations)
                if "image" in result:
                    # Base64 encoded image
                    import base64
                    image_data = base64.b64decode(result["image"])
                    filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
                    filepath = ASSETS_DIR / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    
                    return str(filepath)
            
            print(f"⚠️ Krea API error: {response.status_code} - {response.text[:200]}")
            return await _generate_mock_avatar(gender, ethnicity)
            
    except Exception as e:
        print(f"⚠️ Krea API exception: {e}")
        return await _generate_mock_avatar(gender, ethnicity)


async def _generate_mock_avatar(gender: str, ethnicity: str) -> str:
    """Generate a mock avatar when API is unavailable."""
    from PIL import Image, ImageDraw
    import random
    
    # Simulate some delay
    await asyncio.sleep(random.uniform(1, 2))
    
    # Color palettes for different ethnicities
    SKIN_TONES = {
        "asian": ["#f5d0b0", "#e8c49a", "#d4a574"],
        "caucasian": ["#ffe0bd", "#ffcd94", "#eac086"],
        "african": ["#8d5524", "#6b4423", "#4a3728"],
        "hispanic": ["#d4a574", "#c68642", "#a67c52"],
        "middle-eastern": ["#c68642", "#b5651d", "#a0522d"],
        "any": ["#d4a574", "#e8c49a", "#c68642"]
    }
    
    BG_COLORS = ["#3498db", "#2ecc71", "#9b59b6", "#e74c3c", "#1abc9c"]
    
    size = (400, 400)
    skin_tones = SKIN_TONES.get(ethnicity.lower(), SKIN_TONES["any"])
    skin_color = random.choice(skin_tones)
    bg_color = random.choice(BG_COLORS)
    
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = 200, 200
    
    # Head
    draw.ellipse([120, 60, 280, 220], fill=skin_color)
    # Body  
    draw.ellipse([80, 200, 320, 400], fill=skin_color)
    # Eyes
    draw.ellipse([155, 120, 175, 140], fill="#2c2c2c")
    draw.ellipse([225, 120, 245, 140], fill="#2c2c2c")
    # Smile
    draw.arc([160, 140, 240, 180], start=0, end=180, fill="#2c2c2c", width=3)
    
    filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
    filepath = ASSETS_DIR / filename
    img.save(str(filepath), 'JPEG', quality=90)
    
    return str(filepath)
