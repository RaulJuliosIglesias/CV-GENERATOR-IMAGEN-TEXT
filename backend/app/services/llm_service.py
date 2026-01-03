"""
LLM Service - OpenRouter Integration for CV Content Generation
Enhanced with detailed prompts for comprehensive CVs
"""

import os
import json
import random
import asyncio
from typing import Optional, Tuple
import httpx
from dotenv import load_dotenv
from pathlib import Path
from jinja2 import Template

# CRITICAL: Load .env from backend directory, not CWD
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)
print(f"DEBUG: Loading .env from: {ENV_PATH} (exists: {ENV_PATH.exists()})")

# OpenRouter API Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Fallback models in case API fetch fails
FALLBACK_LLM_MODELS = {
    "openrouter/auto": {
        "name": "Auto (Best Model)",
        "description": "Automatically selects the best model for your prompt",
        "provider": "OpenRouter",
        "context": "Varies",
        "cost": "Varies"
    }
}

def fetch_openrouter_models() -> dict:
    """Fetch live model list from OpenRouter API."""
    import requests
    
    try:
        print("DEBUG: Fetching live models from OpenRouter API...")
        response = requests.get(OPENROUTER_MODELS_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = {}
            
            # Always include auto first
            models["openrouter/auto"] = {
                "name": "Auto (Best Model)",
                "description": "Automatically selects the best model for your prompt",
                "provider": "OpenRouter",
                "context": "Varies",
                "cost": "Varies"
            }
            
            # Add ALL models from API response (removed limit)
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id and model_id not in models:
                    pricing = model.get("pricing", {})
                    prompt_cost = float(pricing.get("prompt", 0)) * 1000000 if pricing.get("prompt") else 0
                    
                    models[model_id] = {
                        "name": model.get("name", model_id),
                        "description": model.get("description", "")[:100] if model.get("description") else "",
                        "provider": model_id.split("/")[0].title() if "/" in model_id else "Unknown",
                        "context": f"{model.get('context_length', 0)//1000}K tokens",
                        "cost": f"${prompt_cost:.2f}/1M" if prompt_cost else "Free"
                    }
            
            print(f"DEBUG: Fetched {len(models)} models from OpenRouter")
            return models
        else:
            print(f"WARNING: OpenRouter models API returned {response.status_code}")
            return FALLBACK_LLM_MODELS
            
    except Exception as e:
        print(f"WARNING: Failed to fetch OpenRouter models: {e}")
        return FALLBACK_LLM_MODELS

# Fetch live models from OpenRouter (runs once at module load)
LLM_MODELS = fetch_openrouter_models()

# Import roles from the database service
from .roles_service import get_all_roles as get_roles_from_db, get_social_links_for_role as get_social_links_from_db

def _get_random_roles() -> list[str]:
    """Get roles from database with fallback."""
    try:
        roles = get_roles_from_db()
        print(f"DEBUG LLM: Loaded {len(roles)} roles from database")
        if roles:
            return roles
    except Exception as e:
        print(f"ERROR LLM: Failed to load roles from database: {e}")
    # Fallback - should rarely hit this
    print("WARNING LLM: Using hardcoded fallback roles!")
    return ["Software Engineer", "Product Manager", "UX Designer", "Data Scientist", "Marketing Manager"]


def normalize_cv_data(cv_data: dict) -> dict:
    """Ensure consistency of CV data keys for HTML template."""
    print(f"DEBUG NORMALIZE: Input CV keys: {list(cv_data.keys())}")
    
    # 1. Normalize Experience
    # Handle common aliases
    if "experiences" in cv_data and "experience" not in cv_data:
        cv_data["experience"] = cv_data.pop("experiences")
    if "work_experience" in cv_data and "experience" not in cv_data:
        cv_data["experience"] = cv_data.pop("work_experience")
        
    # Ensure items fit HTML template (title, company, date_range, description, achievements)
    normalized_exp = []
    
    for exp in cv_data.get("experience", []):
        if "role" in exp and "title" not in exp:
            exp["title"] = exp.pop("role")
        if "period" in exp and "date_range" not in exp:
            exp["date_range"] = exp.pop("period")
        
        # If 'achievements' is missing but 'description' is a list, move list to achievements
        if "achievements" not in exp:
            if isinstance(exp.get("description"), list):
                exp["achievements"] = exp.pop("description")
                exp["description"] = "Key responsibilities and achievements:"
            elif "description" in exp:
                 # Ensure we have an achievements list even if empty for HTML check
                 pass
        
        normalized_exp.append(exp)
        
    cv_data["experience"] = normalized_exp
    
    # CRITICAL FALLBACK: If experience empty, inject dummy to prove HTML works
    if not cv_data.get("experience"):
        print("CRITICAL WARNING: No experience found after normalization. Injecting dummy data.")
        cv_data["experience"] = [{
            "title": "Senior Developer (Generated)",
            "company": "Tech Corp",
            "date_range": "2020 - Present",
            "description": "Experience data was missing from LLM response. Showing placeholder.",
            "achievements": ["Successfully integrated AI systems.", "Optimized backend performance."]
        }]

    # 2. Normalize Skills - Critical for HTML bar charts
    # We need skills.technical list [{"name": "X", "level": N}]
    if "technical_skills" in cv_data and "skills" not in cv_data:
         # Convert old format
         tech_skills = cv_data.pop("technical_skills")
         new_skills = []
         if isinstance(tech_skills, dict):
             # flatten {'Languages': ['Python'], ...}
             for category, items in tech_skills.items():
                 if isinstance(items, list):
                     for item in items:
                         new_skills.append({"name": item, "level": random.randint(75, 95)})
         elif isinstance(tech_skills, list):
             for s in tech_skills:
                 if isinstance(s, str):
                     new_skills.append({"name": s, "level": random.randint(75, 95)})
                 else:
                     new_skills.append(s)
         cv_data["skills"] = {"technical": new_skills}
         
    # Ensure struct existence
    if "skills" not in cv_data:
        cv_data["skills"] = {"technical": []}
    
    # If LLM returned "skills": [...] list instead of dict
    if isinstance(cv_data["skills"], list):
        raw_list = cv_data["skills"]
        new_list = []
        for s in raw_list:
             if isinstance(s, str):
                 new_list.append({"name": s, "level": random.randint(75, 95)})
             elif isinstance(s, dict):
                 new_list.append(s)
        cv_data["skills"] = {"technical": new_list}
        
    # Ensure technical key exists inside skills dict
    if isinstance(cv_data["skills"], dict) and "technical" not in cv_data["skills"]:
         # Maybe keys are categories? Flatten them
         flattened = []
         for k, v in cv_data["skills"].items():
             if isinstance(v, list):
                 for item in v:
                      if isinstance(item, str):
                          flattened.append({"name": item, "level": random.randint(75, 95)})
                      elif isinstance(item, dict):
                          flattened.append(item)
         cv_data["skills"]["technical"] = flattened

    # 3. Normalize Education
    for edu in cv_data.get("education", []):
        if "school" in edu and "institution" not in edu:
            edu["institution"] = edu.pop("school")
        if "details" in edu and "honors" not in edu:
            edu["honors"] = edu.pop("details")

    # 4. Social
    cv_data = ensure_social_dict(cv_data)
    
    return cv_data


def ensure_social_dict(cv_data: dict) -> dict:
    """Ensure the social field is a proper dictionary with expected keys."""
    if not cv_data:
        return cv_data
    
    # Ensure social is a dict, not a list
    social = cv_data.get("social", {})
    if isinstance(social, list):
        # Convert list of dicts to single dict
        social_dict = {}
        for item in social:
            if isinstance(item, dict):
                social_dict.update(item)
        cv_data["social"] = social_dict
    elif not isinstance(social, dict):
        cv_data["social"] = {}
    
    return cv_data


def resolve_role(role: str) -> str:
    """Convert 'any' to a random high-demand tech role."""
    if role.lower() == "any":
        resolved = random.choice(RANDOM_TECH_ROLES)
        print(f"DEBUG: Resolved 'any' role to: {resolved}")
        return resolved
    return role
    
    
def get_social_links_for_role(role: str) -> list[str]:
    """Return relevant social media keys based on role."""
    role = role.lower()
    
    # Base links for everyone
    links = ["linkedin", "website"]
    
    # =====================================
    # TECH & ENGINEERING
    # =====================================
    
    # 1. Game Developers
    if any(k in role for k in ["game", "unity", "unreal", "godot", "indie"]):
        links.append("github")
        links.append("itch_io")
        links.append("steam")
        if "mobile" in role:
            links.append("google_play")
            links.append("app_store")
    
    # 2. Mobile Developers
    elif any(k in role for k in ["mobile", "ios", "android", "flutter", "react native"]):
        links.append("github")
        links.append("google_play")
        links.append("app_store")
    
    # 3. General Developers / Engineers
    elif any(k in role for k in ["developer", "engineer", "software", "programmer", "coder", "devops", "architect", "backend", "frontend", "fullstack", "tech lead", "sre"]):
        links.append("github")
        if "data" in role or "science" in role:
            links.append("kaggle")
    
    # 4. Data & AI / ML
    elif any(k in role for k in ["data", "scientist", "analyst", "ai", "machine learning", "ml", "deep learning", "nlp"]):
        links.append("github")
        links.append("kaggle")
        links.append("huggingface")
    
    # 5. Blockchain / Web3 / Crypto
    elif any(k in role for k in ["blockchain", "crypto", "web3", "solidity", "smart contract", "defi"]):
        links.append("github")
        links.append("twitter")
    
    # =====================================
    # RESEARCH & ACADEMIA
    # =====================================
    
    # 6. Researchers / Academics
    elif any(k in role for k in ["research", "professor", "phd", "academic", "scientist", "lecturer", "postdoc"]):
        links.append("researchgate")
        links.append("google_scholar")
        links.append("orcid")
        if any(k in role for k in ["ai", "computer", "bio", "physics", "math"]):
            links.append("github")
    
    # =====================================
    # DESIGN & CREATIVE
    # =====================================
    
    # 7. 3D Artists / VFX / Animation
    elif any(k in role for k in ["3d", "animator", "vfx", "motion", "cgi", "rigger", "modeler", "texture"]):
        links.append("artstation")
        links.append("behance")
        links.append("vimeo")
        links.append("instagram")
    
    # 8. 2D Artists / Illustrators / Concept Art
    elif any(k in role for k in ["2d", "illustrator", "concept", "character artist", "comic", "storyboard"]):
        links.append("artstation")
        links.append("behance")
        links.append("instagram")
        links.append("deviantart")
    
    # 9. UI/UX / Product Design
    elif any(k in role for k in ["ui", "ux", "product design", "interface", "interaction", "user experience"]):
        links.append("dribbble")
        links.append("behance")
        links.append("figma")
    
    # 10. Graphic Design
    elif any(k in role for k in ["graphic", "visual design", "brand design", "logo"]):
        links.append("behance")
        links.append("dribbble")
        links.append("instagram")
    
    # =====================================
    # MUSIC & AUDIO
    # =====================================
    
    # 11. Musicians / Composers / Sound Design
    elif any(k in role for k in ["music", "composer", "sound design", "audio", "producer", "dj", "songwriter"]):
        links.append("spotify")
        links.append("soundcloud")
        links.append("bandcamp")
        links.append("youtube")
    
    # =====================================
    # VIDEO & MEDIA
    # =====================================
    
    # 12. Video / Film / Photography
    elif any(k in role for k in ["video", "photographer", "film", "cinematographer", "director", "editor"]):
        links.append("youtube")
        links.append("vimeo")
        links.append("instagram")
    
    # 13. Content Creators / Streamers / Influencers
    elif any(k in role for k in ["creator", "youtuber", "streamer", "influencer", "tiktoker", "podcaster"]):
        links.append("youtube")
        links.append("twitch")
        links.append("instagram")
        links.append("tiktok")
    
    # =====================================
    # WRITING & CONTENT
    # =====================================
    
    # 14. Writers / Journalists / Authors
    elif any(k in role for k in ["writer", "author", "journalist", "copywriter", "blogger", "editor", "novelist"]):
        links.append("medium")
        links.append("substack")
        links.append("twitter")
    
    # 15. Marketing / SEO / Social Media
    elif any(k in role for k in ["marketing", "social media", "seo", "growth", "brand", "community", "pr"]):
        links.append("twitter")
        links.append("instagram")
    
    # =====================================
    # ARCHITECTURE & ENGINEERING (Physical)
    # =====================================
    
    # 16. Architects / Interior Design
    elif any(k in role for k in ["architect", "interior", "urban", "landscape"]):
        links.append("behance")
        links.append("archdaily")
        links.append("instagram")
    
    # =====================================
    # EDUCATION & TRAINING
    # =====================================
    
    # 17. Teachers / Trainers / Coaches
    elif any(k in role for k in ["teacher", "trainer", "instructor", "coach", "tutor", "educator"]):
        links.append("youtube")
        links.append("udemy")
    
    # =====================================
    # BUSINESS & MANAGEMENT
    # =====================================
    
    # 18. Executives / Management / Consulting
    elif any(k in role for k in ["ceo", "cto", "cfo", "director", "manager", "consultant", "executive", "founder", "entrepreneur"]):
        # Just LinkedIn + Website is fine
        links.append("twitter")
    
    # 19. Sales / Business Development
    elif any(k in role for k in ["sales", "account", "business development", "partnership"]):
        # LinkedIn + Website
        pass
    
    # =====================================
    # SPECIALTY FIELDS
    # =====================================
    
    # 20. Healthcare / Medical
    elif any(k in role for k in ["doctor", "nurse", "medical", "healthcare", "physician", "surgeon", "therapist"]):
        links.append("doximity")
    
    # 21. Legal
    elif any(k in role for k in ["lawyer", "attorney", "legal", "paralegal", "counsel"]):
        # LinkedIn + Website
        pass
    
    # 22. Finance / Accounting
    elif any(k in role for k in ["finance", "accountant", "auditor", "controller", "investment", "trading"]):
        # LinkedIn + Website
        pass
    
    # 23. HR / Recruiting
    elif any(k in role for k in ["hr", "recruiter", "talent", "people"]):
        # LinkedIn + Website
        pass
    
    # 24. Fashion / Modeling
    elif any(k in role for k in ["fashion", "model", "stylist", "makeup"]):
        links.append("instagram")
        links.append("pinterest")
    
    # 25. Culinary / Chef
    elif any(k in role for k in ["chef", "culinary", "cook", "baker", "restaur"]):
        links.append("instagram")
        links.append("youtube")
    
    return links

# Enhanced system prompt for detailed CVs
# Simplified System Prompt - Details are now in the external template
SYSTEM_PROMPT = """You are an expert CV generator. 
Instructions:
1. Return ONLY valid JSON.
2. No markdown formatting.
3. Follow the user's detailed requirements exactly.
"""



def create_profile_prompt(role: str, gender: str, ethnicity: str, origin: str, age_range: str) -> str:
    """Create a prompt for generating a unique user profile."""
    
    # Load from external template - FAIL FAST
    template_path = BACKEND_DIR / "prompts" / "profile_creation_prompt.txt"
    
    if not template_path.exists():
        error_msg = f"CRITICAL ERROR: Profile Template file not found at {template_path}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
        
    print(f"DEBUG: Loading external Profile template from {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()
    
    return Template(template_str).render(
        role=role,
        gender=gender,
        ethnicity=ethnicity,
        origin=origin,
        age_range=age_range
    )


async def generate_profile_data(
    role: str,
    gender: str,
    ethnicity: str,
    origin: str,
    age_range: str,
    model: Optional[str] = None
) -> Tuple[dict, str]:
    """
    Generate a unique profile (Phase 1)
    Returns: (profile_data, used_prompt)
    """
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not configured")
        
    model_id = model or os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    
    prompt = create_profile_prompt(role, gender, ethnicity, origin, age_range)
    
    request_payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9, # High temperature for variety
        "max_tokens": 1000
    }
        
    # Retry loop for robustness
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ai-cv-suite.local",
                    },
                    json=request_payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    try:
                        content = result["choices"][0]["message"]["content"]
                    except (KeyError, IndexError):
                        raise RuntimeError(f"Unexpected API response format: {result}")
                    
                    # Cleanup and parse
                    # Remove markdown code blocks if present
                    if "```" in content:
                        content = content.split("```json")[-1].split("```")[0].strip()
                    
                    # Find valid JSON bounds
                    start = content.find('{')
                    end = content.rfind('}')
                    if start != -1 and end != -1:
                        content = content[start:end+1]
                        
                    # Try to parse
                    try:
                        profile_data = json.loads(content)
                        print(f"SUCCESS: Generated Profile: {profile_data.get('name')}")
                        return profile_data, prompt
                    except json.JSONDecodeError:
                        print(f"WARNING: Malformed JSON content: {content[:100]}...")
                        raise # Re-raise to be caught by outer except
                
                elif response.status_code == 429:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2s, 3s, 5s...
                    print(f"WARNING: Rate Limit (429) - Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                else:
                    print(f"WARNING: API Request Failed (Attempt {attempt+1}): {response.text}")
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Profile Gen Failed: {response.text}")
        
        except json.JSONDecodeError as e:
            print(f"WARNING: JSON Parse Error (Attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Profile Gen JSON Error: {e} | Content: {content[:100]}...")
            continue # Retry
            
        except Exception as e:
            print(f"ERROR Generating Profile (Attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Profile Gen Error: {e}")
            continue


def create_user_prompt(role: str, expertise: str, age: int, gender: str, ethnicity: str, origin: str, remote: bool, name: Optional[str] = None, profile_data: Optional[dict] = None) -> str:
    """Create detailed user prompt based on profile using external template."""
    
    # Use Profile Data if available (Phase 2)
    display_name = name
    display_role = role
    display_gender = gender
    
    if profile_data:
        display_name = profile_data.get("name", name)
        display_role = profile_data.get("role", role)
        display_gender = profile_data.get("gender", gender)
        # We can pass more profile data into the template if needed

    # Get dynamic social keys based on role from database
    social_keys = get_social_links_from_db(display_role)
    print(f"DEBUG: Selected social keys for role '{display_role}': {social_keys}")

    # 2. Load from external template - CRITICAL: FAIL FAST IF MISSING
    template_path = BACKEND_DIR / "prompts" / "cv_prompt_template.txt"
    
    if not template_path.exists():
        error_msg = f"CRITICAL ERROR: CV Template file not found at {template_path}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
        
    print(f"DEBUG: Loading external CV template from {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()
    
    # Render Jinja2 template
    return Template(template_str).render(
        role=display_role,
        expertise=expertise,
        age=age,
        gender=display_gender,
        ethnicity=ethnicity,
        origin=origin,
        remote="Preferred" if remote else "Flexible",
        name=display_name if display_name else "",
        social_keys=social_keys  # Pass dynamic social list
    )


def get_available_models() -> list[dict]:
    """Return list of available LLM models with their properties."""
    return [
        {
            "id": model_id,
            **model_info
        }
        for model_id, model_info in LLM_MODELS.items()
    ]


async def generate_cv_content_v2(
    role: str = "Software Developer",
    expertise: str = "mid",
    age: int = 30,
    gender: str = "any",
    ethnicity: str = "any",
    origin: str = "United States",
    remote: bool = False,
    model: Optional[str] = None,
    name: Optional[str] = None,
    profile_data: Optional[dict] = None
) -> Tuple[dict, str]:
    """
    Generate detailed CV content using OpenRouter with enhanced prompts.
    Returns: (cv_data, used_prompt)
    """
    # CRITICAL: Resolve "any" to a real role FIRST
    role = resolve_role(role)
    
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    # Debug logging
    print(f"DEBUG: API Key loaded: {'YES (' + api_key[:8] + '...)' if api_key and len(api_key) > 8 else 'NO/EMPTY'}")
    print(f"DEBUG: Role for generation: {role}")
    print(f"DEBUG: Using Profile Data: {bool(profile_data)} (Name: {name})")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        error_msg = "ERROR: OPENROUTER_API_KEY not configured in backend/.env - Cannot generate CV without real API key"
        print(error_msg)
        raise ValueError(error_msg)
    
    # Use provided model or default
    model_id = model or os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    print(f"DEBUG: Using LLM model: {model_id}")
    
    user_prompt = create_user_prompt(
        role=role, 
        expertise=expertise, 
        age=age, 
        gender=gender, 
        ethnicity=ethnicity, 
        origin=origin, 
        remote=remote,
        name=name,
        profile_data=profile_data
    )
    
    # Adjust max_tokens based on expertise level - INCREASED to prevent JSON truncation
    max_tokens = {
        'junior': 5000,
        'mid': 6000,
        'senior': 8000,
        'expert': 8000,
        'any': 6000
    }.get(expertise, 6000)
    
    try:
        # Build request payload
        request_payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": max_tokens
        }
        
        request_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-cv-suite.local",
            "X-Title": "AI CV Suite"
        }
        
        # LOG REQUEST
        print("="*60)
        print(f"DEBUG REQUEST - URL: {OPENROUTER_API_URL}")
        print(f"DEBUG REQUEST - Model: {model_id}")
        print(f"DEBUG REQUEST - Headers: Authorization=Bearer {api_key[:20]}..., Content-Type=application/json")
        print(f"DEBUG REQUEST - Payload keys: {list(request_payload.keys())}")
        print(f"DEBUG REQUEST - Messages count: {len(request_payload['messages'])}")
        print(f"DEBUG REQUEST - System prompt length: {len(SYSTEM_PROMPT)} chars")
        print(f"DEBUG REQUEST - User prompt length: {len(user_prompt)} chars")
        print("="*60)
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=request_headers,
                json=request_payload
            )
            
            # LOG RESPONSE (Safe print for Windows consoles)
            try:
                print("="*60)
                print(f"DEBUG RESPONSE - Status: {response.status_code}")
                # Sanitize headers and body for printing
                safe_body = response.text[:1000].encode('ascii', 'replace').decode('ascii')
                print(f"DEBUG RESPONSE - Body: {safe_body}")
                print("="*60)
            except Exception:
                print("DEBUG RESPONSE - (Content could not be printed due to encoding)")
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Clean up the response
                    content = content.strip()
                    
                    # Remove markdown code blocks if present
                    if content.startswith("```"):
                        lines = content.split("\n")
                        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                        content = content.strip()
                    
                    if content.startswith("json"):
                        content = content[4:].strip()
                    
                    # Robust JSON extraction: Find first { and last }
                    try:
                        start_idx = content.find('{')
                        end_idx = content.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            content = content[start_idx:end_idx+1]
                    except Exception:
                        pass
                    
                    try:
                        cv_data = json.loads(content)
                        # Ensure data structure safety and HTML compatibility
                        cv_data = normalize_cv_data(cv_data)
                        print(f"SUCCESS: CV content generated with {model_id}")
                        return cv_data, user_prompt
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {e}")
                        # Safe print for raw content
                        try:
                            print(f"Raw content sample: {content[:200].encode('ascii', 'replace').decode('ascii')}")
                        except:
                            pass
                        # Fallback: raise error but with safe logging
                        raise RuntimeError(f"JSON Decode Error: {e}")
            
            # Log full response for debugging (Safe print)
            error_details = "Unknown error"
            try:
                if response.text:
                    error_details = response.text[:200].encode('ascii', 'replace').decode('ascii')
            except:
                pass
                
            error_msg = f"OpenRouter API returned status {response.status_code}: {error_details}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
            
    except Exception as e:
        # Safe exception printing
        try:
            safe_e = str(e).encode('ascii', 'replace').decode('ascii')
        except:
            safe_e = "Encoding error in exception message"
            
        error_msg = f"OpenRouter API exception: {safe_e}"
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)


