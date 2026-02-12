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


def test_time_features_empty_dataframe():
    dates = pd.to_datetime([])
    df = pd.DataFrame({'value': []}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_time_features(df)
    
    assert df_features.shape[0] == 0
    for col in ['hour', 'day_of_week', 'day_of_month', 'is_weekend']:
        assert col in df_features.columns
    print("✅ Empty DataFrame handled correctly")


def test_time_features_non_datetime_index():
    df = pd.DataFrame({'value': range(10)})
    
    engineer = FeatureEngineer()
    
    try:
        engineer.add_time_features(df)
        assert False, "Should raise TypeError for non-datetime index"
    except TypeError as e:
        assert "DatetimeIndex" in str(e)
        print("✅ Non-datetime index raises clear error")


def test_ramadan_features():
    dates = [
        pd.Timestamp('2026-02-16 12:00:00'),  # Before Ramadan
        pd.Timestamp('2026-03-01 00:00:00'),  # Day 13
        pd.Timestamp('2026-03-08 12:00:00'),  # Day 20
        pd.Timestamp('2026-03-09 00:00:00'),  # Day 21 (first of last 10)
        pd.Timestamp('2026-03-19 12:00:00'),  # After Ramadan
    ]
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_ramadan_features(df, year=2026)
    
    assert 'is_ramadan' in df_features.columns
    assert 'ramadan_day' in df_features.columns
    assert 'is_last_10_nights' in df_features.columns
    
    # Before Ramadan
    before = df_features.loc[pd.Timestamp('2026-02-16 12:00:00')]
    assert before['is_ramadan'] == 0
    assert before['ramadan_day'] == 0
    assert before['is_last_10_nights'] == 0
    
    # Mid-Ramadan (day 13)
    mid = df_features.loc[pd.Timestamp('2026-03-01 00:00:00')]
    assert mid['is_ramadan'] == 1
    assert mid['ramadan_day'] == 13
    assert mid['is_last_10_nights'] == 0
    
    # Day 20 boundary
    day20 = df_features.loc[pd.Timestamp('2026-03-08 12:00:00')]
    assert day20['is_ramadan'] == 1
    assert day20['ramadan_day'] == 20
    assert day20['is_last_10_nights'] == 0
    
    # Day 21 (first of last 10 nights)
    day21 = df_features.loc[pd.Timestamp('2026-03-09 00:00:00')]
    assert day21['is_ramadan'] == 1
    assert day21['ramadan_day'] == 21
    assert day21['is_last_10_nights'] == 1
    
    # After Ramadan
    after = df_features.loc[pd.Timestamp('2026-03-19 12:00:00')]
    assert after['is_ramadan'] == 0
    assert after['ramadan_day'] == 0
    assert after['is_last_10_nights'] == 0
    
    print("✅ Ramadan features with boundaries work correctly")


def test_prayer_window_features():
    dates = pd.date_range(start='2026-03-01', periods=1440*2, freq='1T')
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_prayer_window_features(df)
    
    assert 'is_suhoor_window' in df_features.columns
    assert 'is_iftar_window' in df_features.columns
    assert 'is_taraweeh_window' in df_features.columns
    
    # Suhoor boundaries (3:00-5:59)
    assert df_features.loc[pd.Timestamp('2026-03-01 02:59:00'), 'is_suhoor_window'] == 0
    assert df_features.loc[pd.Timestamp('2026-03-01 03:00:00'), 'is_suhoor_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 05:00:00'), 'is_suhoor_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 05:59:00'), 'is_suhoor_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 06:00:00'), 'is_suhoor_window'] == 0
    
    # Iftar boundaries (18:00-20:59)
    assert df_features.loc[pd.Timestamp('2026-03-01 17:59:00'), 'is_iftar_window'] == 0
    assert df_features.loc[pd.Timestamp('2026-03-01 18:00:00'), 'is_iftar_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 20:00:00'), 'is_iftar_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 20:59:00'), 'is_iftar_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 21:00:00'), 'is_iftar_window'] == 0
    
    # Taraweeh boundaries (20:00-22:59)
    assert df_features.loc[pd.Timestamp('2026-03-01 19:59:00'), 'is_taraweeh_window'] == 0
    assert df_features.loc[pd.Timestamp('2026-03-01 20:00:00'), 'is_taraweeh_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 22:00:00'), 'is_taraweeh_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 22:59:00'), 'is_taraweeh_window'] == 1
    assert df_features.loc[pd.Timestamp('2026-03-01 23:00:00'), 'is_taraweeh_window'] == 0
    
    # Midday should have all zeros
    midday = pd.Timestamp('2026-03-01 12:00:00')
    assert df_features.loc[midday, 'is_suhoor_window'] == 0
    assert df_features.loc[midday, 'is_iftar_window'] == 0
    assert df_features.loc[midday, 'is_taraweeh_window'] == 0
    
    print("✅ Prayer window features with boundaries work correctly")


