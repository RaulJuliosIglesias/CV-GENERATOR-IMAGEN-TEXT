"""
LLM Service - OpenRouter Integration for CV Content Generation
Enhanced with detailed prompts for comprehensive CVs
"""

import os
import json
import random
from typing import Optional
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
            
            # Add top models from API response
            for model in data.get("data", [])[:50]:  # Limit to top 50
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

# Random tech roles for "any" selection
RANDOM_TECH_ROLES = [
    "Senior DevOps Engineer",
    "AI Research Scientist",
    "Blockchain Lead Developer",
    "Full Stack Architect",
    "Data Platform Engineer",
    "Cloud Security Specialist",
    "Machine Learning Engineer",
    "Site Reliability Engineer",
    "Principal Software Engineer",
    "Backend Systems Architect",
    "Mobile Development Lead",
    "Cybersecurity Analyst",
    "Quantum Computing Researcher",
    "Platform Engineering Manager"
]


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

# Enhanced system prompt for detailed CVs
# Simplified System Prompt - Details are now in the external template
SYSTEM_PROMPT = """You are an expert CV generator. 
Instructions:
1. Return ONLY valid JSON.
2. No markdown formatting.
3. Follow the user's detailed requirements exactly.
"""


def create_user_prompt(role: str, expertise: str, age: int, gender: str, ethnicity: str, origin: str, remote: bool) -> str:
    """Create detailed user prompt based on profile using external template."""
    
    # 1. Resolve logical variables
    role_instruction = f"Role: {role}"
    if role.lower() == "any":
        role_instruction = "Role: CHOOSE A RANDOM HIGH-DEMAND TECH ROLE"

    # 2. Try loading from external template
    try:
        template_path = BACKEND_DIR / "prompts" / "cv_prompt_template.txt"
        if template_path.exists():
            print(f"DEBUG: Loading external CV template from {template_path}")
            with open(template_path, "r", encoding="utf-8") as f:
                template_str = f.read()
            
            # Render Jinja2 template
            return Template(template_str).render(
                role=role if role.lower() != "any" else "High Demand Tech Role (Choose one)",
                expertise=expertise,
                age=age,
                gender=gender,
                ethnicity=ethnicity,
                origin=origin,
                remote="Preferred" if remote else "Flexible",
                name="" # Let AI generate it
            )
    except Exception as e:
        print(f"WARNING: Could not load/render CV template: {e}")

    # 3. Fallback (Legacy prompt if file missing)
    return f"""Generate a COMPLETE, REALISTIC CV (JSON format) for:
    
    Profile:
    - {role_instruction}
    - Level: {expertise}
    - Age: {age}
    - Gender: {gender}
    - Ethnicity: {ethnicity}
    - Location: {origin}
    
    Requirements:
    - JSON Output ONLY.
    - Realistic name matching gender/ethnicity.
    - 5-7 bullet points per job with metrics.
    - Technical skills arrays.
    """


def get_available_models() -> list[dict]:
    """Return list of available LLM models with their properties."""
    return [
        {
            "id": model_id,
            **model_info
        }
        for model_id, model_info in LLM_MODELS.items()
    ]


async def generate_cv_content(
    role: str = "Software Developer",
    expertise: str = "mid",
    age: int = 30,
    gender: str = "any",
    ethnicity: str = "any",
    origin: str = "United States",
    remote: bool = False,
    model: Optional[str] = None
) -> dict:
    """
    Generate detailed CV content using OpenRouter with enhanced prompts.
    """
    # CRITICAL: Resolve "any" to a real role FIRST
    role = resolve_role(role)
    
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    # Debug logging
    print(f"DEBUG: API Key loaded: {'YES (' + api_key[:8] + '...)' if api_key and len(api_key) > 8 else 'NO/EMPTY'}")
    print(f"DEBUG: Role for generation: {role}")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        error_msg = "ERROR: OPENROUTER_API_KEY not configured in backend/.env - Cannot generate CV without real API key"
        print(error_msg)
        raise ValueError(error_msg)
    
    # Use provided model or default
    model_id = model or os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    print(f"DEBUG: Using LLM model: {model_id}")
    
    user_prompt = create_user_prompt(role, expertise, age, gender, ethnicity, origin, remote)
    
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
                        # Ensure data structure safety
                        cv_data = ensure_social_dict(cv_data)
                        print(f"SUCCESS: CV content generated with {model_id}")
                        return cv_data
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
