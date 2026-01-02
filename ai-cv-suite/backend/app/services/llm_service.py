"""
LLM Service - OpenAI/Gemini Handler for CV Content Generation
Generates realistic CV data based on role, origin, and other parameters
"""

import os
import json
import random
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# CV Data structure template for consistent output
CV_STRUCTURE = """
{
    "name": "Full Name",
    "title": "Professional Title",
    "email": "email@example.com",
    "phone": "+1 555-123-4567",
    "profile_summary": "2-3 sentences about professional background and goals",
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
            "description": "Brief description of responsibilities and achievements"
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

SYSTEM_PROMPT = """You are a JSON generator that creates realistic professional CV/resume data.
You MUST output ONLY valid JSON that matches EXACTLY this structure:

{structure}

Rules:
1. Generate realistic, believable data for a professional in the specified role
2. Names should be culturally appropriate for the origin region
3. Skills should have levels from 50-100 (percentage proficiency)
4. Languages should have levels from 1-5 (1=basic, 5=native)
5. Include 4-6 skills relevant to the role
6. Include 2-3 languages
7. Include 2-3 work experiences
8. Include 2-3 education entries
9. Include 1-3 certificates relevant to the role
10. Include 3-4 interests with Font Awesome icon names (like fa-code, fa-music, fa-book)
11. Include 1-2 social links (GitHub, LinkedIn)
12. Output ONLY the JSON object, no markdown formatting or explanation
"""


async def generate_cv_content(
    role: str = "Software Developer",
    origin: str = "United States",
    gender: str = "any"
) -> dict:
    """
    Generate realistic CV content using LLM.
    
    Args:
        role: Target professional role
        origin: Geographic origin for culturally appropriate names
        gender: Gender for name generation
    
    Returns:
        Dictionary containing all CV data
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "gemini":
        return await _generate_with_gemini(role, origin, gender)
    elif provider == "openai":
        return await _generate_with_openai(role, origin, gender)
    else:
        # Fallback to mock data
        return _generate_mock_cv(role, origin, gender)


async def _generate_with_openai(role: str, origin: str, gender: str) -> dict:
    """Generate CV content using OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key or api_key.startswith("sk-your"):
        return _generate_mock_cv(role, origin, gender)
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=api_key)
        
        user_prompt = f"Generate a realistic CV for a {gender if gender != 'any' else 'professional'} {role} from {origin}."
        
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(structure=CV_STRUCTURE)},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return _generate_mock_cv(role, origin, gender)


async def _generate_with_gemini(role: str, origin: str, gender: str) -> dict:
    """Generate CV content using Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key or api_key.startswith("AIza-your"):
        return _generate_mock_cv(role, origin, gender)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
{SYSTEM_PROMPT.format(structure=CV_STRUCTURE)}

