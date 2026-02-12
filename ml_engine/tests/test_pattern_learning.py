import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.pattern_learner import RamadanPatternLearner
from preprocessing.feature_engineering import FeatureEngineer

# Ensure deterministic randomness
np.random.seed(42)


def _build_ramadan_progression_df(minutes: int = 1440 * 30) -> pd.DataFrame:
    """Build synthetic Ramadan data with traffic progression over 30 days."""
    dates = pd.date_range(start='2026-02-17', periods=minutes, freq='1T')
    
    traffic = []
    for date in dates:
        hour = date.hour
        ramadan_day = (date - datetime(2026, 2, 17)).days + 1
        
        # Base traffic with daily progression
        if ramadan_day <= 10:
            day_factor = 1.0
        elif ramadan_day <= 20:
            day_factor = 1.1
        else:  # Last 10 nights
            day_factor = 1.3
        
        # Hourly patterns
        if 3 <= hour <= 5:  # Suhoor
            base = 400 * day_factor
        elif 18 <= hour <= 20:  # Iftar
            base = 500 * day_factor
        elif 20 <= hour <= 22:  # Taraweeh
            base = 300 * day_factor
        else:
            base = 100 * day_factor
        
        traffic.append(max(0, base + np.random.normal(0, 20)))
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    return df


def test_learn_surge_patterns():
    """Test learning surge patterns from historical data."""
    df = _build_ramadan_progression_df()
    
    learner = RamadanPatternLearner()
    learner.learn_surge_patterns(df)
    
    assert 'suhoor' in learner.surge_patterns
    assert 'iftar' in learner.surge_patterns
    assert 'taraweeh' in learner.surge_patterns
    
    # Check suhoor pattern
    suhoor = learner.surge_patterns['suhoor']
    assert suhoor['multiplier_mean'] > 1.0
    assert suhoor['confidence'] > 0.6
    assert suhoor['sample_size'] > 0
    
    # Check iftar pattern
    iftar = learner.surge_patterns['iftar']
    assert iftar['multiplier_mean'] > 1.0
    assert iftar['duration_minutes_mean'] > 0


def test_learn_daily_progression():
    """Test learning daily progression throughout Ramadan."""
    df = _build_ramadan_progression_df()
    
    learner = RamadanPatternLearner()
    learner.learn_daily_progression(df)
    
    assert len(learner.daily_patterns) > 0
    
    # Check that we have patterns for various days
    assert 1 in learner.daily_patterns
    assert 15 in learner.daily_patterns
    assert 25 in learner.daily_patterns
    
    # Check pattern structure
    day_1 = learner.daily_patterns[1]
    assert 'avg_traffic' in day_1
    assert 'peak_traffic' in day_1
    assert 'peak_hour' in day_1
    assert 'baseline_traffic' in day_1


def test_day_adjustment_factors():
    """Test that adjustment factors increase throughout Ramadan."""
    df = _build_ramadan_progression_df()
    
    learner = RamadanPatternLearner()
    learner.learn_daily_progression(df)
    
    early_factor = learner.get_day_adjustment_factor(5)
    mid_factor = learner.get_day_adjustment_factor(15)
    late_factor = learner.get_day_adjustment_factor(25)
    
    # Traffic should increase throughout Ramadan
    assert early_factor <= mid_factor
    assert mid_factor <= late_factor
    assert late_factor > 1.0


def test_pattern_summary():
    """Test pattern summary generation."""
    df = _build_ramadan_progression_df()
    
    learner = RamadanPatternLearner()
    learner.learn_surge_patterns(df)
    learner.learn_daily_progression(df)
    
    summary = learner.get_pattern_summary()
    
    assert 'surge_patterns' in summary
    assert 'daily_progression' in summary
    assert 'total_days_analyzed' in summary
    
    # Check daily progression structure
    progression = summary['daily_progression']
    assert 'early_ramadan' in progression
    assert 'mid_ramadan' in progression
    assert 'last_10_nights' in progression
    
    # Verify progression trend
    assert progression['last_10_nights'] > progression['early_ramadan']


def test_surge_multipliers_reasonable():
    """Test that learned multipliers are reasonable."""
    df = _build_ramadan_progression_df()
    
    learner = RamadanPatternLearner()
    learner.learn_surge_patterns(df)
    
    for event_name, pattern in learner.surge_patterns.items():
        # Multipliers should be reasonable (1.5x to 10x)
        assert 1.5 <= pattern['multiplier_mean'] <= 10.0
        
        # Duration should be reasonable (30-240 minutes)
        assert 30 <= pattern['duration_minutes_mean'] <= 240
        
        # Confidence should be valid
        assert 0.6 <= pattern['confidence'] <= 0.99


def test_empty_data_handling():
    """Test handling of data with no clear patterns."""
    # Create data with no Ramadan or very flat traffic
    dates = pd.date_range(start='2026-01-01', periods=1440, freq='1T')
    df = pd.DataFrame({'value': [100] * 1440}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    learner = RamadanPatternLearner()
    learner.learn_surge_patterns(df)
    learner.learn_daily_progression(df)
    
    # Should handle gracefully without crashing
    assert len(learner.surge_patterns) >= 0
    assert len(learner.daily_patterns) >= 0
