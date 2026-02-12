import numpy as np
import pandas as pd
from typing import Dict, List


class RamadanPatternLearner:
    """Learns Ramadan-specific traffic patterns from historical data.
    
    Analyzes surge patterns (suhoor, iftar, taraweeh) and computes
    daily progression factors showing how traffic evolves throughout Ramadan.
    """
    
    # Configurable class constants
    SURGE_WINDOWS = {
        'suhoor': (3, 5),
        'iftar': (18, 20),
        'taraweeh': (20, 22)
    }
    BASELINE_WINDOW = (10, 14)  # Midday baseline hours
    SURGE_THRESHOLD = 1.5  # Multiplier for surge detection
    DEFAULT_FACTORS = {
        'early': 1.0,
        'mid': 1.1,
        'last_10': 1.25
    }
    
    def __init__(self):
        self.surge_patterns = {}
        self.daily_patterns = {}
    
    def learn_surge_patterns(self, df):
        """Learn surge patterns for key prayer windows.
        
        Args:
            df: DataFrame with datetime index, 'value', 'is_ramadan', 
                'hour', and 'ramadan_day' columns.
        
        Returns:
            self
        """
        ramadan_data = df[df['is_ramadan'] == 1].copy()
        
        for event_name, (start_hour, end_hour) in self.SURGE_WINDOWS.items():
            window_data = ramadan_data[
                (ramadan_data['hour'] >= start_hour) & 
                (ramadan_data['hour'] <= end_hour)
            ]
            
            if len(window_data) == 0:
                continue
            
            # Calculate baseline (midday traffic)
            baseline = ramadan_data[
                (ramadan_data['hour'] >= self.BASELINE_WINDOW[0]) & 
                (ramadan_data['hour'] <= self.BASELINE_WINDOW[1])
            ]['value'].median()
            
            if baseline == 0:
                baseline = ramadan_data['value'].median()
            
            multipliers = []
            durations = []
            
            # Analyze each day's surge
            for day in window_data['ramadan_day'].unique():
                if day == 0:
                    continue
                    
                day_data = window_data[window_data['ramadan_day'] == day]
                peak = day_data['value'].max()
                
                if baseline > 0:
                    multiplier = peak / baseline
                    multipliers.append(multiplier)
                
                # Calculate surge duration (minutes above threshold)
                above_threshold = day_data[day_data['value'] > baseline * self.SURGE_THRESHOLD]
                if len(above_threshold) > 0:
                    # Calculate actual duration in minutes using datetime index
                    if len(above_threshold) > 1:
                        time_diff = (above_threshold.index[-1] - above_threshold.index[0]).total_seconds() / 60
                        duration = time_diff + (above_threshold.index[1] - above_threshold.index[0]).total_seconds() / 60
                    else:
                        # Single data point - use sampling interval if available
                        if len(day_data) > 1:
                            duration = (day_data.index[1] - day_data.index[0]).total_seconds() / 60
                        else:
                            duration = 1.0  # Fallback to 1 minute
                    durations.append(duration)
            
            self.surge_patterns[event_name] = {
                'multiplier_mean': np.mean(multipliers) if multipliers else 1.0,
                'multiplier_std': np.std(multipliers) if multipliers else 0.0,
                'duration_minutes_mean': np.mean(durations) if durations else 60,
                'duration_minutes_std': np.std(durations) if durations else 0.0,
                'confidence': self._calculate_confidence(multipliers),
                'sample_size': len(multipliers)
            }
        
        return self
    
    def learn_daily_progression(self, df):
        """Learn how traffic evolves throughout Ramadan.
        
        Args:
            df: DataFrame with 'is_ramadan', 'ramadan_day', 'hour', 'value'.
        
        Returns:
            self
        """
        ramadan_data = df[df['is_ramadan'] == 1].copy()
        
        for ramadan_day in ramadan_data['ramadan_day'].unique():
            if ramadan_day == 0:
                continue
            
            day_data = ramadan_data[ramadan_data['ramadan_day'] == ramadan_day]
            
            if len(day_data) == 0:
                continue
            
            # Calculate baseline for this day
            midday_data = day_data[
                (day_data['hour'] >= self.BASELINE_WINDOW[0]) & 
                (day_data['hour'] <= self.BASELINE_WINDOW[1])
            ]
            baseline_traffic = midday_data['value'].median() if len(midday_data) > 0 else day_data['value'].median()
            
            self.daily_patterns[int(ramadan_day)] = {
                'avg_traffic': day_data['value'].mean(),
                'peak_traffic': day_data['value'].max(),
                'peak_hour': int(day_data.loc[day_data['value'].idxmax(), 'hour']),
                'baseline_traffic': baseline_traffic
            }
        
        return self
    
    def get_day_adjustment_factor(self, ramadan_day):
        """Get traffic adjustment factor for a specific Ramadan day.
        
        Early Ramadan (days 1-10) typically has lower traffic.
        Last 10 nights (days 21-30) have significantly higher traffic.
        
        Args:
            ramadan_day: Day of Ramadan (1-30)
        
        Returns:
            Adjustment factor relative to early Ramadan
        """
        if ramadan_day not in self.daily_patterns:
            # Default progression based on typical Ramadan patterns
            if ramadan_day <= 10:
                return self.DEFAULT_FACTORS['early']
            elif ramadan_day <= 20:
                return self.DEFAULT_FACTORS['mid']
            else:
                return self.DEFAULT_FACTORS['last_10']
        
        early_days = [d for d in self.daily_patterns.keys() if d <= 10]
        mid_days = [d for d in self.daily_patterns.keys() if 11 <= d <= 20]
        late_days = [d for d in self.daily_patterns.keys() if d >= 21]
        
        # Use whatever data is available
        if ramadan_day <= 10:
            if not early_days:
                return self.DEFAULT_FACTORS['early']
            current_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in early_days if d <= ramadan_day])
            baseline_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in early_days])
        elif ramadan_day <= 20:
            if not mid_days:
                if early_days:
                    # Use early days as baseline
                    baseline_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in early_days])
                    current_avg = baseline_avg * self.DEFAULT_FACTORS['mid']
                else:
                    return self.DEFAULT_FACTORS['mid']
            else:
                current_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in mid_days if d <= ramadan_day])
                baseline_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in early_days]) if early_days else current_avg
        else:
            if not late_days:
                if early_days:
                    # Use early days as baseline
                    baseline_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in early_days])
                    current_avg = baseline_avg * self.DEFAULT_FACTORS['last_10']
                else:
                    return self.DEFAULT_FACTORS['last_10']
            else:
                current_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in late_days if d <= ramadan_day])
                baseline_avg = np.mean([self.daily_patterns[d]['avg_traffic'] for d in early_days]) if early_days else current_avg
        
        if baseline_avg == 0:
            return self.DEFAULT_FACTORS['early']
        
        return current_avg / baseline_avg
    
    def _calculate_confidence(self, multipliers):
        """Calculate confidence score based on variance in multipliers.
        
        Args:
            multipliers: List of multiplier values
        
        Returns:
            Confidence score between 0.6 and 0.99
        """
        if len(multipliers) < 3:
            return 0.6
        
        # Filter out NaN values
        clean_multipliers = [m for m in multipliers if not np.isnan(m)]
        
        if len(clean_multipliers) < 3:
            return 0.6
        
        mean = np.mean(clean_multipliers)
        std = np.std(clean_multipliers)
        
        # Handle NaN in computed stats
        if np.isnan(mean) or np.isnan(std) or mean == 0:
            return 0.6
        
        # Coefficient of variation
        cv = std / mean
        confidence = max(0.6, min(0.99, 1.0 - cv * 0.5))
        
        return confidence
    
    def get_pattern_summary(self):
        """Get summary of learned patterns.
        
        Returns:
            Dict with pattern statistics
        """
        summary = {
            'surge_patterns': self.surge_patterns,
            'daily_progression': {
                'early_ramadan': self.get_day_adjustment_factor(5),
                'mid_ramadan': self.get_day_adjustment_factor(15),
                'last_10_nights': self.get_day_adjustment_factor(25)
            },
            'total_days_analyzed': len(self.daily_patterns)
        }
        
        return summary
