"""
Parser Module Test Suite

This module tests the skill parsing and input processing functionality of ElevatrAI.
It validates the parser's ability to handle different career transition scenarios:
1. Career transitions with existing skills
2. Complete beginners
3. Same role enhancements

Test Coverage:
- Input validation
- Skill normalization
- Role validation
- Different transition types

How to run:
$ python -m tests.test_parser

Author: Anslem Akadu
"""

import json
import unittest
from app.parser import parse_user_input

class TestParser(unittest.TestCase):
    """Test suite for the parser module's core functionality."""
    
    def test_career_transition(self):
        """Test career transition scenario with existing skills."""
        result = parse_user_input(
            target_role="ml_engineer",
            current_role="data_scientist",
            skills="python, pandas, scikit-learn, sql",
            transition_type="upskill"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["transition_type"], "upskill")
        self.assertIn("python", result["matched_skills"])
    
    def test_complete_beginner(self):
        """Test complete beginner scenario with no prior skills."""
        result = parse_user_input(
            target_role="data_scientist",
            transition_type="beginner"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["transition_type"], "beginner")
        self.assertEqual(len(result.get("matched_skills", [])), 0)
    
    def test_same_role_enhancement(self):
        """Test skill enhancement within the same role."""
        result = parse_user_input(
            target_role="backend_engineer",
            current_role="backend_engineer",
            skills="python, flask, postgresql",
            transition_type="same_role"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["transition_type"], "same_role")
        self.assertIn("python", result["matched_skills"])

# Manual testing functionality
if __name__ == "__main__":
    # For quick manual testing during development
    def run_manual_tests():
        """Run manual tests with detailed output for development."""
        print("=== Manual Parser Testing ===\n")
        
        # Test 1: Career transition with skills
        print("Testing: Career Transition")
        test1 = parse_user_input(
            target_role="ml_engineer",
            current_role="data_scientist",
            skills="python, pandas, scikit-learn, sql",
            transition_type="upskill"
        )
        print(json.dumps(test1, indent=2))
        print("\n" + "="*50 + "\n")
        
        # Test 2: Complete beginner
        print("Testing: Complete Beginner")
        test2 = parse_user_input(
            target_role="data_scientist",
            transition_type="beginner"
        )
        print(json.dumps(test2, indent=2))
        print("\n" + "="*50 + "\n")
        
        # Test 3: Same role enhancement
        print("Testing: Same Role Enhancement")
        test3 = parse_user_input(
            target_role="backend_engineer",
            current_role="backend_engineer",
            skills="python, flask, postgresql",
            transition_type="same_role"
        )
        print(json.dumps(test3, indent=2))
    
    # Run both unit tests and manual tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False)
    print("\nRunning manual tests...")
    run_manual_tests()

# TODO: Future Test Improvements
# 1. Add edge case testing (invalid roles, empty skills)
# 2. Add property-based testing for input validation
# 3. Add integration tests with the ML pipeline
# 4. Add performance benchmarks
# 5. Add test coverage reporting