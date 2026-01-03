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

# Available models with their properties - VERIFIED in Krea OpenAPI spec
KREA_MODELS = {
    "bfl/flux-1-dev": {
        "name": "Flux",
        "description": "Fastest and cheapest model (~5s)",
        "images": 4,
        "time": "5s",
        "compute_units": 3,
        "model_id": "bfl/flux-1-dev"
    },
    "seedream-3": {
        "name": "Seedream 3",
        "description": "Fast, high-quality model from ByteDance (~5s)",
        "images": 2,
        "time": "5s",
        "compute_units": 24,
        "model_id": "seedream-3"
    },
    "seedream-4": {
        "name": "Seedream 4",
        "description": "High quality for photorealism (~20s)",
        "images": 2,
        "time": "20s",
        "compute_units": 24,
        "model_id": "seedream-4"
    },
    "imagen-4-fast": {
        "name": "Imagen 4 Fast",
        "description": "Google's fastest image model (~17s)",
        "images": 2,
        "time": "17s",
        "compute_units": 16,
        "model_id": "imagen-4-fast"
    },
    "imagen-4": {
        "name": "Imagen 4",
        "description": "Google's current generation model (~32s)",
        "images": 2,
        "time": "32s",
        "compute_units": 32,
        "model_id": "imagen-4"
    },
    "imagen-4-ultra": {
        "name": "Imagen 4 Ultra",
        "description": "Google's best image model (~30s)",
        "images": 2,
        "time": "30s",
        "compute_units": 47,
        "model_id": "imagen-4-ultra"
    },
    "flux-1.1-pro": {
        "name": "Flux 1.1 Pro",
        "description": "Advanced efficient model from BFL (~11s)",
        "images": 2,
        "time": "11s",
        "compute_units": 31,
        "model_id": "flux-1.1-pro"
    },
    "flux-1.1-pro-ultra": {
        "name": "Flux 1.1 Pro Ultra",
        "description": "BFL's highest quality model (~18s)",
        "images": 2,
        "time": "18s",
        "compute_units": 47,
        "model_id": "flux-1.1-pro-ultra"
    },
    "flux-kontext": {
        "name": "Flux Kontext",
        "description": "Image editing optimized (~5s)",
        "images": 2,
        "time": "5s",
        "compute_units": 6,
        "model_id": "flux-kontext"
    },
    "ideogram-3": {
        "name": "Ideogram 3.0",
        "description": "Highly aesthetic, general-purpose (~18s)",
        "images": 2,
        "time": "18s",
        "compute_units": 54,
        "model_id": "ideogram-3"
    },
    "nano-banana": {
        "name": "Nano Banana",
        "description": "Smart model for image editing (~10s)",
        "images": 2,
        "time": "10s",
        "compute_units": 32,
        "model_id": "nano-banana"
    },
    "nano-banana-pro": {
        "name": "Nano Banana Pro",
        "description": "4K generation and editing (~30s)",
        "images": 2,
        "time": "30s",
        "compute_units": 119,
        "model_id": "nano-banana-pro"
    },
    "chatgpt-image": {
        "name": "ChatGPT Image",
        "description": "Best prompt adherence (~60s)",
        "images": 2,
        "time": "60s",
        "compute_units": 184,
        "model_id": "chatgpt-image"
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
        gender_term = "person"
        
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
        
    # --- CLEAN ROLE LOGIC ---
    # AGGRESSIVELY remove ALL age-biasing words from role
    # This is CRITICAL to prevent "Senior Software Engineer" from making the image look old
    import re
    forbidden_patterns = [
        r'\bsenior\b', r'\blead\b', r'\bprincipal\b', r'\bchief\b', 
        r'\bhead\s*of\b', r'\bexecutive\b', r'\bvp\b', r'\bdirector\b',
        r'\bmanager\b', r'\bsr\.?\b', r'\bjr\.?\b'
    ]
    
    cleaned_role = role
    for pattern in forbidden_patterns:
        cleaned_role = re.sub(pattern, '', cleaned_role, flags=re.IGNORECASE)
    
    # Clean up extra spaces and capitalize
    cleaned_role = ' '.join(cleaned_role.split()).strip()
    
    # If role becomes empty/too short after cleaning, use generic
    if len(cleaned_role) < 3:
        cleaned_role = "Professional"
    else:
        cleaned_role = cleaned_role.title()
        
    # --- DYNAMIC STYLE LOGIC ---
    # Use CLEANED role for context matching (not raw role!)
    # STRICTLY AVOID "OFFICE", "CORPORATE", "EXECUTIVE"
    role_lower = cleaned_role.lower()
    
    # Default context - neutral and modern
    context = "modern casual-professional style"
    style = "high quality, 8k, photorealistic"
    
    if any(k in role_lower for k in ["designer", "creative", "artist", "ux", "ui", "art", "architect"]):
        context = "creative professional, stylish modern attire"
        style = "artistic lighting, 8k, sharp focus, modern vibe"
        
    elif any(k in role_lower for k in ["developer", "engineer", "software", "tech", "data", "programmer"]):
        context = "tech professional, smart-casual attire"
        style = "clean lighting, 8k, modern aesthetic"
        
    elif any(k in role_lower for k in ["teacher", "educator", "professor", "trainer"]):
        context = "educator, smart professional attire"
            
    elif any(k in role_lower for k in ["medical", "doctor", "nurse", "health", "clinical"]):
        context = "healthcare professional, medical attire"
    
    # NO FALLBACK that adds role name - keep it pure
    # The role is already in the CV, the image just needs age/ethnicity/gender

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
    # Use context + cleaned_role implied context
    prompt = prompt.replace("{{role_context}}", context)
    prompt = prompt.replace("{{style_modifiers}}", style)
    
    # DEBUG: Log what we're sending
    print("="*60)
    print("DEBUG IMAGE PROMPT PARAMETERS:")
    print(f"  Gender: {gender} -> {gender_term}")
    print(f"  Age: {age_range} -> {age_val}")
    print(f"  Ethnicity: {ethnicity} -> {ethnicity_term}")
    print(f"  Role (Raw): {role}")
    print(f"  Role (Cleaned): {cleaned_role}")
    print(f"  Context: {context}")
    print(f"  Style: {style}")
    print(f"  Prompt Length: {len(prompt)} chars")
    print("="*60)
    
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
        # Flux Families (BFL) - Verified in OpenAPI spec
        "flux": "bfl/flux-1-dev",
        "bfl/flux-1-dev": "bfl/flux-1-dev",
        "flux-1.1-pro": "bfl/flux-1.1-pro",
        "flux-1.1-pro-ultra": "bfl/flux-1.1-pro-ultra",
        "flux-kontext": "bfl/flux-1-kontext-dev",
        "bfl/flux-1-kontext-dev": "bfl/flux-1-kontext-dev",
        
        # ByteDance - Verified in OpenAPI spec
        "seedream-3": "bytedance/seedream-3",
        "seedream-4": "bytedance/seedream-4",
        
        # Google - Verified in OpenAPI spec
        "imagen-3": "google/imagen-3",
        "imagen-4-fast": "google/imagen-4-fast",
        "imagen-4": "google/imagen-4",
        "imagen-4-ultra": "google/imagen-4-ultra",
        "nano-banana-pro": "google/nano-banana-pro",
        "nano-banana": "google/nano-banana",
        
        # Ideogram - Verified in OpenAPI spec
        "ideogram-3": "ideogram/ideogram-3",
        "ideogram-2-turbo": "ideogram/ideogram-2-turbo",
        
        # OpenAI - Verified in OpenAPI spec
        "chatgpt-image": "openai/gpt-image",
        "gpt-image": "openai/gpt-image",
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
            # Build request body based on model requirements (from OpenAPI spec)
            request_body = {
                "prompt": prompt,
                "width": 512,
                "height": 512
            }
            
            # Model-specific parameters from OpenAPI spec
            if "seedream-3" in model_id:
                # Seedream-3 requires specific model parameter
                request_body["model"] = "seedream-3-0-t2i-250415"
            elif "seedream-4" in model_id:
                # Seedream-4 requires width and height (already included)
                pass
            elif "flux" in model_id.lower():
                # Flux models support steps
                request_body["steps"] = 25
            # Other models use default prompt/width/height
            
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=request_body

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
