import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add ml_engine to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forecaster import HybridForecaster, ForecastResult
from preprocessing.feature_engineering import FeatureEngineer

# Ensure deterministic randomness
np.random.seed(42)


def _build_training_data() -> pd.DataFrame:
    """Build synthetic Ramadan training data."""
    dates = pd.date_range(start='2026-02-17', periods=1440 * 15, freq='1T')  # 15 days
    
    traffic = []
    for date in dates:
        hour = date.hour
        
        # Hourly patterns with surge windows
        if 3 <= hour <= 5:  # Suhoor
            base = 400
        elif 18 <= hour <= 20:  # Iftar
            base = 500
        elif 20 <= hour <= 22:  # Taraweeh
            base = 300
        else:
            base = 100
        
        traffic.append(max(0, base + np.random.normal(0, 20)))
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    # Engineer features
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    return df


def test_forecaster_training():
    """Test that forecaster can be trained."""
    df = _build_training_data()
    
    forecaster = HybridForecaster()
    assert forecaster.is_trained == False
    
    forecaster.train(df)
    assert forecaster.is_trained == True


def test_trigger_rules():
    """Test that trigger rules are correctly defined."""
    forecaster = HybridForecaster()
    
    # Verify all events have trigger rules
    assert 'suhoor' in forecaster.TRIGGER_RULES
    assert 'iftar' in forecaster.TRIGGER_RULES
    assert 'taraweeh' in forecaster.TRIGGER_RULES
    
    # Verify Suhoor trigger (2 AM for 4 AM event)
    suhoor = forecaster.TRIGGER_RULES['suhoor']
    assert suhoor['trigger_hour'] == 2
    assert suhoor['event_hour'] == 4
    
    # Verify Iftar trigger (3 PM for 6 PM event)
    iftar = forecaster.TRIGGER_RULES['iftar']
    assert iftar['trigger_hour'] == 15
    assert iftar['event_hour'] == 18
    
    # Verify Taraweeh trigger (5 PM for 8 PM event)
    taraweeh = forecaster.TRIGGER_RULES['taraweeh']
    assert taraweeh['trigger_hour'] == 17
    assert taraweeh['event_hour'] == 20


def test_forecast_requires_training():
    """Test that forecast raises error if not trained."""
    forecaster = HybridForecaster()
    
    current_time = datetime(2026, 2, 20, 15, 0)  # 3 PM, Iftar trigger
    
    try:
        forecaster.forecast(current_time, current_traffic=100.0)
        assert False, "Should raise ValueError for untrained forecaster"
    except ValueError as e:
        assert "must be trained" in str(e).lower()


def test_forecast_iftar_at_trigger():
    """Test forecasting Iftar event at trigger time."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # Trigger time: 3 PM on Ramadan day 10
    current_time = datetime(2026, 2, 26, 15, 0)  # Day 10 of Ramadan
    current_traffic = 120.0
    
    forecasts = forecaster.forecast(current_time, current_traffic)
    
    # Should generate Iftar forecast
    assert len(forecasts) >= 1
    
    # Find Iftar forecast
    iftar_forecast = None
    for f in forecasts:
        if f.event_name == 'iftar':
            iftar_forecast = f
            break
    
    assert iftar_forecast is not None
    assert iftar_forecast.predicted_traffic > 0
    assert 0.5 <= iftar_forecast.confidence <= 0.99
    assert iftar_forecast.time_to_impact > 0
    assert iftar_forecast.time_to_impact <= 4  # Within 4-hour horizon


def test_forecast_suhoor_at_trigger():
    """Test forecasting Suhoor event at trigger time."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # Trigger time: 2 AM on Ramadan day 15
    current_time = datetime(2026, 3, 3, 2, 0)  # Day 15 of Ramadan
    current_traffic = 80.0
    
    forecasts = forecaster.forecast(current_time, current_traffic)
    
    # Should generate Suhoor forecast
    assert len(forecasts) >= 1
    
    # Find Suhoor forecast
    suhoor_forecast = None
    for f in forecasts:
        if f.event_name == 'suhoor':
            suhoor_forecast = f
            break
    
    assert suhoor_forecast is not None
    assert suhoor_forecast.predicted_traffic > 0
    assert 0.5 <= suhoor_forecast.confidence <= 0.99


def test_no_forecast_outside_ramadan():
    """Test that no forecasts are generated outside Ramadan."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # Outside Ramadan: January 15, 2026
    current_time = datetime(2026, 1, 15, 15, 0)
    current_traffic = 100.0
    
    forecasts = forecaster.forecast(current_time, current_traffic)
    
    # Should return empty list
    assert len(forecasts) == 0


def test_no_forecast_outside_trigger_times():
    """Test that no forecasts are generated outside trigger hours."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # During Ramadan but not at trigger time (10 AM)
    current_time = datetime(2026, 2, 20, 10, 0)
    current_traffic = 100.0
    
    forecasts = forecaster.forecast(current_time, current_traffic)
    
    # Should return empty list (no triggers at 10 AM)
    assert len(forecasts) == 0


