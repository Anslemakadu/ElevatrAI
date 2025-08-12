from app.nlp_utils import extract_skills_from_text, clean_manual_input

def parse_manual_input(skills_str: str, role: str = None):
    """
    Handle form-based manual input.
    """
    normalized_skills = clean_manual_input(skills_str)
    return {
        "skills": normalized_skills,
        "input_mode": "manual",
        "role": role
    }

def parse_resume_text(text: str, role: str = None):
    """
    Handle resume-based input.
    """
    extracted_skills = extract_skills_from_text(text)
    return {
        "skills": extracted_skills,
        "input_mode": "resume",
        "role": role
    }