Generate a realistic CV for a {gender if gender != 'any' else 'professional'} {role} from {origin}.
Output ONLY the JSON object.
"""
        
        response = await model.generate_content_async(prompt)
        
        # Parse the response
        text = response.text.strip()
        # Remove potential markdown formatting
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        return json.loads(text)
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _generate_mock_cv(role, origin, gender)


def _generate_mock_cv(role: str, origin: str, gender: str) -> dict:
    """Generate mock CV data when APIs are unavailable."""
    
    # Name pools by origin/region
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
            "male": ["Michael Johnson", "Carlos Rodriguez", "David Williams", "Juan Martinez", "Robert Garcia"],
            "female": ["Sarah Miller", "Maria Gonzalez", "Jennifer Anderson", "Ana Silva", "Emily Thompson"]
        },
        "default": {
            "male": ["John Smith", "Michael Brown", "David Wilson", "James Taylor", "Robert Anderson"],
            "female": ["Emily Johnson", "Sarah Williams", "Jessica Davis", "Amanda Miller", "Rachel Moore"]
        }
    }
    
    # Determine origin category
    origin_lower = origin.lower()
    if any(x in origin_lower for x in ["europe", "germany", "france", "italy", "uk", "spain", "poland"]):
        origin_key = "europe"
    elif any(x in origin_lower for x in ["asia", "china", "japan", "korea", "india", "vietnam"]):
        origin_key = "asia"
    elif any(x in origin_lower for x in ["america", "usa", "brazil", "mexico", "canada", "argentina"]):
        origin_key = "americas"
    else:
        origin_key = "default"
    
    # Select name based on gender
    if gender.lower() == "male":
        name = random.choice(names_by_origin[origin_key]["male"])
    elif gender.lower() == "female":
        name = random.choice(names_by_origin[origin_key]["female"])
    else:
        all_names = names_by_origin[origin_key]["male"] + names_by_origin[origin_key]["female"]
        name = random.choice(all_names)
    
    # Generate role-appropriate skills
    skill_pools = {
        "devops": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "Linux", "Python", "Ansible"],
        "developer": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "REST APIs", "TypeScript"],
        "designer": ["Figma", "Adobe XD", "Photoshop", "Illustrator", "UI/UX", "Sketch", "CSS", "Prototyping"],
        "manager": ["Project Management", "Agile", "Scrum", "Leadership", "Strategy", "Communication", "Stakeholder Management"],
        "data": ["Python", "SQL", "Machine Learning", "TensorFlow", "Data Analysis", "Statistics", "Power BI", "Pandas"],
        "default": ["Communication", "Problem Solving", "Team Work", "Project Management", "Microsoft Office", "Leadership"]
    }
    
    role_lower = role.lower()
    if "devops" in role_lower or "sre" in role_lower:
        skills_pool = skill_pools["devops"]
    elif "developer" in role_lower or "engineer" in role_lower or "programmer" in role_lower:
        skills_pool = skill_pools["developer"]
    elif "design" in role_lower or "ux" in role_lower:
        skills_pool = skill_pools["designer"]
    elif "manager" in role_lower or "lead" in role_lower:
        skills_pool = skill_pools["manager"]
    elif "data" in role_lower or "analyst" in role_lower or "scientist" in role_lower:
        skills_pool = skill_pools["data"]
    else:
        skills_pool = skill_pools["default"]
    
    selected_skills = random.sample(skills_pool, min(5, len(skills_pool)))
    skills = [{"name": s, "level": random.randint(70, 95)} for s in selected_skills]
    
    # Generate email from name
    email_name = name.lower().replace(" ", ".").replace("'", "")
    domains = ["gmail.com", "outlook.com", "proton.me", "email.com"]
    email = f"{email_name}@{random.choice(domains)}"
    
    return {
        "name": name,
        "title": role,
        "email": email,
        "phone": f"+1 {random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "profile_summary": f"Experienced {role} with a passion for delivering high-quality work. Proven track record of success in fast-paced environments with strong problem-solving abilities and excellent communication skills.",
        "skills": skills,
        "languages": [
            {"name": "English", "level": 5},
            {"name": random.choice(["Spanish", "French", "German", "Mandarin", "Portuguese"]), "level": random.randint(2, 4)}
        ],
        "experience": [
            {
                "title": f"Senior {role}",
                "company": random.choice(["Tech Solutions Inc", "Global Systems Corp", "Innovation Labs", "Digital Ventures"]),
                "years": "2021 - Present",
                "description": f"Leading initiatives and delivering impactful solutions as a {role}. Collaborating with cross-functional teams to drive business objectives."
            },
            {
                "title": role,
                "company": random.choice(["StartUp Co", "Enterprise Tech", "Cloud Services Ltd", "Data Systems"]),
                "years": "2018 - 2021",
                "description": f"Developed expertise in key areas while contributing to major projects and process improvements."
            }
        ],
        "education": [
            {
                "degree": random.choice(["Master's in Computer Science", "MBA", "Master's in Engineering", "Master's in Data Science"]),
                "institution": random.choice(["Stanford University", "MIT", "Cambridge University", "ETH Zurich"]),
                "years": "2016 - 2018"
            },
            {
                "degree": random.choice(["Bachelor's in Computer Science", "Bachelor's in Engineering", "Bachelor's in Business"]),
                "institution": random.choice(["UC Berkeley", "University of Michigan", "Georgia Tech", "Columbia University"]),
                "years": "2012 - 2016"
            }
        ],
        "certificates": [
            {"year": "2023", "title": random.choice(["AWS Solutions Architect", "PMP", "Scrum Master", "Google Cloud Engineer"]), "honors": "Professional"},
            {"year": "2022", "title": random.choice(["Azure Developer", "CISSP", "ITIL", "Six Sigma"]), "honors": "Associate"}
        ],
        "interests": [
            {"name": "Technology", "icon": "fa-laptop-code"},
            {"name": "Travel", "icon": "fa-plane"},
            {"name": "Reading", "icon": "fa-book"},
            {"name": "Music", "icon": "fa-music"}
        ],
        "social": [
            {"platform": "GitHub", "username": f"@{email_name.split('.')[0]}", "url": f"https://github.com/{email_name.split('.')[0]}", "icon": "fa-github"},
            {"platform": "LinkedIn", "username": email_name.replace(".", ""), "url": f"https://linkedin.com/in/{email_name.replace('.', '')}", "icon": "fa-linkedin"}
        ]
    }
