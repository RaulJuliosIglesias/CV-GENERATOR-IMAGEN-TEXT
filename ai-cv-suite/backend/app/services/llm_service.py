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

# Enhanced system prompt for detailed CVs
SYSTEM_PROMPT = """You are an expert CV/Resume writer. Generate COMPLETE, DETAILED, PROFESSIONAL CVs in JSON format.

REQUIREMENTS BY EXPERIENCE LEVEL:
- any/junior (0-2 years): 1 page, 1-2 experiences, education focus
- mid (2-5 years): 1-2 pages, 2-3 experiences, balanced
- senior (5-10 years): 2 FULL pages, 3-5 experiences, leadership
- expert (10+ years): 2 FULL pages, 4-6 experiences, strategic vision

CONTENT GUIDELINES:

1. EXPERIENCE - MUST BE DETAILED:
   - Junior: 100-150 words per role
   - Mid: 150-250 words per role
   - Senior/Expert: 250-400 words per role
   - Include: specific projects, technologies (8-12 for senior), methodologies, achievements with metrics, team size, impact
   - Example metrics: "Reduced API latency by 45%", "Led team of 8"

2. SKILLS (15-30 items):
   - Technical skills with levels 60-100
   - Categories: Languages, Frameworks, Databases, Cloud, DevOps
   - Soft skills: Leadership, Communication, etc.

3. OUTPUT STRICT JSON:
{
  "name": "Realistic Full Name",
  "title": "Professional Job Title",
  "location": "City, Country",
  "email": "name@email.com",
  "phone": "+X XXX XXX XXX",
  "profile_summary": "150-500 words based on level - career highlights, expertise, goals",
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "City",
      "start_date": "Month YYYY",
      "end_date": "Month YYYY or Present",
      "description": "DETAILED description with projects, tech stack, achievements, metrics, team work...",
      "technologies": ["Tech1", "Tech2",...],
      "achievements": ["Achievement with metric"...]
    }
  ],
  "skills": {
    "technical": [
      {"name": "Skill", "level": 90, "years": 4, "category": "Languages"}
    ],
    "soft": ["Leadership", "Communication",...]
  },
  "education": [
    {
      "degree": "Degree Name",
      "institution": "University",
      "location": "City",
      "start_year": "YYYY",
      "end_year": "YYYY",
      "honors": "GPA 3.8/4.0"
    }
  ],
  "certificates": [
    {
      "name": "Cert Name",
      "issuer": "Organization",
      "date": "Month YYYY",
      "credential_id": "ABC123"
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "150-250 words about problem, solution, tech, impact",
      "url": "https://github.com/user/repo",
      "technologies": ["React", "Node.js",...]
    }
  ],
  "languages": [
    {"name": "English", "level": "C2", "proficiency": "Native"}
  ],
  "interests": ["AI/ML", "Open Source",...],
  "social": {
    "github": "username",
    "linkedin": "username",
    "portfolio": "https://site.com"
  }
}

RULES:
1. Match detail level to experience (senior = MUCH more detail)
2. Use realistic metrics and achievements
3. Names match gender/ethnicity
4. Technologies current and relevant
5. OUTPUT ONLY VALID JSON - NO markdown, NO explanations"""


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
    
    return f"""Generate a COMPLETE, REALISTIC CV for:

**Profile**:
- Role: {role}
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
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("⚠️ No OpenRouter API key found, using mock data")
        return _generate_mock_cv(role, origin, gender, expertise)
    
    # Use provided model or default
    model_id = model or os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    
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
                        print(f"✅ CV content generated with {model_id}")
                        return cv_data
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON parse error: {e}")
                        print(f"Raw content: {content[:500]}")
            
            print(f"⚠️ OpenRouter API error: {response.status_code}")
            return _generate_mock_cv(role, origin, gender, expertise)
            
    except Exception as e:
        print(f"⚠️ OpenRouter API exception: {e}")
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
