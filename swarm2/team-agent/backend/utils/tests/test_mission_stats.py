
import unittest
from unittest.mock import MagicMock, patch
from collections import namedtuple

# Mock Governance Decision
GovernanceDecision = namedtuple('GovernanceDecision', ['decision_id', 'decision', 'reason'])

class TestMissionStats(unittest.TestCase):
    
    @patch('app.database.get_backend_session')
    @patch('app.models.governance.GovernanceDecision', create=True)
    def test_get_governance_stats(self, mock_gov_model, mock_get_session):
        # Setup mock session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Test Data: 3 AI, 1 Human, 1 Rejected
        mock_decisions = [
            GovernanceDecision('1', 'approved', 'Auto-approved by policy'),
            GovernanceDecision('2', 'approved', 'Auto-approved by policy'),
            GovernanceDecision('3', 'approved', 'Auto-approved by policy'),
            GovernanceDecision('4', 'approved', 'Human approval granted'),
            GovernanceDecision('5', 'rejected', 'Human rejected'),
            GovernanceDecision('6', 'approved', 'Legacy approval'), # Should correspond to AI fallback
        ]
        
        mock_session.query.return_value.all.return_value = mock_decisions
        
        # Import service (delayed import to pick up mocks if needed, though patch handles it)
        from app.services.mission_service import mission_service
        
        # Execute
        stats = mission_service.get_governance_stats()
        
        # Assertions
        self.assertEqual(stats['total_decisions'], 6)
        self.assertEqual(stats['rejected'], 1)
        self.assertEqual(stats['human_approved'], 1)
        # AI = 3 explicit + 1 legacy fallback = 4
        self.assertEqual(stats['ai_approved'], 4) 
        
        # Ratio = 4 / (4 + 1) = 0.8
        self.assertEqual(stats['autonomy_ratio'], 0.8)

    @patch('app.database.get_backend_session')
    def test_get_governance_stats_empty(self, mock_get_session):
        # Setup mock session with no decisions
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = []
        
        from app.services.mission_service import mission_service
        stats = mission_service.get_governance_stats()
        
        self.assertEqual(stats['total_decisions'], 0)
        self.assertEqual(stats['autonomy_ratio'], 0.0)

if __name__ == '__main__':
    unittest.main()
