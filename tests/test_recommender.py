"""
Recommender System Test Suite

This module tests the ML-powered career recommendation system of ElevatrAI.
It validates:
1. Career transition analysis
2. Skill gap identification
3. Learning path generation
4. Resource recommendations

Test Coverage:
- ML model outputs
- Recommendation quality
- Edge cases
- System reliability

How to run:
$ python -m tests.test_recommender

Author: Anslem Akadu
"""

import json
import unittest
from app.recommender import analyze_career_transition, recommend_roles

class TestRecommender(unittest.TestCase):
    """Test suite for the ML recommendation engine."""
    
    def setUp(self):
        """Initialize test data."""
        self.test_skills = ["python", "pandas", "matplotlib", "sql"]
    
    def test_career_transition_analysis(self):
        """Test ML-powered career transition analysis."""
        result = analyze_career_transition(
            user_skills=self.test_skills,
            current_role_slug="data_scientist",
            target_role_slug="ml_engineer",
            transition_type="upskill"
        )
        self.assertIsNotNone(result)
        self.assertIn("matched_skills", result)
        self.assertIn("missing_skills", result)
    
    def test_beginner_analysis(self):
        """Test complete beginner career path analysis."""
        result = analyze_career_transition(
            user_skills=[],
            current_role_slug="none",
            target_role_slug="data_scientist",
            transition_type="beginner"
        )
        self.assertIsNotNone(result)
        self.assertIn("learning_path", result)

# Manual testing functionality
if __name__ == "__main__":
    def run_manual_tests():
        """Run manual tests with detailed output for development."""
        print("=== Career Transition Analysis ===")
        test_skills = ["python", "pandas", "matplotlib", "sql"]
        
        # Test 1: Data Scientist to ML Engineer
        print("\nTesting: DS → ML Engineer Transition")
        result = analyze_career_transition(
            user_skills=test_skills,
            current_role_slug="data_scientist",
            target_role_slug="ml_engineer",
            transition_type="upskill"
        )
        print(json.dumps(result, indent=2))
        
        # Test 2: Complete beginner
        print("\nTesting: Complete Beginner → Data Scientist")
        beginner_result = analyze_career_transition(
            user_skills=[],
            current_role_slug="none",
            target_role_slug="data_scientist",
            transition_type="beginner"
        )
        print(json.dumps(beginner_result, indent=2))
    
    # Run both unit tests and manual tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False)
    print("\nRunning manual tests...")
    run_manual_tests()

# TODO: Future Test Improvements
# 1. Add ML model accuracy metrics
# 2. Test recommendation diversity
# 3. Add A/B testing framework
# 4. Add stress testing for large skill sets
# 5. Add recommendation quality metrics