"""
Natural Language Skills Parser

This module handles the extraction and normalization of skills from various input sources
including resumes, manual entries, and text descriptions. It uses pattern matching and
a predefined skills matrix to accurately identify technical skills in unstructured text.

Key Features:
- Multi-format skill extraction (resume text, manual input)
- Pattern-based skill recognition
- Skill normalization and validation
- Role-based skill validation

Technical Implementation:
- Uses regex patterns for skill matching
- Two-pass approach for better accuracy:
  1. Direct phrase matching for multi-word skills
  2. Pattern matching with word boundaries
- Validates against known skills matrix

Author: Anslem Akadu
"""

import json
import os
import re
from typing import Dict, List, Set, Optional

# File paths for skill and role definitions
# These files form our knowledge base for skill extraction
RESOURCES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
SKILLS_MATRIX_PATH = os.path.join(RESOURCES_DIR, 'skills_matrix.json')
ROLES_PATH = os.path.join(RESOURCES_DIR, 'roles.json')

# TODO: Add support for fuzzy matching to handle typos and variations
# TODO: Implement skill versioning (e.g., Python 2 vs Python 3)
# TODO: Add support for skill synonyms (e.g., "ML" = "Machine Learning")

# NLP Helper: Build regex patterns for skill detection
def _build_skill_patterns() -> Dict[str, str]:
    """
    Build optimized regex patterns for skill detection from our skills matrix.
    
    This function creates a dictionary of regex patterns used for skill extraction:
    1. Loads the skills matrix JSON
    2. Groups skills by category
    3. Creates optimized regex patterns for each category
    4. Handles special characters and word boundaries
    
    The patterns are used in our two-pass skill extraction system to accurately
    identify technical skills in unstructured text like resumes.
    
    Returns:
        Dict mapping skill categories to their regex patterns:
        {
            'machine_learning': 'tensorflow|pytorch|scikit-learn',
            'programming': 'python|java|javascript',
            ...
        }
        
    Note:
        We escape special characters in skill names to prevent regex errors
        and ensure exact matching when needed.
    """
    try:
        # Load our skills knowledge base
        with open(SKILLS_MATRIX_PATH, 'r') as f:
            skills_data = json.load(f)
        
        # Build optimized patterns for each category
        patterns = {}
        for category, skills in skills_data.items():
            # Create regex pattern with escaped special chars
            pattern = '|'.join(re.escape(skill.lower()) for skill in skills)
            patterns[category.lower()] = pattern
        return patterns
    except Exception as e:
        print(f"Error building skill patterns: {e}")
        return {}

# Initialize patterns from skills matrix
SKILL_PATTERNS = _build_skill_patterns()

def clean_manual_input(text: str) -> List[str]:
    """
    Clean and normalize manually entered skills.
    
    Args:
        text (str): Comma-separated list of skills
        
    Returns:
        List[str]: List of cleaned, normalized skills
    """
    if not text:
        return []
    skills = [skill.strip().lower() for skill in text.split(',')]
    return list(set(skill for skill in skills if skill))

def extract_skills_from_text(text: str) -> Set[str]:
    """
    Extract technical skills from unstructured text using NLP techniques.
    
    This function implements a sophisticated two-pass skill extraction system:
    
    Pass 1 - Exact Phrase Matching:
    - Looks for multi-word skills (e.g., "machine learning", "data science")
    - Uses word boundaries to ensure accurate matches
    - Prevents partial matches within larger words
    
    Pass 2 - Pattern-Based Detection:
    - Uses pre-built regex patterns grouped by skill category
    - Handles variations in formatting and spacing
    - Validates matches against our skills database
    
    Args:
        text: Unstructured text to analyze (e.g., resume content)
        
    Returns:
        Set of unique, normalized skill names found in the text
        
    Example:
        >>> text = "Experienced Python developer with React and AWS"
        >>> skills = extract_skills_from_text(text)
        >>> print(skills)
        {'python', 'react', 'aws'}
        
    Note:
        The function is case-insensitive and handles common formatting variations.
        Skills must exist in our skills matrix to be recognized.
    """
    if not text:
        return set()
        
    # Add word boundaries for accurate matching
    text_lower = ' ' + text.lower() + ' '
    all_skills = load_skills_for_parser()
    found_skills = set()
    
    # Pass 1: Multi-word Skill Detection
    # This pass focuses on complex skill phrases that might be missed by regex
    for skill in all_skills:
        if ' ' in skill:  # Multi-word skills need exact matching
            if f' {skill} ' in text_lower:
                found_skills.add(skill)
                
    # Pass 2: Pattern-Based Skill Detection
    # Uses our pre-built category-based patterns for single-word skills
    for category, pattern in SKILL_PATTERNS.items():
        if pattern:  # Skip empty patterns
            try:
                # Use word boundaries (\b) to prevent partial matches
                matches = re.finditer(r'\b(' + pattern + r')\b', text_lower)
                for match in matches:
                    skill = match.group(1).strip()
                    if skill in all_skills:  # Validate against known skills
                        found_skills.add(skill)
            except re.error:
                print(f"Invalid regex pattern for category {category}")
                continue
    
    return found_skills

def load_skills_for_parser() -> Set[str]:
    """Load and return all valid skills."""
    try:
        with open(SKILLS_MATRIX_PATH, 'r') as f:
            skills_data = json.load(f)
        all_skills = set()
        for role_skills in skills_data.values():
            for skill in role_skills:
                all_skills.add(skill.lower())
        return all_skills
    except Exception as e:
        print(f"Error loading skills: {e}")
        return {'python', 'javascript', 'sql', 'aws', 'docker'}

def load_roles_data() -> Dict[str, Dict]:
    """Load role definitions from roles.json."""
    try:
        with open(ROLES_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading roles: {e}")
        return {}

def parse_user_input(
    target_role: str,
    current_role: Optional[str] = None,
    skills: Optional[str] = None,
    resume_text: Optional[str] = None,
    transition_type: str = 'upskill'
    ) -> Dict[str, any]:
    """
    Process and validate user input from all sources.
    
    Args:
        target_role (str): Desired career role (must be valid from roles.json)
        current_role (str, optional): Current role (if any)
        skills (str, optional): Comma-separated list of skills 
        resume_text (str, optional): Extracted text from resume
        transition_type (str): Type of transition ('upskill', 'transition', 'beginner', 'role_recommendation')
        
    Returns:
        Dict containing:
        {
            'target_role': str - Validated target role
            'current_role': str - Current role or 'entry_level'  
            'skills': List[str] - Normalized list of skills
            'transition_type': str - Validated transition type
        }
        
    Raises:
        ValueError: If target role is invalid or no skills could be extracted
    """
    
    roles_data = load_roles_data()
    
    if transition_type == 'recommend':
        if not skills and not resume_text:
            raise ValueError("Please provide skills for role recommendations")
    else:
        # Only validate target role for non-recommendation paths
        if not roles_data or target_role not in roles_data:
            raise ValueError(f"Invalid target role: {target_role}")
    
    extracted_skills = set()
    
    if skills:
        extracted_skills.update(clean_manual_input(skills))
    
    if resume_text:
        extracted_skills.update(extract_skills_from_text(resume_text))
        
    if not extracted_skills and transition_type != 'beginner':
        raise ValueError("No valid skills could be extracted from input")
    
    current_role = current_role if current_role in roles_data else 'entry_level'
    
    return {
        'target_role': target_role,
        'current_role': current_role,
        'skills': sorted(list(extracted_skills)),
        'transition_type': transition_type
    }
