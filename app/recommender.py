"""
Career Path Recommender System

This module implements the core recommendation engine for ElevatrAI, providing career path
analysis and personalized learning recommendations. It uses ML techniques like cosine
similarity to match user skills with potential career paths and generates customized
learning roadmaps.

Key Components:
- Skill Vector Generation: Converts user skills into numerical vectors
- Role Matching: Uses cosine similarity to find matching career paths
- Learning Path Generation: Creates phased learning plans
- Resource Recommendations: Maps skills to learning resources

Technical Implementation:
- Skills are represented as binary vectors in a global skill space
- Cosine similarity is used for skill-role matching
- Learning paths are generated using a phase-based approach

Author: Anslem Akadu
"""

import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity

def _load_json_file(filepath: str) -> Dict:
    """
    Safely load and parse JSON data from a file with error handling.
    
    Args:
        filepath: Absolute path to the JSON file
        
    Returns:
        Dict containing the parsed JSON data, or empty dict on error
        
    Note:
        This is a helper function used to load various JSON configuration files
        that define our skills matrix, roles, and learning resources.
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return {}

def _load_roles() -> Dict:
    """Load role definitions from roles.json"""
    try:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        roles_path = os.path.join(base, "resources", "roles.json")
        with open(roles_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading roles: {str(e)}")
        return {}

def _load_learning_resources() -> Dict:
    """Load learning resources from learning_resources.json"""
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return _load_json_file(os.path.join(base, "resources", "learning_resources.json"))

def _load_skills_space() -> List[str]:
    """Load the global skill space from skills_matrix.json"""
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return _load_json_file(os.path.join(base, "resources", "skills_matrix.json"))


# Load data at module level
roles_data = _load_roles()
learning_resources = _load_learning_resources()
skill_space = _load_skills_space()

def load_learning_resources(skill: str) -> List[Dict]:
    """
    Get learning resources for a given skill.
    Returns list of resources sorted by level (Beginner first).
    """
    resources = learning_resources.get(skill.lower(), [])
    if not resources:
        return [{"name": "Resource not available yet", "type": "N/A", "url": "#", "level": "N/A"}]
    
    # Sort by level priority: Beginner -> Intermediate -> Advanced
    level_priority = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
    return sorted(resources, key=lambda x: level_priority.get(x.get("level", ""), 999))[:2]

# ML Core: Skill Vector Generation
def skills_to_vector(user_skills: List[str], skill_space: List[str]) -> np.ndarray:
    """
    Convert a list of user skills into a binary vector in the global skill space.
    
    This is a core ML function that transforms text-based skills into a numerical
    vector that can be used for similarity calculations. Each position in the vector
    corresponds to a skill in our global skill space, with 1 indicating the user
    has the skill and 0 indicating they don't.
    
    Args:
        user_skills: List of skills the user has indicated they possess
        skill_space: The global list of all possible skills in our system
        
    Returns:
        numpy.ndarray: Binary vector representation of user's skills
        
    Example:
        >>> skills = ['python', 'javascript']
        >>> space = ['python', 'java', 'javascript', 'c++']
        >>> skills_to_vector(skills, space)
        array([1, 0, 1, 0])
    """
    return np.array([1 if skill in user_skills else 0 for skill in skill_space])

# ML Core: Role Recommendation Engine
def recommend_roles(user_skills: List[str], top_k: int = 3) -> Dict:
    """
    Recommend the top-K most suitable career paths based on user's current skills.
    
    This function implements the core recommendation logic:
    1. Convert user skills to a vector
    2. Compare against each potential role using cosine similarity
    3. Calculate skill gaps and completion percentages
    4. Rank and return the best matches with learning resources
    
    Args:
        user_skills: List of the user's current skills
        top_k: Number of top roles to recommend (default: 3)
        
    Returns:
        Dict containing:
        - recommendations: List of top-K roles with:
            * role_slug: Unique identifier for the role
            * career: Human-readable role title
            * score: Cosine similarity score
            * matched_skills: Skills the user already has
            * missing_skills: Skills they need to learn
            * resources: Learning resources for missing skills
            * completion_percentage: Progress towards role requirements
            * analysis: Human-readable analysis of the match
        - user_skills_count: Total number of user's skills
        - analysis_summary: Overall summary of recommendations
        
    Example:
        >>> skills = ['python', 'pandas', 'sql']
        >>> result = recommend_roles(skills, top_k=2)
        >>> print(result['analysis_summary'])
        'Found 2 recommended roles based on your 3 skills'
    """
    user_vec = skills_to_vector(user_skills, skill_space)
    recommendations = []

    for role_slug, role_data in roles_data.items():
        role_vec = skills_to_vector(role_data["skills"], skill_space)
        
        similarity = cosine_similarity([user_vec], [role_vec])[0][0]

        # Find matched and missing skills
        matched = [s for s in user_skills if s in role_data["skills"]]
        missing = [s for s in role_data["skills"] if s not in user_skills]
        
        # Get learning resources for missing skills
        skill_resources = {
            skill: load_learning_resources(skill)
            for skill in missing
        }

        # Calculate completion percentage
        total_skills = len(role_data["skills"])
        completion = (len(matched) / total_skills * 100) if total_skills > 0 else 0

        recommendations.append({
            "role_slug": role_slug,
            "career": role_data["career"],
            "score": round(float(similarity), 3),
            "matched_skills": matched,
            "missing_skills": missing,
            "resources": skill_resources,
            "completion_percentage": round(completion, 1),
            "analysis": f"Matched {len(matched)} of {total_skills} required skills"
        })

    # Sort by completion percentage and similarity score
    top_recommendations = sorted(
        recommendations,
        key=lambda x: (x["completion_percentage"], x["score"]),
        reverse=True
    )[:top_k]

    return {
        "recommendations": top_recommendations,
        "user_skills_count": len(user_skills),
        "analysis_summary": f"Found {len(top_recommendations)} recommended roles based on your {len(user_skills)} skills"
    }

# Get role by slug
def get_role_by_slug(role_slug: str) -> Optional[Dict]:
    """Get role info by slug"""
    return roles_data.get(role_slug)

# Career Transition Analysis Engine
def analyze_career_transition(
    user_skills: List[str], 
    current_role_slug: str, 
    target_role_slug: str, 
    transition_type: str
) -> Dict[str, Any]:
    """
    Analyze a career transition path and generate a personalized learning roadmap.
    
    This is the main analysis engine that:
    1. Evaluates the user's current skill set
    2. Compares it against target role requirements
    3. Identifies skill gaps and learning needs
    4. Generates a phased learning plan
    5. Recommends specific learning resources
    
    The function handles three main transition types:
    - 'beginner': Complete beginners starting from scratch
    - 'upskill': Enhancing skills within current role
    - 'transition': Moving to a different role
    
    Args:
        user_skills: List of the user's current skills
        current_role_slug: Identifier for user's current role (or 'none')
        target_role_slug: Identifier for desired career role
        transition_type: Type of career transition
        
    Returns:
        Dict containing:
        - transition_type: Type of transition being analyzed
        - target_role: Details about the target role
        - matched_skills: Skills the user already has
        - missing_skills: Skills they need to acquire
        - completion_percentage: Progress towards target role
        - learning_resources: Curated learning materials
        - phases: Structured learning roadmap with:
            * Foundation skills
            * Core development
            * Advanced topics
            
    Raises:
        ValueError: If target role is not found in our database
        
    Example:
        >>> result = analyze_career_transition(
        ...     user_skills=['python', 'sql'],
        ...     current_role_slug='data_analyst',
        ...     target_role_slug='data_scientist',
        ...     transition_type='upskill'
        ... )
        >>> print(f"Completion: {result['completion_percentage']}%")
    """
    
    # Load roles data
    roles_data = _load_roles()
    
    # Get target role data and validate
    target_role_data = roles_data.get(target_role_slug)
    if not target_role_data:
        raise ValueError(f"Invalid target role: {target_role_slug}")

    # Structure target role data consistently
    target_role = {
        "slug": target_role_slug,
        "career": target_role_data.get('title', target_role_slug),
        "skills": target_role_data.get('skills', [])
    }

    # Initialize analysis result with proper structure
    analysis_result = {
        "transition_type": transition_type,
        "target_role": target_role,  # Now properly structured
        "matched_skills": [],
        "missing_skills": [],
        "completion_percentage": 0,
        "learning_resources": {},
        "phases": []
    }

    # Handle different transition types
    if transition_type == 'beginner':
        analysis_result["missing_skills"] = target_role["skills"]
    else:
        required_skills = target_role["skills"]
        analysis_result["matched_skills"] = [s for s in user_skills if s in required_skills]
        analysis_result["missing_skills"] = [s for s in required_skills if s not in user_skills]
        if required_skills:
            analysis_result["completion_percentage"] = int(len(analysis_result["matched_skills"]) / len(required_skills) * 100)

    # Generate learning resources and phases
    skills_to_process = analysis_result["missing_skills"]
    
    # Generate learning resources
    for skill in skills_to_process:
        analysis_result["learning_resources"][skill] = load_learning_resources(skill)

    # Create phases
    skills_per_phase = max(1, len(skills_to_process) // 3)
    phases = []

    if skills_to_process[:skills_per_phase]:
        phases.append({
            "name": "Foundation Skills",
            "description": "Essential skills to build your base knowledge",
            "skills": [(skill, analysis_result["learning_resources"][skill]) 
                      for skill in skills_to_process[:skills_per_phase]]
        })
    
    if skills_to_process[skills_per_phase:skills_per_phase*2]:
        phases.append({
            "name": "Core Development",
            "description": "Build your technical expertise",
            "skills": [(skill, analysis_result["learning_resources"][skill]) 
                      for skill in skills_to_process[skills_per_phase:skills_per_phase*2]]
        })
    
    if skills_to_process[skills_per_phase*2:]:
        phases.append({
            "name": "Advanced Topics",
            "description": "Master advanced concepts",
            "skills": [(skill, analysis_result["learning_resources"][skill]) 
                      for skill in skills_to_process[skills_per_phase*2:]]
        })

    analysis_result["phases"] = phases
    return analysis_result
    
# genrate recommendations
def generate_recommendations(analysis_result: Dict[str, Any]) -> List[Dict]:
    """
    Generate phased learning recommendations for any career path.
    
    Args:
        analysis_result: Dictionary containing analysis results including skills
        
    Returns:
        List of phases, each containing skills and their learning resources
    """
    # Get skills to process based on transition type
    if analysis_result.get('transition_type') == 'recommend':
        skills_to_process = analysis_result.get('missing_skills', [])
    elif analysis_result.get('transition_type') == 'beginner':
        skills_to_process = analysis_result.get('target_role', {}).get('skills', [])
    else:
        skills_to_process = analysis_result.get('missing_skills', [])

    # Define phases based on skill categorization
    foundation_skills = []
    intermediate_skills = []
    advanced_skills = []

    # Distribute skills across phases
    for i, skill in enumerate(skills_to_process):
        resources = load_learning_resources(skill)
        skill_with_resources = (skill, resources)
        
        if i < 3:  # First 3 skills go to foundation
            foundation_skills.append(skill_with_resources)
        elif i < 6:  # Next 3 to intermediate
            intermediate_skills.append(skill_with_resources)
        else:  # Remaining to advanced
            advanced_skills.append(skill_with_resources)

    # Create phases structure
    phases = []
    
    if foundation_skills:
        phases.append({
            "name": "Foundation Skills",
            "description": "Essential skills to build your base knowledge",
            "skills": foundation_skills
        })
    
    if intermediate_skills:
        phases.append({
            "name": "Core Development",
            "description": "Build on your foundation with these key skills",
            "skills": intermediate_skills
        })
    
    if advanced_skills:
        phases.append({
            "name": "Advanced Mastery",
            "description": "Specialized skills to distinguish yourself",
            "skills": advanced_skills
        })

    return phases

def get_required_skills(role_name):
    """Get the required skills for a specific role."""
    try:
        roles = _load_roles()
        role_data = roles.get(role_name, {})
        return role_data.get("skills", [])
    except Exception as e:
        print(f"Error getting required skills: {e}")
        return []



