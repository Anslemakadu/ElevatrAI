from flask import Blueprint, render_template, request, jsonify
from app.nlp_utils import extract_skills_from_text, clean_manual_input
from app.llm import query_llm
from app.recommender import recommend_roles, get_skill_gap
from PyPDF2 import PdfReader
import json
import logging
import os

logger = logging.getLogger(__name__)

# Import local modules
from app.llm import generate_learning_plan, query_llm
from app.recommender import recommend_roles, get_skill_gap
from app.parser import parse_manual_input, parse_resume_text
from app.llm_prompt_builder import build_prompt_step1, build_prompt_step2, build_prompt_step3


main_routes = Blueprint("main", __name__)

@main_routes.route('/', methods=['GET'])
def home():
    return render_template("home.html")

@main_routes.route('/skill-gap', methods=['POST'])
def skill_gap():
    try:
        skills = []
        career = None
        from_scratch = False

        content_type = request.content_type or ""

        # CASE 1: PDF Resume Upload (multipart/form-data)
        if content_type.startswith('multipart/form-data'):
            logger.debug("Processing multipart/form-data request")

            # Validate file exists
            if 'resume' not in request.files:
                return jsonify({"error": "No resume file uploaded"}), 400

            pdf_file = request.files['resume']
            if pdf_file.filename == '':
                return jsonify({"error": "Empty filename for uploaded resume"}), 400

            # Read PDF
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            logger.debug(f"Extracted text length from PDF: {len(text)} characters")

            # Extract skills
            skills = extract_skills_from_text(text)

            # Get career path from form data
            career = request.form.get('career_path', '').strip()
            from_scratch = request.form.get('from_scratch', 'false').lower() == 'true'

        # CASE 2: JSON input (manual or text mode)
        elif content_type.startswith('application/json'):
            try:
                data = request.get_json()
            except Exception as e:
                logger.error(f"JSON parsing failed: {e}")
                return jsonify({"error": "Invalid JSON format", "details": str(e)}), 400

            if not data or not data.get('career_path'):
                return jsonify({"error": "career_path is required"}), 400

            skills_raw = data.get('skills', '')
            career = data.get('career_path')
            input_mode = data.get('input_mode', 'manual')
            from_scratch = data.get('from_scratch', False)

            if from_scratch:
                skills = []
            else:
                skills = clean_manual_input(skills_raw) if input_mode == 'manual' else extract_skills_from_text(skills_raw)

        else:
            return jsonify({"error": "Unsupported Content-Type"}), 400

        # === KEEP EXISTING LLM + gap analysis code ===
        if not from_scratch and not skills:
            return jsonify({"error": "No valid skills detected"}), 400

        gap_analysis = get_skill_gap(skills, career)
        if not gap_analysis or "error" in gap_analysis:
            return jsonify({"error": "Failed to generate skill gap analysis"}), 400

        context = {
            "target_role": gap_analysis["career"],
            "known_skills": gap_analysis["matched_skills"],
            "learn_skills": gap_analysis["missing_skills"],
            "full_skillset": gap_analysis["skills"],
            "resources": gap_analysis["resources"],
            "backend_summary": None
        }

        prompt = build_prompt_step1(context, "", len(context["known_skills"]) == 0)
        llm_response = query_llm(context, prompt)

        try:
            analysis = json.loads(llm_response) if isinstance(llm_response, str) else llm_response
        except json.JSONDecodeError:
            analysis = {
                "missing_skills": context["learn_skills"],
                "learning_path": [{"skill": skill, "estimated_weeks": 4, "prerequisites": []} for skill in context["learn_skills"]],
                "recommendations": ["Focus on fundamentals first"]
            }

        return jsonify({
            "gap_analysis": gap_analysis,
            "llm_analysis": analysis,
            "next_steps": {
                "immediate_focus": context["learn_skills"][:2],
                "resources": dict(list(context["resources"].items())[:3])
            }
        })

    except Exception as e:
        logger.error(f"Error in skill-gap route: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to process skill gap analysis", "details": str(e)}), 500

@main_routes.route('/starter-resources', methods=['POST'])
def starter_resources():
    body = request.get_json(force=True)
    skill = body.get('skill') or (body.get('context') or {}).get('missing_skills', [None])[0]
    
    # Load real resources from file
    resources_path = os.path.join(os.path.dirname(__file__), '../resources/skills/learning_resources.json')
    with open(resources_path, 'r') as f:
        all_resources = json.load(f)
    
    # Normalize skill name for lookup
    skill_key = skill.lower() if skill else None
    resources = all_resources.get(skill_key, {})
    
    # If no resources found, return a default message
    if not resources:
        return jsonify({"resources": [{"title": "No curated resources found for this skill.", "url": "", "description": ""}]})
    
    # Format resources for frontend
    formatted = []
    for typ, val in resources.items():
        formatted.append({
            "title": f"{skill.title()} {typ.title()}",
            "url": val,
            "description": f"{typ.title()} resource for {skill.title()}"
        })
    
    return jsonify({"resources": formatted})

@main_routes.route('/roadmap', methods=['POST'])
def roadmap():
    body = request.get_json(force=True)
    analysis = body.get('analysis', {})
    resources = body.get('resources', [])
    context = body.get('context', {})

    try:
        # Step 2: roadmap generation
        p2 = build_prompt_step2(analysis, from_scratch=(not context.get('known_skills')))
        out2 = query_llm(context, p2)
        roadmap_json = json.loads(out2)
    except Exception:
        roadmap_json = [
            {"title": "Foundations", "weeks": 4, "outcomes": ["Python & Math basics"], "project": "Small data project"},
            {"title": "Modeling", "weeks": 6, "outcomes": ["Train & eval models"], "project": "Train a NN"}
        ]

    # Step 3: motivational message
    final_prompt = build_prompt_step3(roadmap_json)
    final_message = query_llm(context, final_prompt)

    return jsonify({"roadmap": roadmap_json, "final_message": final_message})

@main_routes.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json(force=True)
        skills_raw = data.get('skills', '')
        
        # Clean and extract skills
        if data.get('input_mode') == 'resume':
            skills = extract_skills_from_text(skills_raw)
        else:
            skills = clean_manual_input(skills_raw)
            
        # Get role recommendations
        recommendations = recommend_roles(skills, top_k=3)
        
        # Enhance with LLM insights for each recommendation
        for rec in recommendations:
            context = {
                "target_role": rec["career"],
                "known_skills": rec["matched_skills"],
                "learn_skills": rec["missing_skills"],
                "full_skillset": skills,
                "resources": rec["resources"]
            }
            
            prompt = f"""
            Given someone with skills in {', '.join(context['known_skills'])},
            provide a brief career transition plan to become a {context['target_role']}.
            Focus on immediate next steps and timeline.
            """
            
            try:
                llm_insight = query_llm(context, prompt)
                rec["ai_insights"] = llm_insight
            except Exception as e:
                logger.error(f"LLM insight failed for {rec['career']}: {e}")
                rec["ai_insights"] = "Unable to generate AI insights at this time."

        return jsonify({"recommendations": recommendations})
        
    except Exception as e:
        logger.error(f"Error in recommend route: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to generate recommendations",
            "details": str(e)
        }), 500