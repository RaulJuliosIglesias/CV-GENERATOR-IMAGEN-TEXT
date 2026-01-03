"""
Role Database Loader
Loads roles and social link mappings from the external JSON database.
Supports expertise-level filtering for coherent role selection.
"""

import json
import random
from pathlib import Path
from typing import Optional

# Path to the database - resolve from backend root, not app folder
# __file__ = backend/app/services/roles_service.py
# .parent = backend/app/services
# .parent.parent = backend/app
# .parent.parent.parent = backend
# So: backend/data/roles_database.json
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "roles_database.json"

# Cache
_roles_db = None


def load_roles_database() -> dict:
    """Load the roles database from JSON file."""
    global _roles_db
    
    if _roles_db is not None:
        return _roles_db
    
    print(f"DEBUG ROLES: Attempting to load database from: {DATABASE_PATH}")
    print(f"DEBUG ROLES: Path exists: {DATABASE_PATH.exists()}")
    
    if not DATABASE_PATH.exists():
        print(f"ERROR ROLES: Database not found at {DATABASE_PATH}")
        return {"categories": {}}
    
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        _roles_db = json.load(f)
    
    # Count total roles
    total_roles = 0
    for cat in _roles_db.get("categories", {}).values():
        for level_roles in cat.get("roles_by_level", {}).values():
            total_roles += len(level_roles)
    
    print(f"DEBUG ROLES: Loaded database v{_roles_db.get('version', '1.0')} with {len(_roles_db.get('categories', {}))} categories and {total_roles} total roles")
    return _roles_db


def get_all_roles() -> list[str]:
    """Get flat list of all available roles (all levels)."""
    db = load_roles_database()
    all_roles = []
    
    for category_data in db.get("categories", {}).values():
        # Handle new structure with roles_by_level
        roles_by_level = category_data.get("roles_by_level", {})
        if roles_by_level:
            for level_roles in roles_by_level.values():
                all_roles.extend(level_roles)
        # Fallback to old structure
        elif "roles" in category_data:
            all_roles.extend(category_data.get("roles", []))
    
    return all_roles


def get_roles_by_expertise(expertise: str) -> list[str]:
    """
    Get roles filtered by expertise level.
    
    Args:
        expertise: One of 'junior', 'mid', 'senior', 'expert', or 'any'
    
    Returns:
        List of roles appropriate for the given expertise level.
    """
    db = load_roles_database()
    
    # Normalize expertise level
    expertise = expertise.lower().strip()
    
    # Map expertise to allowed levels
    # - junior can only get junior roles
    # - mid can get junior and mid roles
    # - senior can get mid and senior roles
    # - expert can get senior and expert roles
    level_mapping = {
        "junior": ["junior"],
        "mid": ["junior", "mid"],
        "senior": ["mid", "senior"],
        "expert": ["senior", "expert"],
        "any": ["junior", "mid", "senior", "expert"]
    }
    
    allowed_levels = level_mapping.get(expertise, ["mid"])
    
    matching_roles = []
    
    for category_data in db.get("categories", {}).values():
        roles_by_level = category_data.get("roles_by_level", {})
        
        for level in allowed_levels:
            level_roles = roles_by_level.get(level, [])
            matching_roles.extend(level_roles)
    
    # If no roles found, return fallback
    if not matching_roles:
        print(f"WARNING: No roles found for expertise '{expertise}', using fallback")
        return get_all_roles()[:20] if get_all_roles() else ["Software Engineer"]
    
    return matching_roles


def get_random_role(expertise: str = "mid") -> str:
    """Get a random role appropriate for the expertise level."""
    roles = get_roles_by_expertise(expertise)
    if not roles:
        return "Software Engineer"  # Fallback
    return random.choice(roles)


def get_roles_by_category(category_key: str, expertise: str = "any") -> list[str]:
    """Get roles for a specific category, optionally filtered by expertise."""
    db = load_roles_database()
    category = db.get("categories", {}).get(category_key, {})
    
    if expertise == "any":
        # Return all roles from all levels
        all_roles = []
        for level_roles in category.get("roles_by_level", {}).values():
            all_roles.extend(level_roles)
        return all_roles
    
    # Return roles for specific expertise
    return category.get("roles_by_level", {}).get(expertise.lower(), [])


