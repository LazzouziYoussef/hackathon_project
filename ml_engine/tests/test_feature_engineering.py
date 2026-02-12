import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.feature_engineering import FeatureEngineer


def test_time_features():
    dates = pd.date_range(start='2026-03-01 10:30:00', periods=100, freq='1T')
    df = pd.DataFrame({'value': range(100)}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_time_features(df)
    
    assert 'hour' in df_features.columns
    assert 'day_of_week' in df_features.columns
    assert 'day_of_month' in df_features.columns
    assert 'is_weekend' in df_features.columns
    
    assert df_features['hour'].iloc[0] == 10
    assert df_features['day_of_month'].iloc[0] == 1
    print("✅ Time features extracted correctly")


def test_ramadan_features():
    dates = pd.date_range(start='2026-03-01', periods=1440, freq='1T')
    df = pd.DataFrame({'value': range(1440)}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_ramadan_features(df, year=2026)
    
    assert 'is_ramadan' in df_features.columns
    assert 'ramadan_day' in df_features.columns
    assert 'is_last_10_nights' in df_features.columns
    
    assert df_features['is_ramadan'].iloc[0] == 1
    assert df_features['ramadan_day'].iloc[0] == 13
    assert df_features['is_last_10_nights'].iloc[0] == 0
    print("✅ Ramadan features extracted correctly")


def test_prayer_window_features():
    dates = pd.date_range(start='2026-03-01', periods=1440*2, freq='1T')
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_prayer_window_features(df)
    
    assert 'is_suhoor_window' in df_features.columns
    assert 'is_iftar_window' in df_features.columns
    assert 'is_taraweeh_window' in df_features.columns
    
    suhoor_times = df_features[(df_features.index.hour >= 3) & (df_features.index.hour <= 5)]
    assert suhoor_times['is_suhoor_window'].all() == 1
    
    iftar_times = df_features[(df_features.index.hour >= 18) & (df_features.index.hour <= 20)]
    assert iftar_times['is_iftar_window'].all() == 1
    
    print("✅ Prayer window features extracted correctly")


def test_lag_features():
    dates = pd.date_range(start='2026-03-01', periods=10080*2, freq='1T')
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_lag_features(df)
    
    assert 'traffic_lag_1h' in df_features.columns
    assert 'traffic_lag_24h' in df_features.columns
    assert 'traffic_lag_7d' in df_features.columns
    
    assert pd.isna(df_features['traffic_lag_1h'].iloc[0])
    assert df_features['traffic_lag_1h'].iloc[60] == 0
    
    assert df_features['traffic_lag_24h'].iloc[1440] == 0
    print("✅ Lag features extracted correctly")


def test_rolling_features():
    dates = pd.date_range(start='2026-03-01', periods=2000, freq='1T')
    values = [100 + np.sin(i / 60) * 20 for i in range(len(dates))]
    df = pd.DataFrame({'value': values}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_rolling_features(df)
    
    assert 'traffic_rolling_mean_1h' in df_features.columns
    assert 'traffic_rolling_std_1h' in df_features.columns
    assert 'traffic_rolling_max_1h' in df_features.columns
    assert 'traffic_rolling_min_1h' in df_features.columns
    assert 'traffic_rolling_mean_24h' in df_features.columns
    
    assert not pd.isna(df_features['traffic_rolling_mean_1h'].iloc[0])
    assert df_features['traffic_rolling_mean_1h'].iloc[100] > 0
    print("✅ Rolling features extracted correctly")


def test_engineer_all_features():
    dates = pd.date_range(start='2026-03-01', periods=10080*2, freq='1T')
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.engineer_all_features(df, year=2026)
    
    expected_cols = [
        'hour', 'day_of_week', 'is_ramadan', 'ramadan_day',
        'is_suhoor_window', 'is_iftar_window', 'is_taraweeh_window',
        'traffic_lag_1h', 'traffic_rolling_mean_1h'
    ]
    
    for col in expected_cols:
        assert col in df_features.columns, f"Missing column: {col}"
    
    print(f"✅ Feature engineering created {len(df_features.columns)} features")
    print(f"✅ All expected features present")


if __name__ == "__main__":
    test_time_features()
    test_ramadan_features()
    test_prayer_window_features()
    test_lag_features()
    test_rolling_features()
    test_engineer_all_features()
    print("\n✅ All feature engineering tests passed")