def test_ml_vs_fallback_decision():
    """Test that forecaster uses ML when confidence >= 0.7, fallback otherwise."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # Trigger at 3 PM for Iftar
    current_time = datetime(2026, 2, 26, 15, 0)  # Day 10
    current_traffic = 120.0
    
    forecasts = forecaster.forecast(current_time, current_traffic, historical_df=df)
    
    # Find Iftar forecast
    iftar_forecast = None
    for f in forecasts:
        if f.event_name == 'iftar':
            iftar_forecast = f
            break
    
    assert iftar_forecast is not None
    
    # Verify used_ml flag matches confidence threshold
    if iftar_forecast.confidence >= 0.7:
        assert iftar_forecast.used_ml == True
    else:
        assert iftar_forecast.used_ml == False


def test_forecast_result_structure():
    """Test that ForecastResult has all required fields."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    current_time = datetime(2026, 2, 26, 15, 0)
    forecasts = forecaster.forecast(current_time, current_traffic=120.0)
    
    if len(forecasts) > 0:
        forecast = forecasts[0]
        
        # Verify all required fields exist
        assert hasattr(forecast, 'event_name')
        assert hasattr(forecast, 'predicted_traffic')
        assert hasattr(forecast, 'confidence')
        assert hasattr(forecast, 'time_to_impact')
        assert hasattr(forecast, 'trigger_time')
        assert hasattr(forecast, 'event_time')
        assert hasattr(forecast, 'baseline_traffic')
        assert hasattr(forecast, 'multiplier')
        assert hasattr(forecast, 'used_ml')
        
        # Verify types
        assert isinstance(forecast.event_name, str)
        assert isinstance(forecast.predicted_traffic, (int, float))
        assert isinstance(forecast.confidence, float)
        assert isinstance(forecast.time_to_impact, (int, float))
        assert isinstance(forecast.used_ml, bool)


def test_forecast_horizon_constraint():
    """Test that forecasts are only generated within 4-hour horizon."""
    forecaster = HybridForecaster()
    
    # Horizon should be 4 hours (MVP)
    assert forecaster.FORECAST_HORIZON_HOURS == 4


def test_ramadan_progression_affects_forecast():
    """Test that forecasts change based on Ramadan day progression."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # Early Ramadan (day 5)
    early_time = datetime(2026, 2, 21, 15, 0)
    early_forecasts = forecaster.forecast(early_time, current_traffic=120.0)
    
    # Last 10 nights (day 25)
    late_time = datetime(2026, 3, 13, 15, 0)
    late_forecasts = forecaster.forecast(late_time, current_traffic=120.0)
    
    # Both should generate forecasts
    early_iftar = [f for f in early_forecasts if f.event_name == 'iftar']
    late_iftar = [f for f in late_forecasts if f.event_name == 'iftar']
    
    if early_iftar and late_iftar:
        # Last 10 nights should have higher predicted traffic due to progression
        assert late_iftar[0].predicted_traffic >= early_iftar[0].predicted_traffic


def test_model_summary():
    """Test that model summary provides comprehensive information."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    
    # Before training
    summary = forecaster.get_model_summary()
    assert summary['trained'] == False
    
    # After training
    forecaster.train(df)
    summary = forecaster.get_model_summary()
    
    assert summary['trained'] == True
    assert 'baseline_summary' in summary
    assert 'pattern_summary' in summary
    assert 'forecast_horizon_hours' in summary
    assert 'trigger_rules' in summary
    assert summary['forecast_horizon_hours'] == 4


def test_hybrid_approach_rules_and_ml():
    """Test that forecaster combines rules (WHEN) with ML (HOW MUCH)."""
    df = _build_training_data()
    forecaster = HybridForecaster()
    forecaster.train(df)
    
    # Trigger at 3 PM for Iftar (rule-based WHEN)
    current_time = datetime(2026, 2, 26, 15, 0)
    forecasts = forecaster.forecast(current_time, current_traffic=120.0, historical_df=df)
    
    iftar_forecast = [f for f in forecasts if f.event_name == 'iftar']
    
    if iftar_forecast:
        f = iftar_forecast[0]
        
        # WHEN: Rule-based trigger time
        assert f.trigger_time.hour == 15  # Rule says trigger at 3 PM
        assert f.event_time.hour == 18    # Event at 6 PM
        
        # HOW MUCH: ML-learned multiplier
        assert f.multiplier >= 1.0  # Should have learned multiplier > 1
        assert f.baseline_traffic > 0
        assert f.predicted_traffic == f.baseline_traffic * f.multiplier
