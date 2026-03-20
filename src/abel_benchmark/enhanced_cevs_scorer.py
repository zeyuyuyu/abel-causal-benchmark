#!/usr/bin/env python3
"""
Enhanced CEVS (Causal Emotional Value Score) Scorer for FutureX Benchmark V2

Key improvements over V1:
1. Better intervention scoring with multi-dimensional evaluation
2. Hierarchical scoring: Basic → Enhanced → Exceptional
3. Category-specific scoring weights
4. Response validation against expected schema
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class CEVSComponents:
    """Individual CEVS component scores."""
    explainability: float  # 0-1: Can trace causal path?
    intervenability: float  # 0-1: Can answer what-if?
    confidence_calibration: float  # 0-1: Confidence matches accuracy
    accuracy: float  # 0-1: Directional correctness (if ground truth available)
    
    @property
    def total(self) -> float:
        """Weighted total score."""
        weights = {
            'explainability': 0.30,
            'intervenability': 0.25,
            'confidence_calibration': 0.25,
            'accuracy': 0.20
        }
        return sum(getattr(self, k) * v for k, v in weights.items())


class EnhancedCEVSScorer:
    """
    Enhanced CEVS scorer with category-specific logic.
    """
    
    # Category-specific scoring criteria
    CATEGORY_CRITERIA = {
        'A': {  # Predict
            'explainability_weight': 0.35,
            'intervenability_weight': 0.15,
            'confidence_weight': 0.30,
            'accuracy_weight': 0.20,
            'required_fields': ['prediction', 'probability_up'],
            'bonus_fields': ['features', 'parents', 'tau']
        },
        'B': {  # Intervene
            'explainability_weight': 0.30,
            'intervenability_weight': 0.35,  # Higher weight for intervention
            'confidence_weight': 0.20,
            'accuracy_weight': 0.15,
            'required_fields': ['prediction', 'shock_magnitude', 'propagation'],
            'bonus_fields': [
                'intervention_effect', 'propagation_path', 'affected_nodes',
                'second_order_effects', 'systemic_risk_indicator'
            ]
        },
        'C': {  # Path
            'explainability_weight': 0.40,  # Path clarity is key
            'intervenability_weight': 0.20,
            'confidence_weight': 0.25,
            'accuracy_weight': 0.15,
            'required_fields': ['path', 'path_length'],
            'bonus_fields': ['intermediate_nodes', 'tau_values', 'alternative_paths']
        },
        'D': {  # Sensitivity
            'explainability_weight': 0.30,
            'intervenability_weight': 0.20,
            'confidence_weight': 0.40,  # Confidence analysis is key
            'accuracy_weight': 0.10,
            'required_fields': ['probability_up', 'confidence_metrics'],
            'bonus_fields': ['critical_parents', 'robustness_score', 'regime_analysis']
        },
        'E': {  # Attest
            'explainability_weight': 0.30,
            'intervenability_weight': 0.25,
            'confidence_weight': 0.25,
            'accuracy_weight': 0.20,
            'required_fields': ['comparison', 'ranking'],
            'bonus_fields': ['quantitative_metrics', 'visualization_data']
        }
    }
    
    def __init__(self):
        self.scoring_log: List[Dict] = []
    
    def calculate_cevs(
        self,
        response: Dict[str, Any],
        question: Dict[str, Any],
        ground_truth: Optional[Dict] = None
    ) -> CEVSComponents:
        """
        Calculate CEVS with category-specific logic.
        
        Args:
            response: API response from CG
            question: Question definition from benchmark JSON
            ground_truth: Optional ground truth for accuracy scoring
            
        Returns:
            CEVSComponents with individual scores
        """
        category = question.get('category', 'A')
        criteria = self.CATEGORY_CRITERIA.get(category, self.CATEGORY_CRITERIA['A'])
        
        # Calculate each component
        explainability = self._score_explainability(response, question, criteria)
        intervenability = self._score_intervenability(response, question, criteria)
        confidence = self._score_confidence(response, question, criteria)
        accuracy = self._score_accuracy(response, question, ground_truth)
        
        # Apply category-specific weights
        total = (
            explainability * criteria['explainability_weight'] +
            intervenability * criteria['intervenability_weight'] +
            confidence * criteria['confidence_weight'] +
            accuracy * criteria['accuracy_weight']
        )
        
        # Log scoring details
        self.scoring_log.append({
            'question_id': question.get('id'),
            'category': category,
            'explainability': explainability,
            'intervenability': intervenability,
            'confidence': confidence,
            'accuracy': accuracy,
            'total': total
        })
        
        return CEVSComponents(
            explainability=explainability,
            intervenability=intervenability,
            confidence_calibration=confidence,
            accuracy=accuracy
        )
    
    def _score_explainability(
        self,
        response: Dict,
        question: Dict,
        criteria: Dict
    ) -> float:
        """
        Score explainability based on causal traceability.
        
        Scoring levels:
        - 0.0-0.3: Basic (has prediction but no causal explanation)
        - 0.3-0.6: Enhanced (has features with attribution)
        - 0.6-0.9: Advanced (has full causal path with tau)
        - 0.9-1.0: Exceptional (has second-order effects, counterfactuals)
        """
        score = 0.0
        
        # Basic: Has any prediction
        if 'prediction' in response or 'cumulative_prediction' in response:
            score += 0.2
        
        # Enhanced: Has feature-level attribution
        if 'features' in response and isinstance(response['features'], list):
            features = response['features']
            if features:
                # Check for impact attribution
                has_impact = any(
                    'cumulative_impact' in f or 'impact_percent' in f or 'weight' in f
                    for f in features
                )
                if has_impact:
                    score += 0.2
                
                # Bonus: Has parent information
                has_parents = any('parent' in f or 'source' in f for f in features)
                if has_parents:
                    score += 0.1
        
        # Advanced: Has causal path structure
        path_keys = ['parents', 'children', 'path', 'paths', 'propagation_path', 'causal_path']
        if any(k in response for k in path_keys):
            score += 0.2
            
            # Bonus: Has tau/temporal information
            tau_keys = ['tau', 'tau_value', 'max_lookahead_hours', 'time_lag', 'delay_hours']
            if any(k in str(response).lower() for k in tau_keys):
                score += 0.1
        
        # Exceptional: Has second-order or systemic effects
        if any(k in response for k in ['second_order_effects', 'systemic_risk', 'spillover']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_intervenability(
        self,
        response: Dict,
        question: Dict,
        criteria: Dict
    ) -> float:
        """
        Score intervenability - critical for Category B questions.
        
        Scoring levels:
        - 0.0-0.2: No intervention capability
        - 0.2-0.5: Basic shock response
        - 0.5-0.8: Propagation path identified
        - 0.8-1.0: Quantified multi-hop intervention effects
        """
        category = question.get('category', 'A')
        
        # Category B questions require intervention scoring
        if category == 'B':
            return self._score_intervention_question(response, question)
        
        # Non-B questions get partial credit if intervention API works
        intervention_keys = ['intervention_effect', 'intervention_impact', 'shock_response']
        if any(k in response for k in intervention_keys):
            return 0.5
        
        return 0.2  # Default for non-intervention questions
    
    def _score_intervention_question(
        self,
        response: Dict,
        question: Dict
    ) -> float:
        """
        Specialized scoring for intervention (Category B) questions.
        """
        score = 0.0
        
        # Basic: Has prediction response (fallback works)
        if 'prediction' in response or 'cumulative_prediction' in response:
            score += 0.2
        
        # Enhanced: Has shock magnitude acknowledgment
        shock_keys = ['shock_magnitude', 'intervention_delta', 'delta', 'intervention']
        if any(k in str(response).lower() for k in shock_keys):
            score += 0.15
        
        # Good: Has propagation information
        propagation_keys = [
            'propagation_path', 'propagation_chain', 'affected_nodes',
            'downstream_impact', 'spillover'
        ]
        if any(k in response for k in propagation_keys):
            score += 0.25
            
            # Bonus: Has hop-by-hop breakdown
            if 'hop' in str(response).lower() or 'propagation_path' in response:
                score += 0.1
        
        # Very good: Has quantified effects per node
        if 'affected_nodes' in response or 'impacts' in response:
            score += 0.15
            
            # Bonus: Has second-order effects
            if 'second_order' in str(response).lower() or 'second_order_effects' in response:
                score += 0.05
        
        # Excellent: Has systemic risk or temporal analysis
        if any(k in response for k in ['systemic_risk', 'temporal_decay', 'sentiment_decay']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_confidence(
        self,
        response: Dict,
        question: Dict,
        criteria: Dict
    ) -> float:
        """
        Score confidence calibration.
        
        Scoring:
        - 0.0-0.3: Binary prediction only
        - 0.3-0.6: Probability provided
        - 0.6-0.8: Feature-level confidence
        - 0.8-1.0: Robustness analysis, confidence intervals
        """
        score = 0.0
        
        # Basic: Has probability_up
        if 'probability_up' in response:
            score += 0.3
            
            # Validate probability is reasonable
            prob = response['probability_up']
            if isinstance(prob, (int, float)) and 0 <= prob <= 1:
                score += 0.1
        
        # Enhanced: Has feature-level confidence
        if 'features' in response:
            features = response['features']
            if features:
                # Check for per-feature confidence
                has_feature_conf = any(
                    k in str(f) for f in features for k in ['confidence', 'reliability', 'stability']
                )
                if has_feature_conf:
                    score += 0.15
                
                # Check for feature importance ranking
                has_ranking = any(
                    k in str(f) for f in features for k in ['rank', 'importance', 'weight']
                )
                if has_ranking:
                    score += 0.1
        
        # Advanced: Has robustness analysis
        robustness_keys = ['robustness', 'sensitivity', 'confidence_interval', 'stability']
        if any(k in str(response).lower() for k in robustness_keys):
            score += 0.15
            
            # Bonus: Has regime-dependent confidence
            if any(k in str(response).lower() for k in ['regime', 'bull', 'bear', 'volatile']):
                score += 0.1
        
        return min(score, 1.0)
    
    def _score_accuracy(
        self,
        response: Dict,
        question: Dict,
        ground_truth: Optional[Dict]
    ) -> float:
        """
        Score accuracy - requires ground truth or uses prediction quality heuristics.
        
        Without ground truth:
        - 0.5: Neutral (no info)
        - 0.6-0.7: High confidence prediction (self-reported)
        - 0.8+: Very specific prediction with magnitude
        
        With ground truth:
        - Compare predicted direction vs actual
        """
        if ground_truth is None:
            # Heuristic scoring without ground truth
            score = 0.5  # Neutral baseline
            
            # Boost if prediction is specific
            if 'cumulative_prediction' in response:
                pred = response['cumulative_prediction']
                if isinstance(pred, (int, float)) and pred != 0:
                    score += 0.1
            
            # Boost if probability is well-calibrated
            if 'probability_up' in response:
                prob = response['probability_up']
                if isinstance(prob, (int, float)):
                    # Well-calibrated if not extreme 0 or 1
                    if 0.3 <= prob <= 0.7:
                        score += 0.1
                    elif prob > 0.8 or prob < 0.2:
                        score += 0.05  # Strong directional confidence
            
            return min(score, 0.9)  # Cap at 0.9 without ground truth
        
        # With ground truth: calculate actual accuracy
        predicted_direction = None
        if 'probability_up' in response:
            predicted_direction = 'up' if response['probability_up'] > 0.5 else 'down'
        elif 'prediction' in response:
            predicted_direction = 'up' if response['prediction'] > 0 else 'down'
        
        actual_direction = ground_truth.get('direction', ground_truth.get('actual_movement'))
        
        if predicted_direction and actual_direction:
            return 1.0 if predicted_direction == actual_direction else 0.0
        
        return 0.5
    
    def get_scoring_report(self) -> Dict[str, Any]:
        """Generate detailed scoring report."""
        if not self.scoring_log:
            return {}
        
        by_category = {}
        for entry in self.scoring_log:
            cat = entry['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(entry)
        
        report = {
            'total_questions_scored': len(self.scoring_log),
            'by_category': {},
            'overall_average': sum(e['total'] for e in self.scoring_log) / len(self.scoring_log)
        }
        
        for cat, entries in by_category.items():
            report['by_category'][cat] = {
                'count': len(entries),
                'average_total': sum(e['total'] for e in entries) / len(entries),
                'average_explainability': sum(e['explainability'] for e in entries) / len(entries),
                'average_intervenability': sum(e['intervenability'] for e in entries) / len(entries),
                'average_confidence': sum(e['confidence'] for e in entries) / len(entries),
                'average_accuracy': sum(e['accuracy'] for e in entries) / len(entries)
            }
        
        return report


# Convenience function
def calculate_cevs(
    response: Dict[str, Any],
    question: Dict[str, Any],
    ground_truth: Optional[Dict] = None
) -> CEVSComponents:
    """
    Convenience function for calculating CEVS.
    
    Example:
        cevs = calculate_cevs(
            response={'prediction': 0.05, 'probability_up': 0.65, ...},
            question={'id': 'A1', 'category': 'A', ...}
        )
        print(f"Total CEVS: {cevs.total:.3f}")
    """
    scorer = EnhancedCEVSScorer()
    return scorer.calculate_cevs(response, question, ground_truth)


if __name__ == "__main__":
    # Test with sample data
    test_response = {
        'prediction': 0.035,
        'probability_up': 0.68,
        'features': [
            {'feature': 'ETHUSD', 'cumulative_impact': 0.02, 'tau': 2},
            {'feature': 'BTC_momentum', 'cumulative_impact': 0.015, 'tau': 1}
        ],
        'parents': ['ETHUSD', 'SPY', 'VIX']
    }
    
    test_question = {
        'id': 'A1',
        'category': 'A',
        'question': 'Will BTCUSD go up in the next 5 hours?'
    }
    
    cevs = calculate_cevs(test_response, test_question)
    print(f"Explainability: {cevs.explainability:.3f}")
    print(f"Intervenability: {cevs.intervenability:.3f}")
    print(f"Confidence: {cevs.confidence_calibration:.3f}")
    print(f"Accuracy: {cevs.accuracy:.3f}")
    print(f"Total CEVS: {cevs.total:.3f}")
