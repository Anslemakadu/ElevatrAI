"""
ElevatrAI Web Application Routes

This module implements the web application's API endpoints and request handling logic,
serving as the integration layer between the frontend UI and our ML-powered backend.
It orchestrates the flow of data through the system:

Frontend → Routes → ML Analysis → Results → Frontend

Key Components:
1. Request Handling: Process form submissions and file uploads
2. Input Validation: Ensure data quality and security
3. ML Pipeline Integration: Connect to our skill analysis engine
4. Response Formation: Structure data for frontend templates

Data Flow:
1. User submits skills/resume → validate input
2. Parse and extract skills → normalize data
3. Run ML analysis → get recommendations
4. Format results → render appropriate template

Author: Anslem Akadu
"""

import json
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.parser import parse_user_input
from app.recommender import (
    analyze_career_transition,
    recommend_roles,
    generate_recommendations,
    load_learning_resources,
    roles_data
)
from app.file_utils import process_resume_upload

# Create a Flask Blueprint for our routes
# This allows for modular application structure and easier testing
main_routes = Blueprint("main_routes", __name__)

# Load role definitions at module level for better performance
# This prevents reloading the data on every request
try:
    with open("resources/roles.json") as f:
        ROLES_DATA = json.load(f)
        AVAILABLE_ROLES = list(ROLES_DATA.keys())
except Exception as e:
    print(f"Error loading roles data: {e}")
    ROLES_DATA = {}
    AVAILABLE_ROLES = []

# TODO: Add role data validation and error handling
# TODO: Implement role data caching with TTL
# TODO: Add API versioning for future compatibility

