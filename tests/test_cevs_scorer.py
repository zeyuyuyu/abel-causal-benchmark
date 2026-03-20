"""
Tests for Enhanced CEVS Scorer
"""

import pytest
from abel_benchmark.enhanced_cevs_scorer import (
    CEVSComponents,
    EnhancedCEVSScorer,
    calculate_cevs,
)


class TestCEVSComponents:
    """Test CEVS dataclass."""
    
    def test_total_calculation(self):
        """Test weighted total calculation."""
        cevs = CEVSComponents(
            explainability=1.0,
            intervenability=1.0,
            confidence_calibration=1.0,
            accuracy=1.0
        )
        assert cevs.total == 1.0
    
    def test_partial_scores(self):
        """Test with partial scores."""
        cevs = CEVSComponents(
            explainability=0.5,
            intervenability=0.5,
            confidence_calibration=0.5,
            accuracy=0.5
        )
        assert cevs.total == 0.5


class TestEnhancedCEVSScorer:
    """Test enhanced scorer."""
    
    def test_category_a_scoring(self):
        """Test Category A (predict) scoring."""
        scorer = EnhancedCEVSScorer()
        
        response = {
            'prediction': 0.05,
            'probability_up': 0.68,
            'features': [
                {'cumulative_impact': 0.02, 'tau': 2},
                {'cumulative_impact': 0.015, 'tau': 1}
            ]
        }
        
        question = {'id': 'A1', 'category': 'A'}
        
        cevs = scorer.calculate_cevs(response, question)
        
        assert 0 <= cevs.explainability <= 1
        assert 0 <= cevs.intervenability <= 1
        assert 0 <= cevs.confidence_calibration <= 1
        assert cevs.total > 0
    
    def test_category_b_intervention_scoring(self):
        """Test Category B (intervention) scoring."""
        scorer = EnhancedCEVSScorer()
        
        response = {
            'prediction': 0.03,
            'shock_magnitude': 0.05,
            'propagation_path': [
                {'node': 'NVDA', 'hop': 0, 'effect': 0.08},
                {'node': 'LRCX', 'hop': 1, 'effect': 0.04, 'tau': 12}
            ],
            'affected_nodes': ['NVDA', 'LRCX', 'AMAT']
        }
        
        question = {'id': 'B3', 'category': 'B'}
        
        cevs = scorer.calculate_cevs(response, question)
        
        # Category B should have higher intervenability weight
        assert cevs.intervenability > 0.3
        assert cevs.total > 0
    
    def test_empty_response(self):
        """Test handling of empty response."""
        scorer = EnhancedCEVSScorer()
        
        response = {}
        question = {'id': 'A1', 'category': 'A'}
        
        cevs = scorer.calculate_cevs(response, question)
        
        assert cevs.total >= 0
        assert cevs.explainability < 0.5
    
    def test_scoring_report(self):
        """Test report generation."""
        scorer = EnhancedCEVSScorer()
        
        # Score multiple questions
        for i in range(3):
            scorer.calculate_cevs(
                {'prediction': 0.05, 'probability_up': 0.6},
                {'id': f'A{i}', 'category': 'A'}
            )
        
        report = scorer.get_scoring_report()
        
        assert 'total_questions_scored' in report
        assert report['total_questions_scored'] == 3


class TestCalculateCEVSConvenience:
    """Test convenience function."""
    
    def test_convenience_function(self):
        """Test calculate_cevs() helper."""
        response = {
            'prediction': 0.05,
            'probability_up': 0.65
        }
        question = {'id': 'A1', 'category': 'A'}
        
        cevs = calculate_cevs(response, question)
        
        assert isinstance(cevs, CEVSComponents)
        assert cevs.total > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
