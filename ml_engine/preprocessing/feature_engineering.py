import pandas as pd
import numpy as np
from ml_engine.utils.time_utils import RamadanCalendar


class FeatureEngineer:
    def __init__(self):
        self.ramadan_calendar = RamadanCalendar()
    
    def add_time_features(self, df, datetime_col=None):
        df = df.copy()
        
        if datetime_col is not None:
            if datetime_col not in df.columns:
                raise ValueError(
                    f"datetime_col='{datetime_col}' is not present in the DataFrame columns."
                )
            dt_index = pd.to_datetime(df[datetime_col], errors="coerce")
            if dt_index.isna().any():
                raise ValueError(
                    f"Could not convert all values in '{datetime_col}' to datetime; "
                    "ensure it contains valid datetime values."
                )
        else:
            if not isinstance(df.index, pd.DatetimeIndex):
                raise TypeError(
                    "add_time_features expects a DatetimeIndex when 'datetime_col' is not provided. "
                    "Either set a DatetimeIndex on the DataFrame or pass a 'datetime_col' to derive "
                    "time features from."
                )
            dt_index = df.index
        
        df['hour'] = dt_index.hour
        df['day_of_week'] = dt_index.dayofweek
        df['day_of_month'] = dt_index.day
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    def add_ramadan_features(self, df, year=None):
        df = df.copy()
        
        if year is None:
            if not isinstance(df.index, pd.DatetimeIndex):
                raise TypeError(
                    "Cannot infer year from non-DatetimeIndex. "
                    "Please provide 'year' explicitly."
                )
            if len(df) == 0:
                year = 2026  # Default for empty DataFrame
            else:
                year = df.index[0].year
        
        df['is_ramadan'] = df.index.map(lambda x: self.ramadan_calendar.is_ramadan(x, year)).astype(int)
        df['ramadan_day'] = df.index.map(lambda x: self.ramadan_calendar.get_ramadan_day(x, year))
        df['ramadan_day'] = df['ramadan_day'].fillna(0).astype(int)
        
        df['is_last_10_nights'] = (df['ramadan_day'] >= 21).astype(int)
        
        return df
    
    def add_prayer_window_features(self, df):
        df = df.copy()
        
        # Extract hour if not already present
        if 'hour' not in df.columns:
            df['hour'] = df.index.hour
        
        df['is_suhoor_window'] = ((df['hour'] >= 3) & (df['hour'] <= 5)).astype(int)
        df['is_iftar_window'] = ((df['hour'] >= 18) & (df['hour'] <= 20)).astype(int)
        df['is_taraweeh_window'] = ((df['hour'] >= 20) & (df['hour'] <= 22)).astype(int)
        
        return df
    
    def add_lag_features(self, df, value_col='value', freq_minutes=1):
        """Add lag features.
        
        Args:
            df: DataFrame with datetime index
            value_col: Column to compute lags for
            freq_minutes: Data frequency in minutes (default 1 for minutely data)
        """
        df = df.copy()
        
        # Calculate shift periods based on frequency
        shift_1h = int(60 / freq_minutes)
        shift_24h = int(1440 / freq_minutes)
        shift_7d = int(10080 / freq_minutes)
        
        df['traffic_lag_1h'] = df[value_col].shift(shift_1h)
        df['traffic_lag_24h'] = df[value_col].shift(shift_24h)
        df['traffic_lag_7d'] = df[value_col].shift(shift_7d)
        
        return df
    
    def add_rolling_features(self, df, value_col='value', freq_minutes=1):
        """Add rolling window features.
        
        Args:
            df: DataFrame with datetime index
            value_col: Column to compute rolling features for
            freq_minutes: Data frequency in minutes (default 1 for minutely data)
        """
        df = df.copy()
        
        # Calculate window sizes based on frequency
        window_1h = int(60 / freq_minutes)
        window_24h = int(1440 / freq_minutes)
        
        df['traffic_rolling_mean_1h'] = df[value_col].rolling(window=window_1h, min_periods=1).mean()
        df['traffic_rolling_std_1h'] = df[value_col].rolling(window=window_1h, min_periods=1).std()
        df['traffic_rolling_max_1h'] = df[value_col].rolling(window=window_1h, min_periods=1).max()
        df['traffic_rolling_min_1h'] = df[value_col].rolling(window=window_1h, min_periods=1).min()
        
        df['traffic_rolling_mean_24h'] = df[value_col].rolling(window=window_24h, min_periods=1).mean()
        
        return df
    
    def engineer_all_features(self, df, year=None, drop_na=True, freq_minutes=1):
        """Engineer all features in the pipeline.
        
        Args:
            df: DataFrame with datetime index
            year: Year for Ramadan features (inferred from index if None)
            drop_na: Whether to drop rows with NaN values (default True)
            freq_minutes: Data frequency in minutes (default 1 for minutely data)
        """
        df = self.add_time_features(df)
        df = self.add_ramadan_features(df, year)
        df = self.add_prayer_window_features(df)
        df = self.add_lag_features(df, freq_minutes=freq_minutes)
        df = self.add_rolling_features(df, freq_minutes=freq_minutes)
        
        if drop_na:
            # Only drop rows where lag features are NaN (most restrictive)
            lag_cols = ['traffic_lag_1h', 'traffic_lag_24h', 'traffic_lag_7d']
            df = df.dropna(subset=lag_cols)
        
        return df
