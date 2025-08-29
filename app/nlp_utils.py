"""
Natural Language Processing Utilities

This module provides NLP functionality for skill extraction and matching using
state-of-the-art language models. It implements:

1. Skill Detection: Extract technical skills from unstructured text
2. Fuzzy Matching: Match similar skills using embeddings or string similarity
3. Text Normalization: Clean and standardize skill text

Key Components:
- Sentence Transformers for semantic matching
- Cosine similarity for skill comparison
- Fallback mechanisms for reliability

Technical Implementation:
- Uses all-MiniLM-L6-v2 model for embeddings
- Implements graceful degradation to string matching
- Caches embeddings for performance

Author: Anslem Akadu
"""

import os
import re 
import json
from typing import List, Optional
import difflib
from sentence_transformers import SentenceTransformer, util

# Constants for skill matching
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
COSINE_THRESHOLD = 0.70
FALLBACK_THRESHOLD = 0.80

def load_skills() -> List[str]:
    """
    Load and normalize skills from the skills matrix configuration file.
    
    Returns:
        List[str]: Sorted list of unique, normalized skill names
        
    Technical Details:
        - Skills are loaded from skills_matrix.json
        - All skills are converted to lowercase for consistency
        - Duplicates are removed using set operations
        
    Example:
        >>> skills = load_skills()
        >>> print(skills[:3])
        ['aws', 'azure', 'bash']
    """
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        skills_path = os.path.join(base_path, 'resources', 'skills_matrix.json')
        if not os.path.exists(skills_path):
            raise FileNotFoundError(f"skills_matrix.json not found at {skills_path}")
        with open(skills_path, 'r') as f:
            skills_data = json.load(f)
        return sorted({skill.lower() for skills in skills_data.values() for skill in skills})
    except Exception as e:
        print(f"Error loading skills: {e}")
        return []

# Initialize global skill list
ALL_KNOWN_SKILLS = load_skills()

def clean_text(text: str) -> str:
    """
    Normalize text by removing special characters and converting to lowercase.
    
    Args:
        text: Raw input text
        
    Returns:
        str: Cleaned and normalized text
    """
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

def extract_words(text: str) -> List[str]:
    """
    Split text into individual words after cleaning.
    
    Args:
        text: Raw input text
        
    Returns:
        List[str]: List of cleaned, individual words
    """
    return clean_text(text).split()

# ML Model Management
_embedder = None
_skill_embeddings = None

def _ensure_embedder() -> bool:
    """
    Initialize the sentence transformer model and cache embeddings.
    
    This function implements a lazy loading pattern for the ML model to:
    1. Reduce startup time
    2. Handle cases where the model isn't available
    3. Cache embeddings for better performance
    
    Returns:
        bool: True if model loaded successfully, False for fallback mode
    """
    global _embedder, _skill_embeddings
    if _embedder is not None:
        return True
    try:
        # Load the ML model for semantic matching
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
        # Pre-compute embeddings for all known skills
        _skill_embeddings = _embedder.encode(ALL_KNOWN_SKILLS, convert_to_tensor=True)
        _embedder._util = __import__("sentence_transformers.util", fromlist=["util"])
        return True
    except Exception as e:
        print(f"[nlp_utils] Embedding model unavailable, falling back to fuzzy string match: {e}")
        _embedder = None
        _skill_embeddings = None
        return False

def embed_fuzzy_match(input_skill: str, threshold: float = COSINE_THRESHOLD) -> Optional[str]:
    """
    Match input text to known skills using ML embeddings or fuzzy string matching.
    
    This function uses two approaches:
    1. Primary: Semantic matching using sentence transformers
    2. Fallback: String similarity using difflib
    
    Args:
        input_skill: Text to match against known skills
        threshold: Minimum similarity score (0-1) for a match
        
    Returns:
        Optional[str]: Matched skill name or None if no match found
        
    Example:
        >>> embed_fuzzy_match("python programming")
        'python'
        >>> embed_fuzzy_match("reactjs")
        'react'
    """
    s = input_skill.strip().lower()
    if not s:
        return None
        
    # Try ML-based matching first
    if _ensure_embedder():
        util = _embedder._util
        input_emb = _embedder.encode(s, convert_to_tensor=True)
        # Use cosine similarity to find best match
        cosine_scores = util.pytorch_cos_sim(input_emb, _skill_embeddings)[0]
        import torch
        best_score, best_idx = torch.max(cosine_scores, dim=0)
        if float(best_score) >= threshold:
            return ALL_KNOWN_SKILLS[int(best_idx)]
        return None
        
    # Fallback to string similarity if ML model unavailable
    candidates = difflib.get_close_matches(s, ALL_KNOWN_SKILLS, n=1, cutoff=FALLBACK_THRESHOLD)
    return candidates[0] if candidates else None

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract all skills mentioned in a block of text.
    
    Args:
        text: Block of text to analyze (e.g., resume content)
        
    Returns:
        List[str]: Sorted list of unique skills found
        
    Example:
        >>> text = "Expert in Python and JavaScript, learning React"
        >>> extract_skills_from_text(text)
        ['javascript', 'python', 'react']
    """
    matched = set()
    for w in extract_words(text):
        m = embed_fuzzy_match(w)
        if m:
            matched.add(m)
    return sorted(list(matched))

def clean_manual_input(skills_str: str) -> List[str]:
    """
    Process comma-separated skill input from users.
    
    Args:
        skills_str: Comma-separated list of skills
        
    Returns:
        List[str]: Sorted list of normalized, validated skills
        
    Example:
        >>> clean_manual_input("Python, javascript, ReactJS")
        ['javascript', 'python', 'react']
    """
    raw = [t.strip().lower() for t in skills_str.split(",") if t.strip()]
    out = set()
    for s in raw:
        m = embed_fuzzy_match(s)
        if m:
            out.add(m)
    return sorted(list(out))

# TODO: Future Improvements
# 1. Add support for skill variations (e.g., "JS" -> "JavaScript")
# 2. Implement skill level detection (e.g., "Expert in Python" -> level:expert)
# 3. Add context-aware skill extraction
# 4. Support multiple languages
# 5. Add skill relationship graph




