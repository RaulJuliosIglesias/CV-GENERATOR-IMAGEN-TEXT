"""
LLM Service - OpenRouter Integration for CV Content Generation
Supports multiple LLM models with different capabilities and costs
"""

import os
import json
import random
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Available LLM models
LLM_MODELS = {
    "google/gemini-2.0-flash-exp:free": {
        "name": "Gemini 2.0 Flash (Free)",
        "description": "Google's fast, free experimental model",
        "provider": "Google",
        "context": "1M tokens",
        "cost": "Free"
    },
    "google/gemini-pro": {
        "name": "Gemini Pro",
        "description": "Google's production model",
        "provider": "Google",
        "context": "32K tokens",
        "cost": "$0.25/1M"
    },
    "anthropic/claude-3.5-sonnet": {
        "name": "Claude 3.5 Sonnet",
        "description": "Anthropic's balanced model - great for structured output",
        "provider": "Anthropic",
        "context": "200K tokens",
        "cost": "$3/1M"
    },
    "anthropic/claude-3-haiku": {
        "name": "Claude 3 Haiku",
        "description": "Fast and cheap Claude model",
        "provider": "Anthropic",
        "context": "200K tokens",
        "cost": "$0.25/1M"
    },
    "openai/gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "description": "OpenAI's most capable model",
        "provider": "OpenAI",
        "context": "128K tokens",
        "cost": "$10/1M"
    },
    "openai/gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "description": "Fast and affordable GPT-4 variant",
        "provider": "OpenAI",
        "context": "128K tokens",
        "cost": "$0.15/1M"
    },
    "meta-llama/llama-3.1-70b-instruct": {
        "name": "Llama 3.1 70B",
        "description": "Meta's open-source large model",
        "provider": "Meta",
        "context": "128K tokens",
        "cost": "$0.40/1M"
    },
    "meta-llama/llama-3.1-8b-instruct": {
        "name": "Llama 3.1 8B",
        "description": "Meta's fast open-source model",
        "provider": "Meta",
        "context": "128K tokens",
        "cost": "$0.05/1M"
    },
    "mistralai/mixtral-8x7b-instruct": {
        "name": "Mixtral 8x7B",
        "description": "Mistral's MoE model - great balance",
        "provider": "Mistral",
        "context": "32K tokens",
        "cost": "$0.27/1M"
    },
    "deepseek/deepseek-chat": {
        "name": "DeepSeek Chat",
        "description": "DeepSeek's capable chat model",
        "provider": "DeepSeek",
        "context": "64K tokens",
        "cost": "$0.14/1M"
    },
    "qwen/qwen-2.5-72b-instruct": {
        "name": "Qwen 2.5 72B",
        "description": "Alibaba's large instruction model",
        "provider": "Alibaba",
        "context": "128K tokens",
        "cost": "$0.35/1M"
    }
}

# CV Data structure template
CV_STRUCTURE = """
{
    "name": "Full Name (culturally appropriate for the region)",
    "title": "Professional Title matching the role",
    "email": "professional.email@domain.com",
    "phone": "+XX XXX-XXX-XXXX (format appropriate for region)",
    "profile_summary": "2-3 compelling sentences about professional background, expertise, and career goals",
    "skills": [
        {"name": "Skill Name", "level": 85}
    ],
    "languages": [
        {"name": "Language", "level": 5}
    ],
    "experience": [
        {
            "title": "Job Title",
            "company": "Company Name",
            "years": "2020 - Present",
            "description": "Brief, impactful description of responsibilities and achievements"
        }
    ],
    "education": [
        {
            "degree": "Degree Name",
            "institution": "University Name",
            "years": "2015 - 2019"
        }
    ],
    "certificates": [
        {"year": "2023", "title": "Certificate Name", "honors": "Certification Body"}
    ],
    "interests": [
        {"name": "Interest", "icon": "fa-icon-name"}
    ],
    "social": [
        {"platform": "LinkedIn", "username": "username", "url": "https://linkedin.com/in/username", "icon": "fa-linkedin"}
    ]
}
"""

