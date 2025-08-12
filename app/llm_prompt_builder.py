import json

# Helper prompt builders 
def build_prompt_step1(context, user_message, from_scratch):
    # same logic we discussed earlier; keep short; ask for JSON output
    if from_scratch:
        skill_part = "User is a complete beginner. Provide foundational topics to start from zero."
    else:
        skill_part = f"Known: {', '.join(context.get('known_skills',[]))}\nTo learn: {', '.join(context.get('learn_skills',[]))}"
    prompt = f"""
    You are a career analyst. Target role: {context.get('target_role')}
    {skill_part}
    Return ONLY JSON with keys: missing_skills (list), recommendations (list), reason (short).
    """
    return prompt

def build_prompt_step2(analysis, from_scratch):
    # Ask for concise roadmap stages (JSON)
    if from_scratch:
        mode = "Beginner: start from basic fundamentals."
    else:
        mode = "Targeted gap-filling roadmap."
    prompt = f"""
    You are a career coach. Based on analysis: {json.dumps(analysis)}.
    {mode}
    Produce JSON array 'roadmap' of 3-5 stages. Each stage: title, weeks, outcomes, project.
    """
    return prompt

def build_prompt_step3(roadmap):
    prompt = f"""
    You are a friendly coach. Turn this roadmap JSON into a short motivating message (<=200 words).
    End with 2 follow-up questions.
    Roadmap: {json.dumps(roadmap)}
    """
    return prompt
