import pandas as pd
import numpy as np
import sys
import os

# Add ml_engine to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.confidence_scorer import ConfidenceScorer

# Ensure deterministic randomness
np.random.seed(42)


def test_event_base_confidence():
    """Test that Iftar has higher base confidence than Suhoor."""
    scorer = ConfidenceScorer()
    
    # Same conditions, different events
    iftar_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=15,
        hour=18,
        sample_size=30
    )
    
    suhoor_conf = scorer.calculate_confidence(
        event_name='suhoor',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=15,
        hour=4,
        sample_size=30
    )
    
    # Iftar should have higher confidence than Suhoor
    assert iftar_conf > suhoor_conf
    
    # Both should be in valid range
    assert scorer.MIN_CONFIDENCE <= iftar_conf <= scorer.MAX_CONFIDENCE
    assert scorer.MIN_CONFIDENCE <= suhoor_conf <= scorer.MAX_CONFIDENCE


def test_ramadan_progression_boost():
    """Test that confidence increases throughout Ramadan."""
    scorer = ConfidenceScorer()
    
    # Early Ramadan
    early_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=5,
        hour=18,
        sample_size=30
    )
    
    # Mid Ramadan
    mid_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=15,
        hour=18,
        sample_size=30
    )
    
    # Last 10 nights
    late_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=25,
        hour=18,
        sample_size=30
    )
    
    # Confidence should increase throughout Ramadan
    assert early_conf <= mid_conf
    assert mid_conf <= late_conf


def test_data_quality_impact():
    """Test that data quality affects confidence."""
    scorer = ConfidenceScorer()
    
    # High data quality
    high_quality_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.95,
        ramadan_day=15,
        hour=18,
        sample_size=30
    )
    
    # Low data quality
    low_quality_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.6,
        ramadan_day=15,
        hour=18,
        sample_size=30
    )
    
    # Higher quality should yield higher confidence
    assert high_quality_conf > low_quality_conf


def test_confidence_bounds():
    """Test that confidence stays within MIN and MAX bounds."""
    scorer = ConfidenceScorer()
    
    # Try extreme values
    test_cases = [
        {'model_confidence': 0.0, 'data_quality': 0.0},
        {'model_confidence': 1.0, 'data_quality': 1.0},
        {'model_confidence': 0.5, 'data_quality': 0.5},
    ]
    
    for case in test_cases:
        conf = scorer.calculate_confidence(
            event_name='iftar',
            model_confidence=case['model_confidence'],
            data_quality=case['data_quality'],
            ramadan_day=15,
            hour=18,
            sample_size=30
        )
        
        assert scorer.MIN_CONFIDENCE <= conf <= scorer.MAX_CONFIDENCE


def test_data_quality_calculation():
    """Test data quality calculation from DataFrame."""
    scorer = ConfidenceScorer()
    
    # Perfect data
    perfect_df = pd.DataFrame({
        'value': [100, 200, 300],
        'hour': [1, 2, 3],
        'is_ramadan': [1, 1, 1]
    })
    perfect_quality = scorer.calculate_data_quality(perfect_df)
    assert perfect_quality == 1.0
    
    # Data with some missing values
    missing_df = pd.DataFrame({
        'value': [100, np.nan, 300],
        'hour': [1, 2, 3],
        'is_ramadan': [1, 1, 1]
    })
    missing_quality = scorer.calculate_data_quality(missing_df)
    assert 0.0 < missing_quality < 1.0
    
    # Empty data
    empty_df = pd.DataFrame()
    empty_quality = scorer.calculate_data_quality(empty_df)
    assert empty_quality == 0.0


def test_should_use_ml_threshold():
    """Test ML usage decision based on confidence threshold."""
    scorer = ConfidenceScorer()
    
    # Above threshold - use ML
    assert scorer.should_use_ml(0.75) == True
    assert scorer.should_use_ml(0.85) == True
    assert scorer.should_use_ml(0.95) == True
    
    # Below threshold - use fallback
    assert scorer.should_use_ml(0.65) == False
    assert scorer.should_use_ml(0.55) == False
    
    # Exactly at threshold - use ML
    assert scorer.should_use_ml(scorer.CONFIDENCE_THRESHOLD) == True


def test_confidence_level_labels():
    """Test human-readable confidence level labels."""
    scorer = ConfidenceScorer()
    
    assert scorer.get_confidence_level(0.95) == "very_high"
    assert scorer.get_confidence_level(0.85) == "high"
    assert scorer.get_confidence_level(0.75) == "medium"
    assert scorer.get_confidence_level(0.65) == "low"
    assert scorer.get_confidence_level(0.55) == "very_low"


def test_sample_size_impact():
    """Test that sample size affects confidence."""
    scorer = ConfidenceScorer()
    
    # Large sample
    large_sample_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=15,
        hour=18,
        sample_size=50
    )
    
    # Small sample
    small_sample_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=15,
        hour=18,
        sample_size=5
    )
    
    # Larger sample should yield higher confidence
    assert large_sample_conf >= small_sample_conf


def test_iftar_confidence_threshold():
    """Test that Iftar predictions typically exceed 0.85 confidence."""
    scorer = ConfidenceScorer()
    
    # Good conditions for Iftar
    iftar_conf = scorer.calculate_confidence(
        event_name='iftar',
        model_confidence=0.85,
        data_quality=0.95,
        ramadan_day=20,
        hour=18,
        sample_size=30
    )
    
    # Should exceed 0.85 for Iftar with good conditions
    assert iftar_conf >= 0.85


def test_non_ramadan_confidence_penalty():
    """Test that non-Ramadan periods have lower confidence."""
    scorer = ConfidenceScorer()
    
    # During Ramadan
    ramadan_conf = scorer.calculate_confidence(
        event_name='other',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=15,
        hour=12,
        sample_size=30
    )
    
    # Not during Ramadan
    non_ramadan_conf = scorer.calculate_confidence(
        event_name='other',
        model_confidence=0.8,
        data_quality=0.9,
        ramadan_day=None,
        hour=12,
        sample_size=30
    )
    
    # Ramadan should have higher confidence
    assert ramadan_conf > non_ramadan_conf
