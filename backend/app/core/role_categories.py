"""
Role Categories Module - Maps roles to broad category folders for Smart Category feature.

This module provides a function to categorize any role (regardless of seniority level)
into a broad category folder for organized PDF storage.
"""

import re
from typing import Optional

# Category keyword mappings
# Order matters - more specific matches should come first
# Categories are organized by industry/function with clear separation
CATEGORY_KEYWORDS = {
    # ===========================================
    # TECH INDUSTRY
    # ===========================================
    
    # IT & Infrastructure (separate from Software Development)
    "IT_Infrastructure": [
        "it support", "it specialist", "it administrator", "it manager", "it director",
        "system administrator", "sysadmin", "network administrator", "network engineer",
        "helpdesk", "help desk", "desktop support", "technical support", "it technician",
        "dba", "database administrator", "database admin", "database engineer",
        "cloud administrator", "infrastructure", "it operations", "it ops",
        "systems analyst", "network analyst", "it security", "it coordinator"
    ],
    
    # Software Development (pure dev roles)
    "Software_Development": [
        "software developer", "software engineer", "programmer", "coder",
        "frontend developer", "frontend engineer", "backend developer", "backend engineer",
        "fullstack developer", "fullstack engineer", "full-stack", "full stack developer",
        "web developer", "mobile developer", "mobile engineer",
        "ios developer", "android developer", "react developer", "python developer",
        "java developer", "javascript developer", "golang developer", ".net developer",
        "embedded developer", "firmware engineer", "systems programmer",
        "game developer", "game programmer", "engine programmer", "gameplay programmer"
    ],
    
    # DevOps & Platform Engineering
    "DevOps": [
        "devops", "devsecops", "site reliability", "sre",
        "platform engineer", "build engineer", "release engineer",
        "cloud engineer", "cloud architect", "infrastructure engineer",
        "kubernetes", "docker", "ci/cd", "automation engineer"
    ],
    
    # QA & Testing
    "QA_Testing": [
        "qa engineer", "qa analyst", "quality assurance", "test engineer",
        "tester", "automation tester", "manual tester", "sdet",
        "test lead", "qa lead", "qa manager", "quality engineer"
    ],
    
    # Data & AI/ML
    "Data_AI": [
        "data scientist", "data analyst", "data engineer", "machine learning",
        "ml engineer", "ai engineer", "deep learning", "nlp engineer",
        "bi analyst", "business intelligence", "analytics engineer",
        "data architect", "ai researcher", "ai trainee", "ml researcher",
        "statistician", "quantitative analyst", "data visualization"
    ],
    
    # Cybersecurity
    "Cybersecurity": [
        "cybersecurity", "information security", "infosec", "security engineer",
        "security analyst", "penetration tester", "ethical hacker", "soc analyst",
        "security architect", "security consultant", "ciso", "security specialist"
    ],
    
    # ===========================================
    # CREATIVE & DESIGN
    # ===========================================
    
    # Technical Art (VFX, Animation, 3D for film/games)
    "Technical_Art": [
        "3d artist", "2d artist", "vfx artist", "vfx supervisor",
        "motion graphics", "motion designer", "technical artist",
        "rigger", "rigging artist", "character rigger",
        "animator", "3d animator", "2d animator",
        "texture artist", "shader artist", "modeler", "3d modeler",
        "concept artist", "environment artist", "character artist",
        "lighting artist", "compositor", "compositing",
        "creature designer", "hard surface modeler", "prop artist",
        "level artist", "fx artist", "effects artist"
    ],
    
    # Game Development (game-specific roles beyond programming)
    "Game_Development": [
        "game designer", "level designer", "narrative designer",
        "game artist", "game producer", "game director",
        "game writer", "quest designer", "systems designer",
        "ue4", "ue5", "unreal", "unity developer", "game engine"
    ],
    
    # UX/UI & Product Design
    "Design": [
        "ux designer", "ui designer", "ux/ui", "user experience", "user interface",
        "product designer", "interaction designer", "design system",
        "visual designer", "graphic designer", "web designer",
        "brand designer", "service designer", "design lead", "design director"
    ],
    
    # Creative & Arts (non-technical)
    "Creative": [
        "art director", "creative director", "illustrator",
        "photographer", "videographer", "filmmaker",
        "musician", "composer", "singer", "audio engineer", "sound designer",
        "voice actor", "actor", "actress", "performer", "dancer", "choreographer",
        "fine artist", "painter", "sculptor", "writer", "author"
    ],
    
    # ===========================================
    # FILM & PRODUCTION
    # ===========================================
    
    "Film_Production": [
        "camera operator", "camera assistant", "cinematographer", "dop",
        "director of photography", "gaffer", "grip", "best boy", "dit",
        "colorist", "color grader", "storyboard artist",
        "production assistant", "pa", "line producer", "script supervisor",
        "focus puller", "steadicam", "dolly grip", "boom operator",
        "production coordinator", "key grip", "set decorator", "prop master",
        "makeup artist", "hair stylist", "location scout", "film editor",
        "casting director", "unit production manager", "assistant director",
        "producer", "executive producer", "showrunner"
    ],
    
    # ===========================================
    # BUSINESS & MANAGEMENT
    # ===========================================
    
    # Executive / C-Suite
    "Executive": [
        "ceo", "cto", "cfo", "coo", "cmo", "cio", "cpo", "cdo", "chro", "cso",
        "chief", "vp", "vice president", "svp", "evp", "avp",
        "president", "founder", "co-founder", "partner", "principal",
        "board member", "trustee", "managing director"
    ],
    
    # Management & Leadership (mid-level)
    "Management": [
        "manager", "director", "head of", "team lead", "tech lead",
        "supervisor", "coordinator", "project manager", "program manager",
        "delivery manager", "general manager", "operations manager",
        "scrum master", "agile coach", "product owner"
    ],
    
    # Product Management
    "Product": [
        "product manager", "product owner", "product lead",
        "product director", "product strategist", "product analyst",
        "associate product manager", "apm", "group product manager"
    ],
    
    # Business Development (separate from Sales)
    "Business_Development": [
        "business development", "bdr", "bd manager", "bd director",
        "partnerships", "partner manager", "strategic partnerships",
        "alliances", "channel partner", "business analyst", "strategy",
        "management consultant", "strategy consultant", "consultant"
    ],
    
    # ===========================================
    # SALES & CUSTOMER
    # ===========================================
    
    # Sales
    "Sales": [
        "sales", "account executive", "account manager", "sales representative",
        "sales manager", "sales director", "sales engineer",
        "sdr", "sales development", "inside sales", "outside sales",
        "sales associate", "sales consultant", "regional sales"
    ],
    
    # Customer Success & Support
    "Customer_Success": [
        "customer success", "csm", "customer success manager",
        "account manager", "client services", "client manager",
        "customer support", "customer service", "support specialist",
        "help desk", "call center", "customer care", "technical support"
    ],
    
    # ===========================================
    # MARKETING & COMMUNICATION
    # ===========================================
    
    # Marketing (digital & traditional)
    "Marketing": [
        "marketing manager", "marketing director", "marketing specialist",
        "digital marketing", "performance marketing", "growth marketing",
        "demand generation", "marketing analyst", "marketing coordinator",
        "seo specialist", "sem specialist", "ppc", "paid media",
        "email marketing", "marketing automation", "cmo"
    ],
    
    # Content & Communications
    "Communications": [
        "content writer", "copywriter", "content strategist", "content manager",
        "social media manager", "community manager",
        "pr specialist", "public relations", "communications manager",
        "brand manager", "brand strategist", "editor", "journalist",
        "technical writer", "documentation"
    ],
    
    # Media & Content Creation (influencers, podcasters)
    "Media_Content": [
        "podcaster", "podcast host", "youtuber", "content creator",
        "streamer", "live streamer", "influencer", "vlogger", "tiktoker",
        "broadcaster", "radio host", "tv host", "presenter", "anchor",
        "media personality", "dj"
    ],
    
    # ===========================================
    # PEOPLE & HR
    # ===========================================
    
    # Talent Acquisition (separate from HR operations)
    "Talent_Acquisition": [
        "recruiter", "talent acquisition", "recruiting", "sourcer",
        "talent partner", "recruitment", "hiring manager",
        "technical recruiter", "executive recruiter", "headhunter",
        "recruiting coordinator", "talent scout"
    ],
    
    # HR Operations & People
    "HR": [
        "hr manager", "hr director", "hr generalist", "hr specialist",
        "human resources", "people operations", "people ops", "hrbp",
        "compensation", "benefits", "payroll", "employee relations",
        "hris", "workforce", "hr coordinator", "chro"
    ],
    
    # Learning & Development
    "Learning_Development": [
        "learning officer", "learning and development", "l&d",
        "training manager", "trainer", "instructional designer",
        "curriculum developer", "learning designer", "corporate trainer",
        "training specialist", "enablement", "onboarding"
    ],
    
    # ===========================================
    # FINANCE & LEGAL
    # ===========================================
    
    # Finance & Accounting
    "Finance": [
        "finance manager", "financial analyst", "accountant", "accounting",
        "controller", "cfo", "treasurer", "treasury",
        "audit", "auditor", "tax", "bookkeeper", "payroll",
        "investment", "portfolio manager", "credit analyst", "fp&a"
    ],
    
    # Legal
    "Legal": [
        "lawyer", "attorney", "legal counsel", "paralegal", "law clerk",
        "compliance", "regulatory", "contracts", "legal assistant",
        "litigation", "corporate counsel", "in-house counsel",
        "legal secretary", "legal ops"
    ],
    
    # ===========================================
    # SPECIALIZED INDUSTRIES
    # ===========================================
    
    # Healthcare & Medical
    "Healthcare": [
        "doctor", "physician", "nurse", "registered nurse", "rn",
        "medical", "healthcare", "clinical", "therapist",
        "dentist", "pharmacist", "surgeon", "veterinarian",
        "pharmacy technician", "resident", "fellow", "attending",
        "physician assistant", "pa-c", "nurse practitioner", "np",
        "physical therapist", "occupational therapist", "radiologist",
        "medical assistant", "emt", "paramedic"
    ],
    
    # Education & Academia
    "Education": [
        "teacher", "professor", "instructor", "educator", "tutor",
        "teaching", "academic", "faculty", "lecturer", "coach",
        "curriculum", "endowed chair", "department head", "dean", "provost",
        "assistant professor", "associate professor", "adjunct",
        "teaching assistant", "principal", "superintendent"
    ],
    
    # Research & Science
    "Research": [
        "researcher", "scientist", "research associate", "research assistant",
        "postdoc", "postdoctoral", "phd", "doctoral",
        "lab technician", "laboratory", "biologist", "chemist",
        "physicist", "geologist", "research director"
    ],
    
    # Engineering (non-software)
    "Engineering": [
        "mechanical engineer", "electrical engineer", "civil engineer",
        "chemical engineer", "industrial engineer", "structural engineer",
        "aerospace engineer", "automotive engineer", "manufacturing engineer",
        "process engineer", "quality engineer", "project engineer"
    ],
    
    # Architecture & Construction
    "Architecture": [
        "architect", "architecture", "urban planner", "interior designer",
        "construction manager", "site manager", "quantity surveyor",
        "landscape architect", "architectural designer", "builder"
    ],
    
    # Hospitality & Culinary
    "Hospitality": [
        "chef", "sous chef", "head chef", "executive chef", "pastry chef",
        "bartender", "barista", "sommelier", "server", "waiter", "waitress",
        "hostess", "maître d", "restaurant manager", "food service",
        "baker", "cook", "line cook", "hotel manager", "concierge",
        "front desk", "housekeeping", "mixologist", "catering"
    ],
    
    # Fashion & Apparel
    "Fashion": [
        "fashion designer", "fashion stylist", "wardrobe stylist",
        "costume designer", "apparel designer", "textile designer",
        "pattern maker", "seamstress", "tailor", "fashion buyer",
        "accessories designer", "footwear designer", "fashion editor"
    ],
    
    # Operations & Logistics
    "Operations": [
        "operations", "logistics", "supply chain", "warehouse manager",
        "inventory", "procurement", "purchasing", "fleet manager",
        "distribution", "fulfillment", "shipping"
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
