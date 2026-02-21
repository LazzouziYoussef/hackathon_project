import numpy as np
import pandas as pd
from collections import defaultdict


class SeasonalBaselineModel:
    """Seasonal baseline model using hourly traffic patterns.
    
    This is a fallback model used when ML models are unavailable or 
    have low confidence. It learns average traffic patterns by hour
    of day from historical Ramadan data.
    """
    
    def __init__(self):
        self.patterns = defaultdict(dict)
        self.is_trained = False
    
    def train(self, df):
        """Train the model on historical data.
        
        Args:
            df: DataFrame with datetime index and 'value' column.
                Must include 'is_ramadan' and 'hour' features.
        
        Returns:
            self
        """
        ramadan_data = df[df['is_ramadan'] == 1].copy()
        
        if len(ramadan_data) == 0:
            raise ValueError("No Ramadan data found for training")
        
        for hour in range(24):
            hour_data = ramadan_data[ramadan_data['hour'] == hour]['value']
            
            if len(hour_data) > 0:
                self.patterns[hour] = {
                    'mean': hour_data.mean(),
                    'median': hour_data.median(),
                    'std': hour_data.std(),
                    'p25': hour_data.quantile(0.25),
                    'p75': hour_data.quantile(0.75),
                    'count': len(hour_data)
                }
        
        self.is_trained = True
        return self
    
    def predict(self, timestamp, baseline_traffic=None):
        """Predict traffic for a given timestamp.
        
        Args:
            timestamp: datetime object
            baseline_traffic: Current traffic level (optional)
        
        Returns:
            Predicted traffic value
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        hour = timestamp.hour
        
        if hour not in self.patterns:
            return baseline_traffic if baseline_traffic is not None else 0
        
        pattern = self.patterns[hour]
        
        if baseline_traffic is None or baseline_traffic == 0:
            return pattern['median']
        
        # Calculate multiplier based on current vs baseline
        multiplier = self.get_multiplier(hour)
        predicted = baseline_traffic * multiplier
        
        return max(0, predicted)
    
    def get_multiplier(self, hour):
        """Get traffic multiplier for a given hour.
        
        Args:
            hour: Hour of day (0-23)
        
        Returns:
            Multiplier relative to baseline median
        """
        if hour not in self.patterns:
            return 1.0
        
        pattern = self.patterns[hour]
        baseline_median = np.median([p['median'] for p in self.patterns.values()])
        
        if baseline_median == 0:
            return 1.0
        
        return pattern['median'] / baseline_median
    
    def get_confidence(self, hour):
        """Get confidence score for predictions at a given hour.
        
        Confidence is based on the coefficient of variation (lower is better).
        
        Args:
            hour: Hour of day (0-23)
        
        Returns:
            Confidence score between 0.5 and 0.99
        """
        if hour not in self.patterns:
            return 0.5
        
        pattern = self.patterns[hour]
        
        if pattern['mean'] == 0:
            return 0.5
        
        # Coefficient of variation
        cv = pattern['std'] / pattern['mean']
        confidence = max(0.5, min(0.99, 1.0 - cv))
        
        return confidence
    
    def get_pattern_summary(self):
        """Get summary of learned patterns.
        
        Returns:
            Dict with pattern statistics
        """
        if not self.is_trained:
            return {}
        
        hourly_multipliers = {h: self.get_multiplier(h) for h in self.patterns.keys()}
        
        # Identify peak hours
        peak_hours = sorted(hourly_multipliers.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'hours_covered': len(self.patterns),
            'peak_hours': dict(peak_hours),
            'avg_confidence': np.mean([self.get_confidence(h) for h in self.patterns.keys()]),
            'total_samples': sum(p['count'] for p in self.patterns.values())
        }
