"""
Role Categories Module - Maps roles to broad category folders for Smart Category feature.

This module provides a function to categorize any role (regardless of seniority level)
into a broad category folder for organized PDF storage.
"""

import re
from typing import Optional

# Category keyword mappings
# Order matters - more specific matches should come first
CATEGORY_KEYWORDS = {
    # Technical Art (before general Art/Creative to catch "3D Artist" etc.)
    "Technical_Art": [
        "3d", "2d", "vfx", "motion graphics", "motion designer", "technical artist",
        "rigger", "rigging", "animator", "texture", "shader", "modeler", "modeling",
        "concept art", "environment artist", "character artist", "lighting artist"
    ],
    
    # Development
    "Developer": [
        "developer", "engineer", "programmer", "coder", "software", "frontend", 
        "backend", "fullstack", "full-stack", "full stack", "web dev", "mobile dev",
        "ios", "android", "devops", "cloud engineer", "sre", "site reliability",
        "embedded", "firmware", "systems engineer"
    ],
    
    # Data & AI
    "Data": [
        "data scientist", "data analyst", "data engineer", "machine learning", 
        "ml engineer", "ai engineer", "deep learning", "nlp", "bi analyst",
        "business intelligence", "analytics", "statistician", "quantitative"
    ],
    
    # Design (UX/UI/Product)
    "Design": [
        "ux", "ui", "user experience", "user interface", "product design",
        "graphic design", "visual design", "interaction design", "design system",
        "brand design", "web design"
    ],
    
    # Creative & Artistic (general)
    "Creative": [
        "art director", "creative director", "illustrator", "photographer",
        "videographer", "filmmaker", "director of photography", "cinematographer",
        "music", "musician", "composer", "singer", "audio", "sound design",
        "voice", "actor", "actress", "performer", "dancer", "choreographer"
    ],
    
    # Management & Leadership
    "Management": [
        "manager", "management", "project manager", "product manager", "pm",
        "scrum master", "agile coach", "team lead", "tech lead", "head of",
        "supervisor", "coordinator"
    ],
    
    # Executive / C-Suite
    "Executive": [
        "ceo", "cto", "cfo", "coo", "cmo", "cio", "chief", "vp", "vice president",
        "director", "president", "founder", "co-founder", "partner", "principal"
    ],
    
    # Communication & Marketing
    "Communication": [
        "marketing", "content", "copywriter", "copy writer", "social media",
        "pr", "public relations", "communications", "brand manager", "seo",
        "growth", "community manager", "editor", "journalist", "writer"
    ],
    
    # Sales & Business Development
    "Sales": [
        "sales", "account executive", "account manager", "business development",
        "bdr", "sdr", "customer success", "client", "partnership"
    ],
    
    # Human Resources
    "HR": [
        "hr", "human resources", "recruiter", "recruiting", "talent acquisition",
        "people operations", "people ops", "compensation", "benefits"
    ],
    
    # Finance & Accounting
    "Finance": [
        "finance", "financial", "accountant", "accounting", "controller",
        "treasury", "audit", "tax", "bookkeeper", "payroll"
    ],
    
    # Legal
    "Legal": [
        "lawyer", "attorney", "legal", "counsel", "paralegal", "compliance",
        "regulatory", "contract"
    ],
    
    # Healthcare & Medical
    "Healthcare": [
        "doctor", "physician", "nurse", "medical", "healthcare", "health care",
        "clinical", "therapist", "dentist", "pharmacist", "surgeon", "vet"
    ],
    
    # Education & Training
    "Education": [
        "teacher", "professor", "instructor", "educator", "tutor", "trainer",
        "teaching", "academic", "faculty", "lecturer", "coach"
    ],
    
    # Engineering (non-software)
    "Engineering": [
        "mechanical engineer", "electrical engineer", "civil engineer",
        "chemical engineer", "industrial engineer", "structural engineer",
        "aerospace", "automotive engineer", "manufacturing"
    ],
    
    # Architecture & Construction
    "Architecture": [
        "architect", "architecture", "urban planner", "interior design",
        "construction", "builder", "site manager", "quantity surveyor"
    ],
    
    # Operations & Logistics
    "Operations": [
        "operations", "logistics", "supply chain", "warehouse", "inventory",
        "procurement", "purchasing", "fleet", "distribution"
    ],
    
    # Customer Service & Support
    "Support": [
        "customer service", "support", "help desk", "technical support",
        "customer care", "call center"
    ],
    
    # Research & Science
    "Research": [
        "researcher", "scientist", "research", "laboratory", "lab tech",
        "biologist", "chemist", "physicist", "geologist"
    ],
    
    # Security
    "Security": [
        "security", "cybersecurity", "information security", "infosec",
        "penetration", "ethical hacker", "soc analyst"
    ]
}


def get_category_for_role(role: str) -> str:
    """
    Map a role to its category folder name.
    
    Args:
        role: The job title/role (e.g., "Senior Frontend Developer", "3D Artist")
        
    Returns:
        Category folder name (e.g., "Developer", "Technical_Art", "Other")
    """
    if not role:
        return "Other"
    
    # Normalize: lowercase, remove extra spaces
    role_lower = role.lower().strip()
    role_lower = re.sub(r'\s+', ' ', role_lower)
    
    # Remove seniority prefixes for matching (don't affect categorization)
    seniority_prefixes = [
        "senior ", "junior ", "jr ", "sr ", "lead ", "principal ", 
        "staff ", "associate ", "intern ", "trainee ", "entry level ",
        "mid ", "mid-level "
    ]
    
    clean_role = role_lower
    for prefix in seniority_prefixes:
        if clean_role.startswith(prefix):
            clean_role = clean_role[len(prefix):]
            break  # Only remove one prefix
    
    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in clean_role or keyword in role_lower:
                return category
    
    # Fallback
    return "Other"


def ensure_category_folder(base_path, category: str):
    """
    Ensure the category subfolder exists.
    
    Args:
        base_path: Path object to base PDF directory
        category: Category folder name
        
    Returns:
        Path object to the category folder
    """
    from pathlib import Path
    
    category_path = Path(base_path) / category
    category_path.mkdir(parents=True, exist_ok=True)
    return category_path


# For debugging/testing
if __name__ == "__main__":
    test_roles = [
        "Senior Frontend Developer",
        "Junior 3D Artist",
        "Art Director",
        "Data Scientist",
        "Product Manager",
        "CEO",
        "Marketing Specialist",
        "Teacher",
        "Registered Nurse",
        "Random Unknown Role"
    ]
    
    for role in test_roles:
        cat = get_category_for_role(role)
        print(f"{role:30} -> {cat}")