def _generate_mock_cv(role: str, origin: str, gender: str, expertise: str = "mid") -> dict:
    """Generate mock CV data when API is unavailable."""
    
    # Name pools by origin
    names_by_origin = {
        "europe": {
            "male": ["Alexander Schmidt", "Lucas Müller", "Pierre Dubois", "Marco Rossi", "James Wilson"],
            "female": ["Sophie Martin", "Emma Weber", "Isabella Romano", "Charlotte Brown", "Olivia Davis"]
        },
        "asia": {
            "male": ["Wei Chen", "Hiroshi Tanaka", "Jin Park", "Raj Patel", "Amit Kumar"],
            "female": ["Mei Lin", "Yuki Sato", "Ji-Young Kim", "Priya Sharma", "Aiko Yamamoto"]
        },
        "americas": {
            "male": ["Michael Johnson", "Carlos Rodriguez", "David Williams", "Juan Martinez"],
            "female": ["Sarah Miller", "Maria Gonzalez", "Jennifer Anderson", "Ana Silva"]
        },
        "default": {
            "male": ["John Smith", "Michael Brown", "David Wilson"],
            "female": ["Emily Johnson", "Sarah Williams", "Jessica Davis"]
        }
    }
    
    # Determine origin category
    origin_lower = origin.lower()
    if any(x in origin_lower for x in ["europe", "germany", "france", "italy", "uk", "spain"]):
        origin_key = "europe"
    elif any(x in origin_lower for x in ["asia", "china", "japan", "korea", "india"]):
        origin_key = "asia"
    elif any(x in origin_lower for x in ["america", "usa", "brazil", "mexico", "canada"]):
        origin_key = "americas"
    else:
        origin_key = "default"
    
    # Select name
    if gender.lower() == "male":
        name = random.choice(names_by_origin[origin_key]["male"])
    elif gender.lower() == "female":
        name = random.choice(names_by_origin[origin_key]["female"])
    else:
        all_names = names_by_origin[origin_key]["male"] + names_by_origin[origin_key]["female"]
        name = random.choice(all_names)
    
    # Role-appropriate skills
    skill_pools = {
        "devops": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "Linux", "Python"],
        "developer": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "TypeScript"],
        "default": ["Communication", "Problem Solving", "Team Work", "Project Management"]
    }
    
    role_lower = role.lower()
    if "devops" in role_lower:
        skills_pool = skill_pools["devops"]
    elif "developer" in role_lower or "engineer" in role_lower:
        skills_pool = skill_pools["developer"]
    else:
        skills_pool = skill_pools["default"]
    
    selected_skills = random.sample(skills_pool, min(5, len(skills_pool)))
    skills_list = [{"name": s, "level": random.randint(70, 95)} for s in selected_skills]
    
    email_name = name.lower().replace(" ", ".").replace("'", "")
    
    return {
        "name": name,
        "title": role,
        "email": f"{email_name}@gmail.com",
        "phone": f"+1 {random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "profile_summary": f"Experienced {role} with a passion for delivering high-quality work and proven track record in fast-paced environments.",
        "skills": {
            "technical": skills_list
        },
        "languages": [
            {"name": "English", "level": 5},
            {"name": random.choice(["Spanish", "French", "German"]), "level": random.randint(2, 4)}
        ],
        "experience": [
            {
                "title": f"Senior {role}",
                "company": random.choice(["Tech Solutions Inc", "Global Systems Corp", "Innovation Labs"]),
                "years": "2021 - Present",
                "description": f"Leading initiatives as a {role}, collaborating with cross-functional teams."
            },
            {
                "title": role,
                "company": random.choice(["StartUp Co", "Enterprise Tech", "Cloud Services Ltd"]),
                "years": "2018 - 2021",
                "description": "Developed expertise in key areas while contributing to major projects."
            }
        ],
        "education": [
            {
                "degree": "Master's in Computer Science",
                "institution": random.choice(["Stanford University", "MIT", "Cambridge University"]),
                "years": "2016 - 2018"
            }
        ],
        "certificates": [
            {"year": "2023", "title": "AWS Solutions Architect", "honors": "Professional"}
        ],
        "interests": ["Technology", "Travel", "Reading", "Photography"],
        "social": {
            "github": f"https://github.com/{email_name.split('.')[0]}",
            "linkedin": f"https://linkedin.com/in/{email_name.replace('.', '')}"
        }
    }