SYSTEM_PROMPT = """You are a professional CV/resume content generator. Your task is to create realistic, believable professional profiles.

OUTPUT FORMAT: You MUST output ONLY valid JSON that matches EXACTLY this structure:
{structure}

CRITICAL RULES:
1. Generate culturally appropriate names for the specified origin region
2. Skills should have levels from 60-95 (percentage proficiency) - be realistic
3. Languages should have levels from 1-5 (1=basic, 3=conversational, 5=native)
4. Include 4-6 skills directly relevant to the specified role
5. Include 2-3 languages (always include English)
6. Include 2-3 work experiences with realistic company names
7. Include 1-2 education entries from real universities in the region
8. Include 1-3 certificates relevant to the role
9. Include 3-4 interests with Font Awesome icon names (fa-code, fa-music, fa-book, fa-plane, etc.)
10. Include GitHub and LinkedIn social links with realistic usernames
11. Make the profile feel authentic and professional
12. Output ONLY the JSON object - no markdown, no explanations, no code blocks"""


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
    origin: str = "United States",
    gender: str = "any",
    model: Optional[str] = None
) -> dict:
    """
    Generate realistic CV content using OpenRouter.
    
    Args:
        role: Target professional role
        origin: Geographic origin for culturally appropriate names
        gender: Gender for name generation
        model: OpenRouter model ID to use (defaults to env var DEFAULT_LLM_MODEL)
    
    Returns:
        Dictionary containing all CV data
    """
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("⚠️ No OpenRouter API key found, using mock data")
        return _generate_mock_cv(role, origin, gender)
    
    # Use provided model or default
    model_id = model or os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    
    user_prompt = (
        f"Generate a complete, realistic CV for a {gender if gender != 'any' else ''} "
        f"{role} professional from {origin}. "
        f"Make it authentic with real-sounding companies, universities, and achievements."
    )
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-cv-suite.local",
                    "X-Title": "AI CV Suite"
                },
                json={
                    "model": model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT.format(structure=CV_STRUCTURE)
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Clean up the response
                    content = content.strip()
                    
                    # Remove markdown code blocks if present
                    if content.startswith("```"):
                        lines = content.split("\n")
                        # Remove first and last lines (code block markers)
                        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                        content = content.strip()
                    
                    if content.startswith("json"):
                        content = content[4:].strip()
                    
                    try:
                        cv_data = json.loads(content)
                        print(f"✅ CV content generated with {model_id}")
                        return cv_data
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON parse error: {e}")
                        print(f"Raw content: {content[:500]}")
            
            print(f"⚠️ OpenRouter API error: {response.status_code}")
            return _generate_mock_cv(role, origin, gender)
            
    except Exception as e:
        print(f"⚠️ OpenRouter API exception: {e}")
        return _generate_mock_cv(role, origin, gender)


def _generate_mock_cv(role: str, origin: str, gender: str) -> dict:
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
    skills = [{"name": s, "level": random.randint(70, 95)} for s in selected_skills]
    
    email_name = name.lower().replace(" ", ".").replace("'", "")
    
    return {
        "name": name,
        "title": role,
        "email": f"{email_name}@gmail.com",
        "phone": f"+1 {random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "profile_summary": f"Experienced {role} with a passion for delivering high-quality work and proven track record in fast-paced environments.",
        "skills": skills,
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
        "interests": [
            {"name": "Technology", "icon": "fa-laptop-code"},
            {"name": "Travel", "icon": "fa-plane"},
            {"name": "Reading", "icon": "fa-book"}
        ],
        "social": [
            {"platform": "GitHub", "username": f"@{email_name.split('.')[0]}", "url": f"https://github.com/{email_name.split('.')[0]}", "icon": "fa-github"},
            {"platform": "LinkedIn", "username": email_name.replace(".", ""), "url": f"https://linkedin.com/in/{email_name.replace('.', '')}", "icon": "fa-linkedin"}
        ]
    }
