import os
import re
import json
import torch
from sentence_transformers import SentenceTransformer, util

def load_skills():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    skills_path = os.path.join(base_path, 'resources', 'skills.json')
    with open(skills_path, 'r') as f:
        skills_data = json.load(f)
    return list({skill.lower() for role in skills_data.values() for skill in role["core_skills"]})

ALL_KNOWN_SKILLS = load_skills()

def clean_text(text):
    """
    Lowercase and remove special characters from text.
    """
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

def extract_words(text):
    """
    Split cleaned text into words.
    """
    return clean_text(text).split()
#using ebedding for fuzzy matching

# Load once
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute all skill embeddings
skill_embeddings = embedder.encode(ALL_KNOWN_SKILLS, convert_to_tensor=True)

def embed_fuzzy_match(input_skill, threshold=0.7):
    """
    Use sentence embeddings to match user-entered skill to known skill space.
    """
    input_embedding = embedder.encode(input_skill, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(input_embedding, skill_embeddings)[0]

    best_score, best_idx = torch.max(cosine_scores, dim=0)
    if best_score >= threshold:
        return ALL_KNOWN_SKILLS[best_idx]
    return None

def extract_skills_from_text(text):
    """
    Extract valid skills from any raw input text using fuzzy matching.
    Used for resume uploads.
    """
    words = extract_words(text)
    matched_skills = set()

    for word in words:
        match = embed_fuzzy_match(word)
        if match:
            matched_skills.add(match)

    return list(matched_skills)

def clean_manual_input(skills_str):
    """
    Takes comma-separated user skills and normalizes them using fuzzy match.
    """
    raw_skills = [skill.strip().lower() for skill in skills_str.split(",")]
    normalized_skills = set()

    for skill in raw_skills:
        match = embed_fuzzy_match(skill)
        if match:
            normalized_skills.add(match)

    return list(normalized_skills)


