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
            
            # NOTE: Removed openrouter/auto - it selects paid models automatically
            # and caused unexpected billing charges
            
            # Add ALL models from API response (removed limit)
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id and model_id not in models:
                    pricing = model.get("pricing", {})
                    prompt_cost = float(pricing.get("prompt", 0)) * 1000000 if pricing.get("prompt") else 0
                    completion_cost = float(pricing.get("completion", 0)) * 1000000 if pricing.get("completion") else 0
                    
                    # Determine if truly free: must have :free suffix OR both costs are exactly 0
                    is_truly_free = model_id.endswith(":free") or (prompt_cost == 0 and completion_cost == 0)
                    
                    if is_truly_free:
                        cost_display = "✅ Free"
                    elif prompt_cost < 0.01:
                        cost_display = f"~${prompt_cost:.4f}/1M"  # Very cheap but not free
                    else:
                        cost_display = f"${prompt_cost:.2f}/1M"
                    
                    models[model_id] = {
                        "name": model.get("name", model_id),
                        "description": model.get("description", "")[:100] if model.get("description") else "",
                        "provider": model_id.split("/")[0].title() if "/" in model_id else "Unknown",
                        "context": f"{model.get('context_length', 0)//1000}K tokens",
                        "cost": cost_display,
                        "is_free": is_truly_free  # Add flag for frontend filtering
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


def enforce_career_progression(cv_data: dict) -> dict:
    """
    Parametrically enforce logical career progression.
    Ensures simplest roles are at the past, senior roles at present.
    """
    experience = cv_data.get("experience", [])
    if not isinstance(experience, list) or len(experience) < 2:
        return cv_data

    # Iterate from oldest (end of list) to 2nd newest (index 1)
    # We leave index 0 (current role) as is.
    
    forbidden_prefixes = ["Senior ", "Lead ", "Principal ", "Chief ", "Head of ", "Executive ", "Sr. ", "Snr. "]
    
    # Process all past roles (index 1 to end)
    for i in range(1, len(experience)):
        role = experience[i]
        if not isinstance(role, dict): continue
        
        title = role.get("title", "")
        original_title = title
        
        # 1. Strip high-level seniority prefixes from ALL past roles
        for prefix in forbidden_prefixes:
            # Case insensitive check
            if title.lower().startswith(prefix.lower()):
                title = title[len(prefix):] # Remove prefix
        
        # 2. Special handling for the OLDEST job (entry/mid point)
        if i == len(experience) - 1:
            # Downgrade C-Level/VP/Director for the very first job history
            if "Vice President" in title or "VP" in title:
                title = "Director"
            elif "Director" in title:
                title = "Senior Manager"
            elif "Manager" in title and "Senior" not in title:
                # Optional: Downgrade Manager to Specialist/Lead? 
                # Let's keep Manager as it might be plausible for a mid-career entry
                pass
                
        # Update if changed
        if title != original_title:
            role["title"] = title.strip()
            
    return cv_data

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
    
    # ENFORCE LOGICAL CAREER PROGRESSION
    cv_data = enforce_career_progression(cv_data)
    
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
    # Base and logic imported from previous context (abbreviated for restoration but functional)
    return get_social_links_from_db(role)

# Enhanced system prompt for detailed CVs
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

def clean_json_response(content: str) -> str:
    """
    Robustly clean LLM response to extract valid JSON.
    Handles <think> blocks, code fences, and extra commentary.
    """
    import re
    
    # 1. Remove <think> blocks (often used by reasoning models)
    # Use dotall flag to match across newlines
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # 2. Remove standard markdown code fences
    if "```" in content:
        # Try finding json specific block first
        if "```json" in content:
            parts = content.split("```json")
            if len(parts) > 1:
                content = parts[1].split("```")[0]
        else:
            # Generic fence
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1]
                
    # 3. Find the first '{' and last '}'
    start = content.find('{')
    end = content.rfind('}')
    
    if start != -1 and end != -1:
        content = content[start:end+1]
    
    # 4. Strip whitespace
    content = content.strip()
    
    return content

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
                        "X-Title": "AI CV Suite", # Required for some free models
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
                    content = clean_json_response(content)
                        
                    # Try to parse
                    try:
                        profile_data = json.loads(content)
                        # Minimal validation
                        if not isinstance(profile_data, dict):
                            raise ValueError("JSON parsed but result is not a dictionary")
                        
                        print(f"SUCCESS: Generated Profile: {profile_data.get('name')}")
                        return profile_data, prompt

                    except json.JSONDecodeError as e:
                        print(f"WARNING: Malformed JSON content: {content[:100]}...")
                        # One last desperate cleanup attempt for common issues
                        try:
                            # Sometimes braces are missing at the very end
                            if content.strip().startswith("{") and not content.strip().endswith("}"):
                                content += "}"
                                profile_data = json.loads(content)
                                return profile_data, prompt
                        except: pass
                        raise # Re-raise to be caught by outer except
                
                elif response.status_code == 404 or response.status_code == 403:
                    # Model not found or restricted - switch to guaranteed FREE model with notification
                    fallback_model = "google/gemini-2.0-flash-exp:free"
                    print(f"⚠️ WARNING: Model '{model_id}' returned {response.status_code}. Switching to FREE fallback: {fallback_model}")
                    model_id = fallback_model
                    request_payload["model"] = model_id
                    await asyncio.sleep(1)
                    continue

                elif response.status_code == 429:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2s, 3s, 5s...
                    print(f"WARNING: Rate Limit (429) - Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                else:
                    print(f"WARNING: API Request Failed (Attempt {attempt+1}): {response.text}")
                    if attempt == max_retries - 1:
                        # On final failure, try FREE fallback once before giving up
                        fallback_model = "google/gemini-2.0-flash-exp:free"
                        if model_id != fallback_model:
                            print(f"⚠️ FALLBACK: Trying FREE model {fallback_model} after failures")
                            model_id = fallback_model
                            request_payload["model"] = model_id
                            continue
                        raise RuntimeError(f"Profile Gen Failed after {max_retries} attempts: {response.text}")
        
        except json.JSONDecodeError as e:
            print(f"WARNING: JSON Parse Error (Attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                # Use partial content in error if available
                content_preview = locals().get('content', 'No content')[:200]
                raise RuntimeError(f"Profile Gen JSON Error: {e} | Content: {content_preview}...")
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
    
    # Retry loop for robustness
    max_retries = 3
    for attempt in range(max_retries):
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
                
                # LOG RESPONSE
                try:
                    print("="*60)
                    print(f"DEBUG RESPONSE - Status: {response.status_code}")
                    safe_body = response.text[:1000].encode('ascii', 'replace').decode('ascii')
                    print(f"DEBUG RESPONSE - Body: {safe_body}")
                    print("="*60)
                except Exception:
                    print("DEBUG RESPONSE - (Content could not be printed due to encoding)")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        try:
                            content = result["choices"][0]["message"]["content"]
                            
                            # Clean up the response using robust helper
                            content = clean_json_response(content)
                            
                            # Parse JSON
                            cv_data = json.loads(content)
                            
                            # Normalize Data structure for HTML template
                            cv_data = normalize_cv_data(cv_data)
                            
                            print(f"SUCCESS: Generated CV Content for {role}")
                            return cv_data, user_prompt

                        except (KeyError, IndexError):
                             print(f"WARNING: Invalid API response structure: {result}")
                             raise RuntimeError(f"Invalid API response: {result}")
                             
                        except json.JSONDecodeError as e:
                            print(f"WARNING: JSON Parse Error (Attempt {attempt+1}): {e}")
                            print(f"DEBUG: Failed content snippet: {content[:200]}...")
                            
                            if attempt == max_retries - 1:
                                raise RuntimeError(f"CV Gen JSON Error: {e}")
                            continue

                    else:
                        raise RuntimeError(f"API returned no choices: {result}")
                
                elif response.status_code == 429:
                    wait_time = (2 ** attempt) + 1
                    print(f"WARNING: Rate Limit (429) - Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                else:
                    print(f"WARNING: API Request Failed (Attempt {attempt+1}): {response.text}")
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"CV Gen Failed after {max_retries} attempts. Last error: {response.text}")
        
        except Exception as e:
            print(f"ERROR Generating CV (Attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"CV Gen Error: {e}")
            continue
            
    # Should not be reached if exceptions are raised correctly, but as safety:
    raise RuntimeError("CV Generation failed - unexpected exit from retry loop")