def get_category_for_role(role: str) -> Optional[str]:
    """Find which category a role belongs to."""
    db = load_roles_database()
    role_lower = role.lower()
    
    for category_key, category_data in db.get("categories", {}).items():
        roles_by_level = category_data.get("roles_by_level", {})
        for level_roles in roles_by_level.values():
            for r in level_roles:
                if role_lower == r.lower():
                    return category_key
    
    return None


def get_social_links_for_role(role: str) -> list[str]:
    """Get appropriate social links for a role based on its category."""
    db = load_roles_database()
    role_lower = role.lower()
    
    # Find the category for this role
    for category_data in db.get("categories", {}).values():
        roles_by_level = category_data.get("roles_by_level", {})
        for level_roles in roles_by_level.values():
            for r in level_roles:
                if role_lower == r.lower():
                    return category_data.get("social_links", ["linkedin", "website"])
    
    # Fallback: Try to match keywords in role name
    keyword_mapping = {
        "developer": ["linkedin", "website", "github"],
        "engineer": ["linkedin", "website", "github"],
        "designer": ["linkedin", "website", "dribbble", "behance"],
        "artist": ["linkedin", "website", "artstation", "instagram"],
        "manager": ["linkedin", "website"],
        "director": ["linkedin", "website"],
        "researcher": ["linkedin", "website", "researchgate", "google_scholar"],
    }
    
    for keyword, links in keyword_mapping.items():
        if keyword in role_lower:
            return links
    
    # Default fallback
    return ["linkedin", "website"]


def get_all_categories() -> dict:
    """Get all categories with their metadata."""
    db = load_roles_database()
    return db.get("categories", {})


def get_expertise_level_for_role(role: str) -> Optional[str]:
    """Determine what expertise level a role belongs to."""
    db = load_roles_database()
    role_lower = role.lower()
    
    for category_data in db.get("categories", {}).values():
        roles_by_level = category_data.get("roles_by_level", {})
        for level, level_roles in roles_by_level.items():
            for r in level_roles:
                if role_lower == r.lower():
                    return level
    
    return None


# =====================================================
# CONFIG GETTERS - Single source of truth for UI
# =====================================================

def get_genders() -> list[dict]:
    """Get gender options from database."""
    db = load_roles_database()
    return db.get("genders", [
        {"value": "any", "label": "Any Gender"},
        {"value": "male", "label": "Male"},
        {"value": "female", "label": "Female"}
    ])


def get_ethnicities() -> list[dict]:
    """Get ethnicity options from database."""
    db = load_roles_database()
    return db.get("ethnicities", [
        {"value": "any", "label": "Any Ethnicity"}
    ])


def get_origins() -> list[dict]:
    """Get origin/location options from database."""
    db = load_roles_database()
    return db.get("origins", [
        {"value": "any", "label": "Any Location"}
    ])


def get_expertise_levels() -> list[dict]:
    """Get expertise level options from database."""
    db = load_roles_database()
    return db.get("expertise_levels", [
        {"value": "any", "label": "Any Level"},
        {"value": "junior", "label": "Junior"},
        {"value": "mid", "label": "Mid-Level"},
        {"value": "senior", "label": "Senior"},
        {"value": "expert", "label": "Expert"}
    ])


def get_all_config() -> dict:
    """Get complete config for frontend - single API call."""
    return {
        "roles": get_all_roles(),
        "genders": get_genders(),
        "ethnicities": get_ethnicities(),
        "origins": get_origins(),
        "expertise_levels": get_expertise_levels()
    }


def get_gender_values() -> list[str]:
    """Get just the gender values for backend use."""
    return [g["value"] for g in get_genders() if g["value"] != "any"]


def get_ethnicity_values() -> list[str]:
    """Get just the ethnicity values for backend use."""
    return [e["value"] for e in get_ethnicities() if e["value"] != "any"]


def get_origin_values() -> list[str]:
    """Get just the origin values for backend use."""
    return [o["value"] for o in get_origins() if o["value"] != "any"]
