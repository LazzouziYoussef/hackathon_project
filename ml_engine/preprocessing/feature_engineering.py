import pandas as pd
import numpy as np
from utils.time_utils import RamadanCalendar


class FeatureEngineer:
    def __init__(self):
        self.ramadan_calendar = RamadanCalendar()
    
    def add_time_features(self, df):
        df = df.copy()
        
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    def add_ramadan_features(self, df, year=2026):
        df = df.copy()
        
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
    
    def add_lag_features(self, df, value_col='value'):
        df = df.copy()
        
        df['traffic_lag_1h'] = df[value_col].shift(60)
        df['traffic_lag_24h'] = df[value_col].shift(1440)
        df['traffic_lag_7d'] = df[value_col].shift(10080)
        
        return df
    
    def add_rolling_features(self, df, value_col='value'):
        df = df.copy()
        
        df['traffic_rolling_mean_1h'] = df[value_col].rolling(window=60, min_periods=1).mean()
        df['traffic_rolling_std_1h'] = df[value_col].rolling(window=60, min_periods=1).std()
        df['traffic_rolling_max_1h'] = df[value_col].rolling(window=60, min_periods=1).max()
        df['traffic_rolling_min_1h'] = df[value_col].rolling(window=60, min_periods=1).min()
        
        df['traffic_rolling_mean_24h'] = df[value_col].rolling(window=1440, min_periods=1).mean()
        
        return df
    
    def engineer_all_features(self, df, year=2026):
        df = self.add_time_features(df)
        df = self.add_ramadan_features(df, year)
        df = self.add_prayer_window_features(df)
        df = self.add_lag_features(df)
        df = self.add_rolling_features(df)
        
        return df.dropna()
