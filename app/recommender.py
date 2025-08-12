import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

#  Load Skill Space
with open("resources/skills/skills_matrix.json") as f:
    skill_space = json.load(f)

#  Load Learning Resources (used for missing skills) 
with open("resources/skills/learning_resources.json") as f:
    learning_resources = json.load(f)

# LOAD MERGED ROLES.JSON FILE
roles_path = "resources/roles/roles.json"
with open(roles_path) as f:
    raw_roles = json.load(f)

# FLATTEN TO LIST (and preserve role key/slug)
roles = []
for key, value in raw_roles.items():
    value["slug"] = key  # nice for LLM prompts
    roles.append(value)

#  Convert User Skill List to Vector 
def skills_to_vector(user_skills, skill_space):
    """
    Converts a list of user skills into a binary vector aligned with the global skill space.
    """
    return np.array([1 if skill in user_skills else 0 for skill in skill_space])

#  Skill Gap Checker 
def get_skill_gap(user_skills, role_name):
    """
    For a given role, compare required skills vs. user skills.
    Returns missing skills and resources to learn them.
    """
    for role in roles:
        # Match by slug instead of career name
        if role["slug"].lower() == role_name.lower():
            required = role["skills"]
            missing = [s for s in required if s not in user_skills]
            matched = [s for s in user_skills if s in required]

            # Get resource links for missing skills (fallback if not found)
            resources = {s: learning_resources.get(s, "No resource found") for s in missing}

            return {
                "career": role["career"],
                "slug": role["slug"],
                "skills": role["skills"],
                "matched_skills": matched,
                "missing_skills": missing,
                "resources": resources
            }

    return {"error": f"Role '{role_name}' not found."}

#  Role Recommender 
def recommend_roles(user_skills, top_k=3):
    """
    Recommends top-K career paths based on cosine similarity between user and role vectors.
    """
    user_vec = skills_to_vector(user_skills, skill_space)
    recommendations = []

    for role in roles:
        role_vec = skills_to_vector(role["skills"], skill_space)
        similarity = cosine_similarity([user_vec], [role_vec])[0][0]

        matched = [s for s in user_skills if s in role["skills"]]
        missing = [s for s in role["skills"] if s not in user_skills]
        resources = {s: learning_resources.get(s, "No resource found") for s in missing}

        recommendations.append({
            "career": role["career"],
            "score": round(float(similarity), 3),
            "matched_skills": matched,
            "missing_skills": missing,
            "resources": resources
        })

    # Sort by similarity score descending and return top-K
    return sorted(recommendations, key=lambda x: x["score"], reverse=True)[:top_k]

#  EXAMPLES (for testing) 
# if __name__ == "__main__":
#     print("\nSkill gap for Data Scientist:")
#     print(get_skill_gap(["python", "pandas", "matplotlib"], "Data Scientist"))


#  EXAMPLES (for testing) 
# if __name__ == "__main__":
#     # Example 1: Beginner (no skills)
#     print("Beginner:")
#     print(recommend_roles([]))

#     # # Example 2: Curious user — some ML skills
#     # print("\nWith ML skills:")
#     # print(recommend_roles(["python", "linux", "scikit-learn"]))

#     # Example 3: Wants to be a Data Scientist
#     print("\nSkill gap for Data Scientist:")
#     print(get_skill_gap(["python", "pandas", "matplotlib"], "Data Scientist"))