def test_lag_features():
    dates = pd.date_range(start='2026-03-01', periods=10080*2, freq='1T')
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_lag_features(df, freq_minutes=1)
    
    assert 'traffic_lag_1h' in df_features.columns
    assert 'traffic_lag_24h' in df_features.columns
    assert 'traffic_lag_7d' in df_features.columns
    
    lag_1h = df_features['traffic_lag_1h']
    lag_24h = df_features['traffic_lag_24h']
    lag_7d = df_features['traffic_lag_7d']
    
    # 1h lag (60 minutes)
    assert pd.isna(lag_1h.iloc[0])
    assert pd.isna(lag_1h.iloc[59])
    assert lag_1h.iloc[60] == 0
    assert lag_1h.iloc[61] == 1
    
    # 24h lag (1440 minutes)
    assert pd.isna(lag_24h.iloc[0])
    assert pd.isna(lag_24h.iloc[1439])
    assert lag_24h.iloc[1440] == 0
    assert lag_24h.iloc[1441] == 1
    
    # 7d lag (10080 minutes)
    assert lag_7d.iloc[:10080].isna().all()
    assert pd.isna(lag_7d.iloc[10079])
    assert lag_7d.iloc[10080] == 0
    assert lag_7d.iloc[10081] == 1
    
    print("✅ Lag features with all boundaries work correctly")


def test_rolling_features():
    dates = pd.date_range(start='2026-03-01', periods=2000, freq='1T')
    values = list(range(len(dates)))
    df = pd.DataFrame({'value': values}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_rolling_features(df, freq_minutes=1)
    
    assert 'traffic_rolling_mean_1h' in df_features.columns
    assert 'traffic_rolling_std_1h' in df_features.columns
    assert 'traffic_rolling_max_1h' in df_features.columns
    assert 'traffic_rolling_min_1h' in df_features.columns
    assert 'traffic_rolling_mean_24h' in df_features.columns
    
    mean_1h = df_features['traffic_rolling_mean_1h']
    std_1h = df_features['traffic_rolling_std_1h']
    mean_24h = df_features['traffic_rolling_mean_24h']
    
    # At index 0, single value
    assert mean_1h.iloc[0] == 0.0
    
    # At index 59, values 0..59
    assert np.isclose(mean_1h.iloc[59], 29.5)
    
    # At index 60, window values 1..60
    assert np.isclose(mean_1h.iloc[60], 30.5)
    
    # Std at index 0 (single value)
    assert pd.isna(std_1h.iloc[0])
    
    # Std at index 60
    expected_std_60 = np.std(np.arange(1, 61), ddof=1)
    assert np.isclose(std_1h.iloc[60], expected_std_60)
    
    # 24h rolling mean at index 1440
    expected_mean_24h_1440 = np.mean(np.arange(1, 1441))
    assert np.isclose(mean_24h.iloc[1440], expected_mean_24h_1440)
    
    print("✅ Rolling features with precise calculations work correctly")


def test_engineer_all_features():
    dates = pd.date_range(start='2026-03-01', periods=10080*2, freq='1T')
    df = pd.DataFrame({'value': range(len(dates))}, index=dates)
    
    engineer = FeatureEngineer()
    df_features = engineer.engineer_all_features(df, year=2026, drop_na=True, freq_minutes=1)
    
    expected_cols = [
        'hour', 'day_of_week', 'is_ramadan', 'ramadan_day',
        'is_suhoor_window', 'is_iftar_window', 'is_taraweeh_window',
        'traffic_lag_1h', 'traffic_lag_24h', 'traffic_lag_7d',
        'traffic_rolling_mean_1h'
    ]
    
    for col in expected_cols:
        assert col in df_features.columns, f"Missing column: {col}"
    
    # Verify dropna reduced rows and no NaNs remain
    assert len(df_features) < len(df)
    assert not df_features.isna().any().any()
    
    # Verify lag integrity for a sample timestamp
    sample_ts = df_features.index[len(df_features) // 2]
    lag_source_ts = sample_ts - pd.Timedelta(hours=1)
    assert df_features.loc[sample_ts, 'traffic_lag_1h'] == df.loc[lag_source_ts, 'value']
    
    # Verify rolling mean integrity
    window = df.loc[sample_ts - pd.Timedelta(minutes=59): sample_ts, 'value']
    expected_mean = window.mean()
    assert np.isclose(df_features.loc[sample_ts, 'traffic_rolling_mean_1h'], expected_mean)
    
    # Verify Ramadan features
    ramadan_rows = df_features[df_features['is_ramadan'] == 1]
    if len(ramadan_rows) > 0:
        assert (ramadan_rows['ramadan_day'] >= 1).all()
        assert (ramadan_rows['ramadan_day'] <= 30).all()
    
    print(f"✅ Feature engineering created {len(df_features.columns)} features")
    print(f"✅ All expected features present")
    print("✅ No NaNs remain and feature values are consistent")


if __name__ == "__main__":
    test_time_features()
    test_time_features_empty_dataframe()
    test_time_features_non_datetime_index()
    test_ramadan_features()
    test_prayer_window_features()
    test_lag_features()
    test_rolling_features()
    test_engineer_all_features()
    print("\n✅ All feature engineering tests passed")
