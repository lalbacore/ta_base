"""
Tests for workflow orchestration and Turing Tape.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from workflow.tape import WorkflowTape, StageStatus, StageCheckpoint
from workflow.orchestrator import WorkflowOrchestrator


class TestWorkflowTape(unittest.TestCase):
    """Test the Turing Tape state machine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.stages = ["architect", "builder", "critic", "governance", "recorder"]
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_new_tape(self):
        """Test creating a new workflow tape."""
        mission = "Build a calculator"
        tape = WorkflowTape.create_new(mission, "test_team", self.stages)
        
        self.assertIsNotNone(tape.workflow_id)
        self.assertEqual(tape.mission, mission)
        self.assertEqual(tape.team_id, "test_team")
        self.assertEqual(tape.status, "pending")
        self.assertEqual(len(tape.stages), 5)
        
        # All stages should start as pending
        for stage in self.stages:
            self.assertEqual(tape.stages[stage].status, StageStatus.PENDING)
    
    def test_save_and_load_tape(self):
        """Test saving and loading a tape."""
        mission = "Build a calculator"
        tape = WorkflowTape.create_new(mission, "test_team", self.stages)
        
        # Save
        tape.save(self.temp_dir)
        
        # Load
        loaded_tape = WorkflowTape.load(tape.workflow_id, self.temp_dir)
        
        self.assertIsNotNone(loaded_tape)
        self.assertEqual(loaded_tape.workflow_id, tape.workflow_id)
        self.assertEqual(loaded_tape.mission, mission)
        self.assertEqual(len(loaded_tape.stages), 5)
    
    def test_stage_progression(self):
        """Test progressing through stages."""
        tape = WorkflowTape.create_new("Test mission", "test_team", self.stages)
        
        # Start first stage
        tape.start_stage("architect", {"input": "test"})
        self.assertEqual(tape.stages["architect"].status, StageStatus.IN_PROGRESS)
        self.assertEqual(tape.current_stage, "architect")
        
        # Complete first stage
        tape.complete_stage("architect", {"output": "design"})
        self.assertEqual(tape.stages["architect"].status, StageStatus.COMPLETED)
        self.assertIsNotNone(tape.stages["architect"].output_data)
    
    def test_stage_failure(self):
        """Test handling stage failure."""
        tape = WorkflowTape.create_new("Test mission", "test_team", self.stages)
        
        tape.start_stage("architect", {"input": "test"})
        tape.fail_stage("architect", "Something went wrong")
        
        self.assertEqual(tape.stages["architect"].status, StageStatus.FAILED)
        self.assertEqual(tape.status, "failed")
        self.assertIsNotNone(tape.stages["architect"].error)
    
    def test_get_next_pending_stage(self):
        """Test finding next pending stage."""
        tape = WorkflowTape.create_new("Test mission", "test_team", self.stages)
        
        # First pending should be architect
        next_stage = tape.get_next_pending_stage()
        self.assertEqual(next_stage, "architect")
        
        # Complete architect
        tape.start_stage("architect", {})
        tape.complete_stage("architect", {})
        
        # Next pending should be builder
        next_stage = tape.get_next_pending_stage()
        self.assertEqual(next_stage, "builder")
    
    def test_is_complete(self):
        """Test checking if workflow is complete."""
        tape = WorkflowTape.create_new("Test mission", "test_team", self.stages)
        
        self.assertFalse(tape.is_complete())
        
        # Complete all stages
        for stage in self.stages:
            tape.start_stage(stage, {})
            tape.complete_stage(stage, {})
        
        self.assertTrue(tape.is_complete())
    
    def test_get_progress(self):
        """Test getting workflow progress."""
        tape = WorkflowTape.create_new("Test mission", "test_team", self.stages)
        
        progress = tape.get_progress()
        self.assertEqual(progress['total_stages'], 5)
        self.assertEqual(progress['completed'], 0)
        self.assertEqual(progress['progress_percent'], 0)
        
        # Complete 2 stages
        for stage in self.stages[:2]:
            tape.start_stage(stage, {})
            tape.complete_stage(stage, {})
        
        progress = tape.get_progress()
        self.assertEqual(progress['completed'], 2)
        self.assertEqual(progress['progress_percent'], 40.0)


class TestWorkflowOrchestrator(unittest.TestCase):
    """Test the workflow orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = WorkflowOrchestrator("test_team")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execute_workflow(self):
        """Test executing a complete workflow."""
        mission = "Build a hello world program"
        
        results = self.orchestrator.execute_workflow(mission)
        
        self.assertIsNotNone(results)
        self.assertIn('workflow_id', results)
        self.assertIn('results', results)
        self.assertIn('final_record', results)
        
        # Check all stages executed
        self.assertIn('architect', results['results'])
        self.assertIn('builder', results['results'])
        self.assertIn('critic', results['results'])
        self.assertIn('governance', results['results'])
        self.assertIn('recorder', results['results'])
        
        # Check progress is 100%
        self.assertEqual(results['progress']['progress_percent'], 100.0)
    
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        mission = "Build a calculator"
        results = self.orchestrator.execute_workflow(mission)
        workflow_id = results['workflow_id']
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        
        self.assertIsNotNone(status)
        self.assertEqual(status['workflow_id'], workflow_id)
        self.assertEqual(status['mission'], mission)
        self.assertEqual(status['status'], 'completed')


if __name__ == '__main__':
    unittest.main()