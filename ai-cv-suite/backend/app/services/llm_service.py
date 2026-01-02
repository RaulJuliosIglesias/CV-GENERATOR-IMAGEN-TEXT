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


def resolve_role(role: str) -> str:
    """Convert 'any' to a random high-demand tech role."""
    if role.lower() == "any":
        resolved = random.choice(RANDOM_TECH_ROLES)
        print(f"DEBUG: Resolved 'any' role to: {resolved}")
        return resolved
    return role

# Enhanced system prompt for detailed CVs
# Enhanced system prompt for detailed CVs
SYSTEM_PROMPT = """You are an expert Executive CV/Resume Writer for top-tier tech roles. 
Your goal is to generate an EXTREMELY DETAILED, RICH, and PREMIUM curriculum vitae.

RULES FOR CONTENT GENERATION:
1.  **Length & Detail**: The content MUST be sufficient for a 2-page CV. detailed descriptions are required.
    - EXPERIENCE: Generate 3-4 roles. For the most recent role, provide 5-7 distinct bullet points with metrics (e.g., "Improved latency by 40%").
    - PROJECTS: Generate 3-4 detailed projects (hackathons, open source, complex apps). Description should be 2-3 sentences each.
    - SUMMARY: write a compelling, 4-line executive summary.

2.  **Creativity**: Do generic "team player" bullet points. Use strong action verbs (Architected, Orchestrated, Spearheaded).

3.  **Strict JSON Structure**: Return ONLY valid JSON matching this exact structure:
{
  "name": "Full Name",
  "title": "Target Role",
  "email": "email@example.com",
  "phone": "+1 234 567 890",
  "location": "City, Country",
  "profile_summary": "Compelling executive summary...",
  "skills": {
    "technical": [
        {"name": "Skill 1", "level": 95}, 
        {"name": "Skill 2", "level": 90}
    ]
  },
  "social": {
    "github": "https://github.com/username",
    "linkedin": "https://linkedin.com/in/username",
    "portfolio": "https://portfolio.com"
  },
  "experiences": [
    {
      "title": "Role Title",
      "company": "Company Name",
      "date_range": "2020 - Present",
      "description": "High-level overview of the role responsibility.",
      "achievements": [
        "Spearheaded the migration of legacy monolith to microservices...",
        "Reduced cloud costs by 35% through optimization..."
      ]
    }
  ],
  "education": [
    {
       "degree": "Master of Science in CS",
       "institution": "University Name",
       "year": "2018-2020",
       "honors": "Summa Cum Laude"
    }
  ],
  "certificates": [
    {"name": "AWS Solutions Architect", "issuer": "Amazon", "date": "2022"}
  ],
  "interests": ["Quantum Computing", "Generative AI Art", "Triathlon"],
  "projects": [
    {
       "name": "Project Alpha",
       "description": "A high-performance distributed system for..."
    }
  ],
  "languages": [
    {"name": "English", "level_num": 5},
    {"name": "Spanish", "level_num": 4}
  ]
}
"""


def create_user_prompt(role: str, expertise: str, age: int, gender: str, ethnicity: str, origin: str, remote: bool) -> str:
    """Create detailed user prompt based on profile."""
    
    expertise_map = {
        'any': '2-5',
        'junior': '0-2',
        'mid': '2-5',
        'senior': '5-10',
        'expert': '10+'
    }
    
    years_experience = expertise_map.get(expertise, '2-5')
    
    detail_requirement = {
        'any': "balanced detail",
        'junior': "focus on education and potential",
        'mid': "balanced skills and achievements",
        'senior': "MAXIMUM DETAIL - 2 full pages with leadership focus",
        'expert': "MAXIMUM DETAIL - 2 full pages with strategic vision"
    }
    
    detail_level = detail_requirement.get(expertise, "balanced detail")
    
    
    role_instruction = f"Role: {role}"
    if role.lower() == "any":
        role_instruction = "Role: CHOOSE A RANDOM HIGH-DEMAND TECH ROLE (e.g. Senior DevOps, AI Research Scientist, Blockchain Lead, Full Stack Architect, Data Engineer)"

    return f"""Generate a COMPLETE, REALISTIC CV for:

**Profile**:
- {role_instruction}
- Experience Level: {expertise} ({years_experience} years)
- Age: {age} years old
- Gender: {gender}
- Ethnicity: {ethnicity}
- Location/Origin: {origin}
- Remote Work: {"Preferred" if remote else "Flexible"}

**Requirements**:
- {detail_level}
- Use appropriate experience count for {expertise} level
- Include specific technologies for {role}
- Generate realistic name matching {gender} and {ethnicity}
- Make achievements quantifiable with metrics

OUTPUT ONLY THE JSON, NO OTHER TEXT."""


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
        print("WARNING: No OpenRouter API key found, using mock data")
        return _generate_mock_cv(role, origin, gender, expertise)
    
    # Use provided model or default
    model_id = model or os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    print(f"DEBUG: Using LLM model: {model_id}")
    
    user_prompt = create_user_prompt(role, expertise, age, gender, ethnicity, origin, remote)
    
    # Adjust max_tokens based on expertise level
    max_tokens = {
        'junior': 2000,
        'mid': 3000,
        'senior': 4000,
        'expert': 4000,
        'any': 2500
    }.get(expertise, 2500)
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
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
                        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                        content = content.strip()
                    
                    if content.startswith("json"):
                        content = content[4:].strip()
                    
                    try:
                        cv_data = json.loads(content)
                        # Ensure data structure safety
                        cv_data = ensure_social_dict(cv_data)
                        print(f"SUCCESS: CV content generated with {model_id}")
                        return cv_data
                    except json.JSONDecodeError as e:
                        print(f"WARNING: JSON parse error: {e}")
                        print(f"Raw content: {content[:500]}")
            
            print(f"WARNING: OpenRouter API error: {response.status_code}")
            return _generate_mock_cv(role, origin, gender, expertise)
            
    except Exception as e:
        print(f"WARNING: OpenRouter API exception: {e}")
        return _generate_mock_cv(role, origin, gender, expertise)


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
