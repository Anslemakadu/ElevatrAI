# Project: ElevatrAI

## 🔍 Overview

ElevatrAI is an open-source, AI-powered career assistant designed to help users:
- Understand which tech roles they're fit for based on their current skills or resume
- Discover personalized learning paths toward roles like ML Engineer, DevOps, Frontend Developer, etc.
- Receive weekly study plans, curated learning resources, and GitHub project ideas
- Track progress over time through lightweight session management
- Help user to upscale from there current role to another role and discover skill gaps and give them hte learning path to learn that and how long it i will take.

This tool is built for job seekers, tech upskillers, upscalling you tech skills, students, and early-career devs who want structured, actionable guidance — not vague career advice.

It combines:
- **NLP** for skill extraction
- **Recommender systems** for role suggestions and skills gaps
- **LLMs** for personalized learning path generation and more user guidiance on there career and somwthing to talk back to.

---

## Tech Stack

### Backend:
- **Flask** (main web server)
- **FastAPI** (LLM inference server on the HuggingSpace free Space)

### AI/NLP/ML:
- `sentence-transformers` for fuzzy skill matching
- `scikit-learn` (cosine similarity)
- `transformers` (LLM inference via Hugging Face)
- `PyPDF2`  for resume parsing

### Storage:
- `user_data.json` (local user sessions)
- `roles.json`, `skills.json`, `learning_resources.json` (custom role/skill/resource databases)

### Frontend:
- HTML/CSS templates (`dashboard.html`, `results.html`, etc.)
- React (planned upgrade for better user interface)

### Deployment:
- Local (Ubuntu/Linux dev environment)
- Hugging Face Spaces(for the LLM we are using) / Render (target for deployment)

---

## 🧱 Project Architecture

User Input (Resume or Manual)
|
[parser.py]
|
↓ (via nlp_utils.py)
[parsed_skills]
|
[recommender.py] ——→ Matches roles, checks skill gaps, for new user give them what to learn base on the role they pick
|
↓
Recommended roles + missing skills for the role you're upcalling to
|
[llm.py] ← Prompt built via llm_prompt_builder.py 
|
Generates learning roadmap using LLM (by pulling the from the free rources that we have provided and for each role)
↓
[routes.py] → Renders results to user via Flask templates


---

## 📂 Key Project Structure

.
├── app/
│ ├── parser.py # Extracts + normalizes user skills
│ ├── nlp_utils.py # Sentence embedding + similarity matching
│ ├── recommender.py # Role recommendation via cosine similarity + skill gap detection
│ ├── llm.py # Sends enriched prompt to LLM
│ ├── llm_prompt_builder.py # Builds final LLM input from gaps/goals
│ ├── routes.py # Flask routes and rendering logic
│ ├── llm_server/ # FastAPI server for local model inference
│ └── templates/ # HTML files (home, dashboard, results)
├── data/user_data.json # Stores per-session user progress       
├── resources/ # Static role/skill/resource info
│ ├── roles/roles.json
│ ├── skills/skills_matrix.json
│ ├── skills/learning_resources.json
│ └── skills.json
├── run.py # Entry point for Flask app
├── static/styles.css # Custom styling
└── context.md # This file (context for LLM)


---

## 🎯 Current & Planned Features

### ✅ Built:
- Resume parser & manual skill entry
- Cosine similarity–based role recommender
- Skill gap detection


### 🔜 Planned:
- LLM-based learning path generator
- Dashboard UI with results + roadmap
- JSON-based persistent session store
- Weekly learning plan breakdown
- React UI upgrade
- Leaderboard: Top trending learner
- User login/session tracking (via email)
- User clustering or CF-based recommender upgrade
- Deploy on Hugging Face Spaces and Render

---

## 🧠 What I Want from the LLM

You are my assistant for ElevatrAI. Here's what I want your help with:

### 👨🏽‍💻 Logic & Design
- Help me design clean, modular code (Pythonic, scalable)
- Suggest file splits/refactors when things get messy
- Point out tight coupling or anti-patterns in Flask routing

### 🧠 AI/ML/NLP
- Improve my skill matching logic (sentence embeddings, thresholding)
- Make my recommender more robust (maybe hybrid methods)
- Improve my prompt building for the LLM (concise but info-rich)

### 🐞 Debugging
- Walk through bugs WITH me, don’t just fix it
- Always explain root causes and help me reason through the code

### ✍🏽 Prompt Engineering
- Help refine prompts that give better learning paths
- Suggest ways to personalize tone or difficulty level

### 🧪 Testing + UX
- Help me design test cases (esp. for recommender and LLM output)
- Suggest improvements to the UI/UX or user journey

---

## 📌 Notes, Constraints, and Assumptions

- Runs locally on Ubuntu Linux — assume I’m on that stack
- All data is stored in local JSON files for now — no DB yet
- Project is being built as an open-source showcase to:
  - Show off fullstack AI skills
  - Help people upskill faster
  - Attract real job opportunities
- Must stay fast, lightweight, and privacy-safe
- No API keys or external DBs by default
- LLM is hosted on Hugging Face Spaces (or locally via FastAPI)
