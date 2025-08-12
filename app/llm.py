from app.llm_prompt_builder import build_prompt_step1, build_prompt_step2, build_prompt_step3
from app.recommender import get_skill_gap
import json
import requests

LLM_SERVER_URL = "https://anslem19-elevatrai2-0.hf.space/chat"

def query_llm(context: dict, message: str, temperature: float = 0.7) -> str:
    payload = {
        "user_message": message,
        "context": context,
        "temperature": temperature,
        "max_tokens": 200
    }
    
    try:
        print("\n--- Sending to LLM ---")
        print(payload)
        
        response = requests.post(
            LLM_SERVER_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        print(f"HTTP Status: {response.status_code}")
        print("Raw Response Text:", response.text)

        if response.status_code != 200:
            return ""  # Return empty so caller knows it failed

        try:
            result = response.json()
        except json.JSONDecodeError:
            print("Could not decode JSON from LLM response.")
            return ""

        print("Parsed JSON from LLM:", result)

        if "output" in result:
            return result["output"]
        elif "choices" in result and result["choices"]:
            return result["choices"][0].get("text", "")
        elif isinstance(result, str):
            return result
        else:
            return json.dumps(result)

    except requests.RequestException as e:
        print(f"LLM Request failed: {str(e)}")
        return ""

def generate_learning_plan(user_skills: list, role_name: str, from_scratch=False) -> str:
    # Step 0: Skill gap analysis
    result = get_skill_gap(user_skills, role_name)
    if "error" in result:
        return result["error"]

    context = {
        "target_role": result["career"],
        "known_skills": result["matched_skills"],
        "learn_skills": result["missing_skills"],
        "full_skillset": result["skills"],
        "resources": result["resources"]
    }

    # Step 1: Missing skills + recommendations
    prompt1 = build_prompt_step1(context, "", from_scratch)
    analysis_raw = query_llm(context, prompt1)
    try:
        analysis = json.loads(analysis_raw)
    except json.JSONDecodeError:
        return f"Error parsing Step 1 output: {analysis_raw}"

    # Step 2: Roadmap creation
    prompt2 = build_prompt_step2(analysis, from_scratch)
    roadmap_raw = query_llm(context, prompt2)
    try:
        roadmap = json.loads(roadmap_raw)
    except json.JSONDecodeError:
        return f"Error parsing Step 2 output: {roadmap_raw}"

    # Step 3: Friendly message
    prompt3 = build_prompt_step3(roadmap)
    friendly_message = query_llm(context, prompt3)

    return {
        "analysis": analysis,
        "roadmap": roadmap,
        "message": friendly_message
    }

