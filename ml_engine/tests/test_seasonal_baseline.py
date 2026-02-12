import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.seasonal_baseline import SeasonalBaselineModel
from preprocessing.feature_engineering import FeatureEngineer


def test_seasonal_baseline_training():
    """Test that the model can be trained on Ramadan data."""
    dates = pd.date_range(start='2026-03-01', periods=1440*7, freq='1T')
    
    # Generate synthetic Ramadan traffic with patterns
    traffic = []
    for date in dates:
        hour = date.hour
        if 3 <= hour <= 5:  # Suhoor
            base = 400
        elif 18 <= hour <= 20:  # Iftar
            base = 500
        else:
            base = 100
        
        traffic.append(base + np.random.normal(0, 10))
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    # Add features needed for training
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    # Train model
    model = SeasonalBaselineModel()
    model.train(df)
    
    assert model.is_trained
    assert len(model.patterns) == 24  # All 24 hours
    print("✅ Model trains successfully on Ramadan data")


def test_seasonal_baseline_prediction():
    """Test that the model can make predictions."""
    dates = pd.date_range(start='2026-03-01', periods=1440*7, freq='1T')
    
    traffic = []
    for date in dates:
        hour = date.hour
        if 3 <= hour <= 5:
            base = 400
        elif 18 <= hour <= 20:
            base = 500
        else:
            base = 100
        traffic.append(base + np.random.normal(0, 10))
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    model = SeasonalBaselineModel()
    model.train(df)
    
    # Test prediction for suhoor time
    test_time = datetime(2026, 3, 8, 4, 0)
    prediction = model.predict(test_time, baseline_traffic=100)
    
    assert prediction > 100  # Should predict higher traffic during suhoor
    print(f"✅ Suhoor prediction: {prediction:.1f} (baseline: 100)")
    
    # Test prediction for iftar time
    test_time_iftar = datetime(2026, 3, 8, 19, 0)
    prediction_iftar = model.predict(test_time_iftar, baseline_traffic=100)
    
    assert prediction_iftar > 100  # Should predict higher traffic during iftar
    print(f"✅ Iftar prediction: {prediction_iftar:.1f} (baseline: 100)")


def test_seasonal_baseline_multipliers():
    """Test that multipliers are calculated correctly."""
    dates = pd.date_range(start='2026-03-01', periods=1440*7, freq='1T')
    
    traffic = []
    for date in dates:
        hour = date.hour
        if 3 <= hour <= 5:
            base = 400
        elif 18 <= hour <= 20:
            base = 500
        else:
            base = 100
        traffic.append(base + np.random.normal(0, 10))
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    model = SeasonalBaselineModel()
    model.train(df)
    
    # Suhoor hours should have high multiplier
    suhoor_multiplier = model.get_multiplier(4)
    assert suhoor_multiplier > 1.0
    print(f"✅ Suhoor multiplier: {suhoor_multiplier:.2f}x")
    
    # Iftar hours should have high multiplier
    iftar_multiplier = model.get_multiplier(19)
    assert iftar_multiplier > 1.0
    print(f"✅ Iftar multiplier: {iftar_multiplier:.2f}x")
    
    # Midday should have lower multiplier
    midday_multiplier = model.get_multiplier(12)
    assert midday_multiplier < suhoor_multiplier
    print(f"✅ Midday multiplier: {midday_multiplier:.2f}x")


def test_seasonal_baseline_confidence():
    """Test confidence scoring."""
    dates = pd.date_range(start='2026-03-01', periods=1440*7, freq='1T')
    
    traffic = []
    for date in dates:
        hour = date.hour
        base = 100 + hour * 10  # Predictable pattern
        traffic.append(base + np.random.normal(0, 5))  # Low variance
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    model = SeasonalBaselineModel()
    model.train(df)
    
    # Confidence should be high for predictable patterns
    confidence = model.get_confidence(12)
    assert 0.5 <= confidence <= 0.99
    print(f"✅ Confidence score: {confidence:.2%}")


def test_seasonal_baseline_summary():
    """Test pattern summary generation."""
    dates = pd.date_range(start='2026-03-01', periods=1440*7, freq='1T')
    
    traffic = []
    for date in dates:
        hour = date.hour
        if 3 <= hour <= 5:
            base = 400
        elif 18 <= hour <= 20:
            base = 500
        else:
            base = 100
        traffic.append(base + np.random.normal(0, 10))
    
    df = pd.DataFrame({'value': traffic}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    model = SeasonalBaselineModel()
    model.train(df)
    
    summary = model.get_pattern_summary()
    
    assert 'hours_covered' in summary
    assert 'peak_hours' in summary
    assert 'avg_confidence' in summary
    assert 'total_samples' in summary
    
    assert summary['hours_covered'] == 24
    assert len(summary['peak_hours']) == 5
    
    print("✅ Pattern summary:")
    print(f"   Hours covered: {summary['hours_covered']}")
    print(f"   Peak hours: {summary['peak_hours']}")
    print(f"   Avg confidence: {summary['avg_confidence']:.2%}")
    print(f"   Total samples: {summary['total_samples']}")


def test_no_ramadan_data_error():
    """Test that training fails gracefully without Ramadan data."""
    dates = pd.date_range(start='2026-01-01', periods=1440, freq='1T')
    df = pd.DataFrame({'value': range(1440)}, index=dates)
    
    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_ramadan_features(df, year=2026)
    
    model = SeasonalBaselineModel()
    
    try:
        model.train(df)
        assert False, "Should raise ValueError for no Ramadan data"
    except ValueError as e:
        assert "No Ramadan data" in str(e)
        print("✅ Raises clear error when no Ramadan data available")


if __name__ == "__main__":
    test_seasonal_baseline_training()
    test_seasonal_baseline_prediction()
    test_seasonal_baseline_multipliers()
    test_seasonal_baseline_confidence()
    test_seasonal_baseline_summary()
    test_no_ramadan_data_error()
    print("\n✅ All seasonal baseline tests passed")
