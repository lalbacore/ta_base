"""
Tests for enhanced workflow with better quality checks.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from workflow.orchestrator import WorkflowOrchestrator, Mission
from swarms.team_agent.roles_v2 import Critic, Governance


class TestEnhancedCritic(unittest.TestCase):
    """Test the enhanced Critic agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.critic = Critic("test_workflow")
    
    def test_simple_code_analysis(self):
        """Test analyzing simple code."""
        code = '''#!/usr/bin/env python3
"""Simple test module."""

def main():
    """Main function."""
    print("Hello")

if __name__ == "__main__":
    main()
'''
        
        implementation = {
            "code": code,
            "language": "python"
        }
        
        result = self.critic.run(implementation)
        
        self.assertIn('quality_score', result)
        self.assertIn('issues', result)
        self.assertIn('strengths', result)
        self.assertIn('details', result)
        
        # Should have high quality
        self.assertGreater(result['quality_score'], 70)
        
        # Should have scores breakdown
        scores = result['details']['scores']
        self.assertIn('structure', scores)
        self.assertIn('documentation', scores)
        self.assertIn('security', scores)
    
    def test_security_issues_detection(self):
        """Test that security issues are detected."""
        code = '''
password = "hardcoded123"
api_key = "secret_key"

def run():
    eval("print('dangerous')")
'''
        
        implementation = {"code": code}
        result = self.critic.run(implementation)
        
        # Should detect security issues
        security_score = result['details']['scores']['security']
        self.assertLess(security_score, 100)
        
        # Should have security-related issues
        issues = result['issues']
        security_issues = [i for i in issues if 'password' in i.lower() or 'api' in i.lower() or 'eval' in i.lower()]
        self.assertGreater(len(security_issues), 0)


class TestEnhancedGovernance(unittest.TestCase):
    """Test the enhanced Governance agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.governance = Governance("test_workflow")
    
    def test_approval_workflow(self):
        """Test approval for high-quality code."""
        review = {
            "quality_score": 85,
            "issues": [],
            "details": {
                "scores": {
                    "structure": 90,
                    "documentation": 80,
                    "security": 100,
                    "maintainability": 85,
                    "performance": 90
                }
            }
        }
        
        result = self.governance.run(review)
        
        self.assertEqual(result['decision'], 'approved')
        self.assertEqual(len(result['violations']), 0)
        self.assertEqual(result['compliance_score'], 100)
    
    def test_rejection_for_low_quality(self):
        """Test rejection for low-quality code."""
        review = {
            "quality_score": 45,
            "issues": ['critical issue'],
            "details": {
                "scores": {
                    "structure": 50,
                    "documentation": 30,
                    "security": 40,
                    "maintainability": 60,
                    "performance": 50
                }
            }
        }
        
        result = self.governance.run(review)
        
        # Should not be approved
        self.assertIn(result['decision'], ['conditional', 'rejected'])
        self.assertGreater(len(result['violations']), 0)
        self.assertLess(result['compliance_score'], 100)
    
    def test_policy_enforcement(self):
        """Test that specific policies are enforced."""
        review = {
            "quality_score": 50,
            "issues": [],
            "details": {
                "scores": {
                    "security": 60,
                    "documentation": 40
                }
            }
        }
        
        # With security policy
        input_data = {
            "input": review,
            "instructions": {
                "policies": ["security", "documentation"]
            }
        }
        
        result = self.governance.run(input_data)
        
        # Should have violations for both policies
        self.assertGreater(len(result['violations']), 0)
        policy_names = [v['policy'] for v in result['violations']]
        self.assertTrue(any('security' in p for p in policy_names))


class TestMissionExecution(unittest.TestCase):
    """Test mission-based workflow execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = WorkflowOrchestrator("test_team")
    
    def test_simple_mission_execution(self):
        """Test executing a simple text mission."""
        mission_text = "Build a hello world program"
        
        results = self.orchestrator.execute_mission(mission_text)
        
        self.assertIsNotNone(results)
        self.assertIn('workflow_id', results)
        self.assertIn('results', results)
        self.assertIn('final_record', results)
        
        # Check all stages completed
        self.assertEqual(results['progress']['progress_percent'], 100.0)
        
        # Check final record has enhanced metrics
        record = results['final_record']
        self.assertIn('composite_score', record)
        self.assertIn('breakdown', record['composite_score'])
    
    def test_mission_object_execution(self):
        """Test executing a Mission object."""
        mission_data = {
            'mission': {
                'id': 'test_001',
                'name': 'Test Mission',
                'description': 'Test mission description',
                'requirements': ['Build something'],
                'acceptance_criteria': {
                    'quality_score': '>= 70'
                },
                'stages': {
                    'critic': {
                        'focus_areas': ['code_quality', 'security']
                    },
                    'governance': {
                        'policies': ['code_quality']
                    }
                }
            }
        }
        
        mission = Mission(mission_data)
        results = self.orchestrator.execute_mission(mission)
        
        self.assertIsNotNone(results)
        self.assertIn('acceptance_met', results)


if __name__ == '__main__':
    unittest.main()