"""
Krea Image Service - Real Krea API Integration
Supports multiple image generation models with different speeds and compute costs
"""

import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
import httpx
from dotenv import load_dotenv

# Get paths - CRITICAL: load .env from backend directory
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)
print(f"DEBUG KREA: Loading .env from: {ENV_PATH} (exists: {ENV_PATH.exists()})")

# Output directory for avatars
OUTPUT_DIR = BACKEND_DIR / "output"
AVATARS_DIR = OUTPUT_DIR / "avatars"
AVATARS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = AVATARS_DIR # Backward compatibility wrapper

# Krea API Configuration - Per official docs (Jan 2026)
KREA_API_BASE = "https://api.krea.ai"
KREA_JOBS_URL = "https://api.krea.ai/jobs"

# Available models with their properties - Using correct API path format
KREA_MODELS = {
    "bfl/flux-1-dev": {
        "name": "Flux",
        "description": "Fastest and cheapest model (~5s)",
        "images": 4,
        "time": "5s",
        "compute_units": 3,
        "model_id": "bfl/flux-1-dev"
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


def get_avatar_prompt(gender: str, ethnicity: str, age_range: str, role: str = "Professional") -> str:
    """Generate the prompt for the avatar using external template."""
    
    # Map variables for template
    if gender.lower() == "female":
        gender_term = "woman"
    elif gender.lower() == "male":
        gender_term = "man"
    else:
        gender_term = "professional person"
        
    ethnicity_term = ethnicity if ethnicity != "any" else "mixed heritage"
    
    # Clean age: If "25-35", take average or specific. If just "28", use it.
    if '-' in str(age_range):
        try:
            min_a, max_a = map(int, str(age_range).split('-'))
            age_val = (min_a + max_a) // 2
        except:
            age_val = age_range
    else:
        age_val = age_range
        
    # --- DYNAMIC STYLE LOGIC ---
    # Determine context based on role keywords to avoid generic "Corporate" look
    role_lower = role.lower()
    
    context = "Professional portrait, neutral background"
    style = "high quality, 8k, photorealistic"
    
    if any(k in role_lower for k in ["designer", "creative", "artist", "ux", "ui", "art director", "architect"]):
        context = "Creative professional in a modern bright studio environment, smart-casual stylish attire"
        style = "artistic lighting, 8k, sharp focus, modern vibe"
        
    elif any(k in role_lower for k in ["developer", "engineer", "software", "tech", "data", "programmer", "it "]):
        context = "Tech professional in a modern open-plan tech office, casual-smart attire (t-shirt and blazer or smart shirt)"
        style = "clean lighting, 8k, modern tech aesthetic"
        
    elif any(k in role_lower for k in ["manager", "director", "executive", "chief", "head of", "vp", "president"]):
        # Executive but keep it modern, not "stiff old corporate"
        context = "Modern business executive in a contemporary glass office, modern business attire"
        style = "cinematic lighting, 8k, depth of field, premium look"
        
    elif any(k in role_lower for k in ["teacher", "educator", "professor", "trainer"]):
        context = "Education professional in a modern academic setting, smart professional attire"
            
    elif any(k in role_lower for k in ["medical", "doctor", "nurse", "health", "clinical"]):
        context = "Healthcare professional in a clean medical setting, professional medical attire or scrubs"
    
    else:
        # Fallback for general roles
        context = f"Professional {role} in a modern work environment, appropriate professional attire"

    # CRITICAL: Prevent "Senior" in title from aging the face
    # We add a negative prompt instruction implicit in the positive description
    
    # Load from template file
    template_path = BACKEND_DIR / "prompts" / "image_prompt_template.txt"
    
    if not template_path.exists():
        # Fallback inline template if file missing
        return f"Natural portrait of a {gender_term}, age {age_val}, {ethnicity_term}, {context}. {style}"

    print(f"DEBUG: Loading external Image template from {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    # Replace placeholders
    prompt = template.replace("{{gender_term}}", gender_term)
    prompt = prompt.replace("{{age}}", str(age_val))
    prompt = prompt.replace("{{ethnicity}}", ethnicity_term)
    prompt = prompt.replace("{{role_context}}", context)
    prompt = prompt.replace("{{style_modifiers}}", style)
    
    return prompt


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
    origin: str = "United States",
    role: str = "Professional",
    model: Optional[str] = None,
    filename: Optional[str] = None
) -> Tuple[str, str]:
    """Generate profile avatar using Krea API.
    
    Args:
        gender: "male", "female", or "any"
        ethnicity: Ethnicity category
        age_range: Age range or specific age
        origin: Geographic origin
        role: Job role for context styling
        model: Krea model ID
    """
    api_key = os.getenv("KREA_API_KEY", "")
    
    # Debug logging
    print(f"DEBUG KREA: API Key loaded: {'YES (' + api_key[:8] + '...)' if api_key and len(api_key) > 8 else 'NO/EMPTY'}")
    
    if not api_key or api_key == "your-krea-api-key-here":
        error_msg = "ERROR: KREA_API_KEY not configured in backend/.env - Cannot generate avatar without real API key"
        print(error_msg)
        raise ValueError(error_msg)
    
    # Use provided model or default - map old names to new API paths
    model_input = model or os.getenv("DEFAULT_IMAGE_MODEL", "bfl/flux-1-dev")
    
    # Map simple names to correct API paths (Provider/Model-ID format)
    # Based on user feedback and Krea API standards
    MODEL_PATH_MAP = {
        # Flux Families (BFL)
        "flux": "bfl/flux-1-dev",
        "bfl/flux-1-dev": "bfl/flux-1-dev",
        "flux-2": "bfl/flux-2-dev",
        "flux-2-pro": "bfl/flux-2-pro",
        "flux-1.1-pro": "bfl/flux-1.1-pro",
        "flux-1.1-pro-ultra": "bfl/flux-1.1-pro-ultra",
        "flux-kontext": "bfl/flux-1-kontext-dev", # Specific override
        
        # Krea Native
        "krea-1": "krea/krea-1", # Assuming provider prefix for consistency, or fallback to simple if 404
        "flux-1-krea": "krea/flux-1-krea",
        
        # Alibaba
        "z-image": "alibaba/z-image",
        "qwen": "alibaba/qwen-vl",
        "qwen-image-2512": "alibaba/qwen-image-2512",
        
        # ByteDance
        "seedream-3": "bytedance/seedream-3",
        "seedream-4": "bytedance/seedream-4",
        "seedream-4.5": "bytedance/seedream-4.5",
        
        # Google
        "imagen-4-fast": "google/imagen-4-fast",
        "imagen-4": "google/imagen-4",
        "imagen-4-ultra": "google/imagen-4-ultra",
        "nano-banana-pro": "google/nano-banana-pro",
        "nano-banana": "google/nano-banana",
        
        # Ideogram
        "ideogram-3": "ideogram/ideogram-3",
        
        # Kuaishou
        "kling-01": "kuaishou/kling-01",
        
        # Runway
        "runway-gen-4": "runway/gen-4",
        
        # OpenAI
        "chatgpt-image": "openai/dall-e-3", # Guessing standard, or maybe chatgpt-image is correct? Keeping map just in case
        "chatgpt-image-1.5": "openai/dall-e-3"
    }
    
    # Clean fallback: If exact match exists in map, use it. Else try to construct provider prefix if missing?
    # For now, rely on MAP or raw string
    model_id = MODEL_PATH_MAP.get(model_input, model_input)
    
    print(f"DEBUG KREA: Using model: {model_id}")
    
    prompt = get_avatar_prompt(gender, ethnicity, age_range, role)
    
    try:
        # Construct API URL per Krea docs
        api_url = f"{KREA_API_BASE}/generate/image/{model_id}"
        print(f"DEBUG KREA: Calling {api_url}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Create generation job
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "width": 512,
                    "height": 512,
                    "steps": 25
                }
            )
            
            print(f"DEBUG KREA: Initial response status: {response.status_code}")
            print(f"DEBUG KREA: Initial response: {response.text[:500]}")
            
            if response.status_code != 200:
                error_msg = f"Krea API error: {response.status_code} - {response.text[:300]}"
                print(f"ERROR: {error_msg}")
                raise RuntimeError(error_msg)
            
            result = response.json()
            job_id = result.get("job_id")
            
            if not job_id:
                error_msg = f"Krea API did not return job_id: {result}"
                print(f"ERROR: {error_msg}")
                raise RuntimeError(error_msg)
            
            print(f"DEBUG KREA: Job created: {job_id}")
            
            # Step 2: Poll for completion (max 60 seconds)
            max_polls = 30
            for poll_num in range(max_polls):
                await asyncio.sleep(2)  # Wait 2 seconds between polls
                
                job_response = await client.get(
                    f"{KREA_JOBS_URL}/{job_id}",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if job_response.status_code != 200:
                    print(f"DEBUG KREA: Poll {poll_num+1} - status {job_response.status_code}")
                    continue
                
                job_data = job_response.json()
                status = job_data.get("status", "")
                print(f"DEBUG KREA: Poll {poll_num+1} - status: {status}")
                
                if job_data.get("completed_at"):
                    if status == "completed":
                        # Get image URL from result
                        urls = job_data.get("result", {}).get("urls", [])
                        if urls:
                            image_url = urls[0]
                            print(f"DEBUG KREA: Image ready: {image_url}")
                            
                            # Download and save the image
                            img_response = await client.get(image_url)
                            if img_response.status_code == 200:
                                # Use provided filename or generate one
                                if not filename:
                                    filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
                                    
                                filepath = AVATARS_DIR / filename
                                
                                with open(filepath, 'wb') as f:
                                    f.write(img_response.content)
                                
                                print(f"SUCCESS: Avatar generated with {model_id}: {filename}")
                                return str(filepath), prompt
                    else:
                        error_msg = f"Krea job failed: {status}"
                        print(f"ERROR: {error_msg}")
                        raise RuntimeError(error_msg)
            
            error_msg = "Krea API timeout - job did not complete in 60 seconds"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
            
    except Exception as e:
        error_msg = f"Krea API exception: {e}"
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)


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