def allowed_file(filename: str) -> bool:
    """
    Validate file types for secure resume uploads.
    
    This security function ensures that only allowed file types can be processed,
    preventing potential security vulnerabilities from malicious file uploads.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
        
    Example:
        >>> allowed_file('resume.pdf')
        True
        >>> allowed_file('script.js')
        False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

@main_routes.route('/')
def home():
    """
    Render the application's home page.
    
    This route:
    1. Loads available career roles from our dataset
    2. Passes them to the template for dynamic role selection
    3. Renders the main UI where users start their career analysis
    
    Returns:
        Rendered index.html template with:
        - List of available career roles
        - Dynamic form fields
        - File upload options
    """
    return render_template("index.html", roles=AVAILABLE_ROLES)

@main_routes.route('/select-role', methods=['POST'])
def select_role():
    """
    Handle role selection and generate personalized learning journey.
    
    This endpoint processes role selections from the recommendations page:
    1. Validates the selected role and user's current skills
    2. Generates a career transition analysis
    3. Creates a phased learning plan with resources
    
    Request Parameters:
        role_slug (str): Identifier for the selected role
        skills_str (str): Comma-separated list of user's current skills
        
    Returns:
        Rendered results.html template with:
        - Career transition analysis
        - Phased learning plan
        - Curated learning resources
        
    Error Handling:
        - Invalid role selection → Redirect to home with error message
        - Missing skills → Redirect to home with error message
        - Analysis errors → Redirect to home with error details
    """
    role_slug = request.form.get('role_slug')
    skills_str = request.form.get('skills')
    
    if not role_slug or not skills_str:
        flash('Invalid role selection.', 'error')
        return redirect(url_for('main_routes.home'))
    
    try:
        user_skills = [s.strip() for s in skills_str.split(',')]
        
        # Get career transition analysis
        analysis = analyze_career_transition(
            user_skills=user_skills,
            current_role_slug=None,
            target_role_slug=role_slug,
            transition_type='upskill'
        )
        
        phases = generate_recommendations(analysis)
        
        return render_template(
            'results.html',
            transition_type='selected_role',
            analysis=analysis,
            phases=phases,
            user_skills=user_skills,
            selected_role=roles_data[role_slug]
        )
        
    except Exception as e:
        flash(f'Error analyzing role: {str(e)}', 'error')
        return redirect(url_for('main_routes.home'))

@main_routes.route('/skill-gap', methods=['POST'])
def analyze_skills():
    """
    Main Analysis Endpoint: Process career analysis requests and generate recommendations.
    
    This is the core endpoint of our application that:
    1. Handles multiple analysis paths:
       - Role recommendations based on skills
       - Complete beginner roadmap
       - Upskilling in current role
       - Career transition analysis
       
    2. Processes input from various sources:
       - Manual skill entry
       - Resume uploads (PDF/DOCX)
       - Current/target role selections
       
    3. Generates personalized results:
       - Skill gap analysis
       - Learning recommendations
       - Career transition roadmap
       
    Request Parameters:
        path: Analysis type ('recommend', 'beginner', 'upskill', 'switch')
        current_role: User's current role (optional)
        target_role: Desired career role
        skills_text: Manually entered skills
        raw_skills: Skills from other sources
        resume: File upload (optional)
        
    Returns:
        Rendered results.html with personalized analysis
        
    Error Handling:
        - Invalid input → Flash message + redirect
        - Missing required data → Flash message + redirect
        - Processing errors → Flash message + redirect
        
    Security:
        - File type validation
        - Input sanitization
        - Error message sanitization
    """
    # Extract and validate form data
    path = request.form.get('path')
    current_role = request.form.get('current_role', '').strip()
    target_role = request.form.get('target_role', '').strip()
    skills_text = request.form.get('skills', '').strip()
    raw_skills = request.form.get('raw_skills', '').strip()
    
    # Handle different analysis paths based on user's request
    if path == 'recommend':
        # Path: Role Recommendations
        # This path uses ML to suggest roles based on user's current skills
        transition_type = 'recommend'
        
        # Validate input: require either manual skills or resume
        if not skills_text and not raw_skills and 'resume' not in request.files:
            flash('Please provide your skills either by pasting them or uploading a resume.', 'error')
            return redirect(url_for('main_routes.home'))
            
        try:
            # Step 1: Extract and normalize skills
            # We don't need role information for pure recommendations
            parsed = parse_user_input(
                target_role=None,  # Not needed for recommendations
                current_role=None, # Not needed for recommendations
                skills=skills_text,
                resume_text=None,  # Resume processing handled separately
                transition_type='recommend'
            )
            
            # Handle parsing errors
            if parsed.get('error'):
                flash(parsed['error'], 'error')
                return redirect(url_for('main_routes.home'))
                
            # Step 2: Generate Role Recommendations
            # This uses our ML model to match skills with potential roles
            analysis = recommend_roles(parsed.get('skills', []))
            
            # Step 3: Sort and filter recommendations
            # We show only top 3 roles sorted by match score
            if 'recommendations' in analysis:
                analysis['recommendations'] = sorted(
                    analysis['recommendations'],
                    key=lambda x: x['score'],  # Sort by ML confidence score
                    reverse=True
                )[:3]  # Limit to top 3 matches
            
            return render_template(
                'results.html',
                transition_type='recommend',
                analysis=analysis,
                recommendations=analysis.get('recommendations', []),
                user_skills=parsed.get('skills', [])
            )
        except Exception as e:
            flash(f'Error generating recommendations: {str(e)}', 'error')
            return redirect(url_for('main_routes.home'))
    
    # Handle Beginner Path
    # This path creates a complete learning roadmap for beginners
    elif path == 'beginner':
        transition_type = 'beginner'
        if not target_role or target_role not in AVAILABLE_ROLES:
            flash('Please select your target role for the beginner path.', 'error')
            return redirect(url_for('main_routes.home'))
            
    # Handle Beginner With Some Skills Path
    # Similar to beginner but takes existing skills into account
    elif path == 'beginner_with_skills':
        transition_type = 'beginner'
        # Validate target role selection
        if not target_role or target_role not in AVAILABLE_ROLES:
            flash('Please select your target role for the beginner path.', 'error')
            return redirect(url_for('main_routes.home'))
        # Validate skill input
        if not skills_text and not raw_skills:
            flash('Please provide some skills you have, either by pasting or uploading a resume.', 'error')
            return redirect(url_for('main_routes.home'))
        current_role = None  # No current role for beginners with skills
    
    # Handle Upskilling Path
    # This path focuses on advancing within the current role
    elif path == 'upskill':
        transition_type = 'same_role'
        # Validate current role
        if not current_role or current_role not in AVAILABLE_ROLES:
            flash('Please select your current role for upskilling.', 'error')
            return redirect(url_for('main_routes.home'))
        # For upskilling, target is same as current role
        target_role = current_role
        
    # Handle Career Switch Path
    # This path analyzes transitions between different roles
    else:  # switch
        transition_type = 'upskill'
        # Validate both current and target roles
        if not current_role or not target_role or current_role not in AVAILABLE_ROLES or target_role not in AVAILABLE_ROLES:
            flash('Please select both your current and target roles for the career switch.', 'error')
            return redirect(url_for('main_routes.home'))
        # Prevent incorrect path usage
        if current_role == target_role:
            flash('For same role progression, please use the "Level Up Current Role" option instead.', 'error')
            return redirect(url_for('main_routes.home'))
    
    # Resume Processing Section
    # Handle file uploads and extract text content
    resume_text = None
    if 'resume' in request.files:
        file = request.files['resume']
        if file and file.filename and allowed_file(file.filename):
            try:
                # Extract text from resume using our NLP pipeline
                resume_text = process_resume_upload(file)
            except Exception as e:
                # Provide user-friendly error message while logging details
                print(f"Resume processing error: {str(e)}")  # For debugging
                flash('Could not read file. Please upload PDF/DOCX or paste skills.', 'error')
                return redirect(url_for('main_routes.home'))

    # Skill Analysis Pipeline
    try:
        # For recommendation path: Focus on skill matching
        if path == 'recommend':
            # Extract and analyze skills without role context
            parsed = parse_user_input(
                target_role=None,     # No target role needed
                current_role=None,     # No current role needed
                skills=skills_text,    # Manual skill input
                resume_text=resume_text,# Extracted resume text
                transition_type='recommend'
            )
            
            if parsed.get('error'):
                flash(parsed['error'], 'error')
                return redirect(url_for('main_routes.home'))
                
            # Get top 3 role recommendations
            recommendations = recommend_roles(parsed.get('skills', []))
            return render_template(
                'results.html',
                transition_type='recommend',
                recommendations=recommendations,
                user_skills=parsed.get('skills', [])
            )
        
        # For other paths, continue with normal flow
        parsed = parse_user_input(
            target_role=target_role,
            current_role=current_role,
            skills=skills_text,
            resume_text=resume_text,
            transition_type=transition_type
        )
        
        if parsed.get('error'):
            flash(parsed['error'], 'error')
            return redirect(url_for('main_routes.home'))
            
        # Analyze career transition
        analysis = analyze_career_transition(
            user_skills=parsed.get('skills', []),
            current_role_slug=current_role,
            target_role_slug=target_role,
            transition_type=transition_type
        )
        
        # Log analysis results for monitoring and debugging
        # TODO: Replace with proper logging system
        print("Analysis result:", analysis)
        print("Skills found:", analysis.get('matched_skills'))
        print("Missing skills:", analysis.get('missing_skills'))
        print("Resources:", analysis.get('learning_resources'))
        
        # Cache analysis results in session
        # TODO: Move to Redis/proper caching system for scalability
        session['analysis'] = analysis
        
        # Return results to frontend
        return render_template('results.html', 
            analysis=analysis,          # ML analysis results
            transition_type=transition_type,  # Path type
            current_role=current_role,  # Starting point
            target_role=target_role     # Career goal
        )
        
    except Exception as e:
        # Log the error for debugging
        # TODO: Add proper error logging and monitoring
        print(f"Error in skill analysis: {str(e)}")
        
        # Show user-friendly error message
        flash("An error occurred while analyzing your career path. Please try again.", 'error')
        return redirect(url_for('main_routes.home'))

# TODO: Add the following improvements:
# 1. API Documentation using Swagger/OpenAPI
# 2. Rate limiting for API endpoints
# 3. Caching layer for frequent requests
# 4. Async processing for long-running analyses
# 5. Better error handling and validation
# 6. Monitoring and analytics
# 7. A/B testing framework for ML model improvements


