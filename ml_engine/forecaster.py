import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from models.seasonal_baseline import SeasonalBaselineModel
from models.pattern_learner import RamadanPatternLearner
from models.confidence_scorer import ConfidenceScorer
from preprocessing.feature_engineering import FeatureEngineer
from utils.time_utils import RamadanCalendar


@dataclass
class ForecastResult:
    """Result of a traffic forecast."""
    event_name: str
    predicted_traffic: float
    confidence: float
    time_to_impact: float  # Hours until event
    trigger_time: datetime
    event_time: datetime
    baseline_traffic: float
    multiplier: float
    used_ml: bool  # True if ML model used, False if fallback to baseline


class HybridForecaster:
    """Hybrid traffic forecaster combining rule-based timing with ML-learned patterns.
    
    System Design Alignment:
    - Rules determine WHEN (hour triggers based on prayer times)
    - ML determines HOW MUCH (learned multipliers from patterns)
    - Falls back to seasonal baseline if confidence < 0.7
    - Forecast horizon: 4 hours (MVP), not 24-48 hours (production target)
    - Ramadan-specific event handling (Suhoor, Iftar, Taraweeh)
    """
    
    # Rule-based trigger times (hours before event)
    TRIGGER_RULES = {
        'suhoor': {
            'trigger_hour': 2,   # 2 AM trigger for 3-5 AM suhoor
            'event_hour': 4,     # Peak at 4 AM
            'window': (3, 5)
        },
        'iftar': {
            'trigger_hour': 15,  # 3 PM trigger for 6-8 PM iftar
            'event_hour': 18,    # Peak at 6 PM
            'window': (18, 20)
        },
        'taraweeh': {
            'trigger_hour': 17,  # 5 PM trigger for 8-10 PM taraweeh
            'event_hour': 20,    # Peak at 8 PM
            'window': (20, 22)
        }
    }
    
    FORECAST_HORIZON_HOURS = 4  # MVP: 4-hour horizon (production: 24-48)
    
    def __init__(self):
        self.baseline_model = SeasonalBaselineModel()
        self.pattern_learner = RamadanPatternLearner()
        self.confidence_scorer = ConfidenceScorer()
        self.feature_engineer = FeatureEngineer()
        
        self.is_trained = False
    
    def train(self, df: pd.DataFrame) -> 'HybridForecaster':
        """Train both baseline and pattern learner models.
        
        Args:
            df: DataFrame with datetime index, 'value', and engineered features
        
        Returns:
            self
        """
        # Ensure features are engineered
        if 'is_ramadan' not in df.columns:
            df = self.feature_engineer.add_time_features(df)
            df = self.feature_engineer.add_ramadan_features(df)
        
        # Train both models
        self.baseline_model.train(df)
        self.pattern_learner.learn_surge_patterns(df)
        self.pattern_learner.learn_daily_progression(df)
        
        self.is_trained = True
        return self
    
    def forecast(
        self,
        current_time: datetime,
        current_traffic: float,
        historical_df: Optional[pd.DataFrame] = None
    ) -> List[ForecastResult]:
        """Generate forecasts for upcoming events within the forecast horizon.
        
        Args:
            current_time: Current timestamp
            current_traffic: Current traffic value
            historical_df: Optional historical data for data quality assessment
        
        Returns:
            List of ForecastResult objects for predicted events
        """
        if not self.is_trained:
            raise ValueError("Forecaster must be trained before making predictions")
        
        forecasts = []
        current_hour = current_time.hour
        
        # Check if we're in Ramadan
        year = current_time.year
        is_ramadan = RamadanCalendar.is_ramadan(current_time, year=year)
        ramadan_day = RamadanCalendar.get_ramadan_day(current_time, year=year) if is_ramadan else None
        
        if not is_ramadan:
            # No Ramadan-specific forecasts outside Ramadan
            return forecasts
        
        # Check each event type for triggers
        for event_name, rules in self.TRIGGER_RULES.items():
            trigger_hour = rules['trigger_hour']
            event_hour = rules['event_hour']
            
            # Calculate time to event
            hours_until_event = (event_hour - current_hour) % 24
            
            # Only forecast if we're at the trigger time and event is within horizon
            if current_hour == trigger_hour and hours_until_event <= self.FORECAST_HORIZON_HOURS:
                event_time = current_time.replace(hour=event_hour, minute=0, second=0, microsecond=0)
                if event_time <= current_time:
                    event_time += timedelta(days=1)
                
                time_to_impact = (event_time - current_time).total_seconds() / 3600
                
                # Generate forecast
                forecast = self._forecast_event(
                    event_name=event_name,
                    event_time=event_time,
                    current_time=current_time,
                    ramadan_day=ramadan_day,
                    historical_df=historical_df
                )
                
                if forecast:
                    forecasts.append(forecast)
        
        return forecasts
    
    def _forecast_event(
        self,
        event_name: str,
        event_time: datetime,
        current_time: datetime,
        ramadan_day: Optional[int],
        historical_df: Optional[pd.DataFrame]
    ) -> Optional[ForecastResult]:
        """Forecast a specific event using hybrid approach.
        
        Args:
            event_name: Event type ('suhoor', 'iftar', 'taraweeh')
            event_time: When the event will occur
            current_time: Current timestamp
            current_traffic: Current traffic value
            ramadan_day: Day of Ramadan (1-30)
            historical_df: Historical data for quality assessment
        
        Returns:
            ForecastResult or None if forecast cannot be made
        """
        event_hour = event_time.hour
        
        # Calculate data quality
        data_quality = 0.8  # Default
        if historical_df is not None:
            try:
                data_quality = self.confidence_scorer.calculate_data_quality(historical_df)
            except (ValueError, KeyError, AttributeError) as e:
                # Log warning and use default if data quality calculation fails
                import warnings
                warnings.warn(f"Data quality calculation failed: {e}. Using default value.")
                data_quality = 0.8
        
        # Get baseline prediction
        baseline_traffic = self._get_baseline_prediction(event_hour, ramadan_day)
        
        # Get learned patterns
        surge_multiplier = self._get_learned_multiplier(event_name, ramadan_day)
        
        # Calculate model confidence from pattern learner
        model_confidence = 0.8  # Default
        if event_name in self.pattern_learner.surge_patterns:
            pattern = self.pattern_learner.surge_patterns[event_name]
            model_confidence = pattern.get('confidence', 0.8)
        
        # Get sample size
        sample_size = None
        if event_name in self.pattern_learner.surge_patterns:
            sample_size = self.pattern_learner.surge_patterns[event_name].get('sample_size', None)
        
        # Calculate final confidence
        confidence = self.confidence_scorer.calculate_confidence(
            event_name=event_name,
            model_confidence=model_confidence,
            data_quality=data_quality,
            ramadan_day=ramadan_day,
            hour=event_hour,
            sample_size=sample_size
        )
        
        # Decide whether to use ML or fallback
        use_ml = self.confidence_scorer.should_use_ml(confidence)
        
        if use_ml:
            # ML: Use learned multiplier
            predicted_traffic = baseline_traffic * surge_multiplier
            multiplier = surge_multiplier
        else:
            # Fallback: Use baseline with conservative multiplier
            multiplier = self.baseline_model.get_multiplier(event_hour)
            predicted_traffic = baseline_traffic * multiplier
        
        time_to_impact = (event_time - current_time).total_seconds() / 3600
        
        return ForecastResult(
            event_name=event_name,
            predicted_traffic=predicted_traffic,
            confidence=confidence,
            time_to_impact=time_to_impact,
            trigger_time=current_time,
            event_time=event_time,
            baseline_traffic=baseline_traffic,
            multiplier=multiplier,
            used_ml=use_ml
        )
    
    def _get_baseline_prediction(self, hour: int, ramadan_day: Optional[int]) -> float:
        """Get baseline traffic prediction for a given hour.
        
        Args:
            hour: Hour of day (0-23)
            ramadan_day: Day of Ramadan (1-30) or None
        
        Returns:
            Baseline traffic prediction
        """
        # Use seasonal baseline - create a timestamp with the target hour
        # Use a typical Ramadan date from training period for consistency
        dummy_timestamp = datetime(2026, 2, 20, hour, 0)
        
        try:
            prediction = self.baseline_model.predict(dummy_timestamp, baseline_traffic=None)
            return float(prediction)
        except (ValueError, KeyError, AttributeError) as e:
            # Log warning and use fallback if prediction fails
            import warnings
            warnings.warn(f"Baseline prediction failed for hour {hour}: {e}. Using fallback value.")
            return 100.0
    
    def _get_learned_multiplier(self, event_name: str, ramadan_day: Optional[int]) -> float:
        """Get learned multiplier for an event, adjusted for daily progression.
        
        Args:
            event_name: Event type
            ramadan_day: Day of Ramadan (1-30) or None
        
        Returns:
            Learned multiplier adjusted for Ramadan progression
        """
        # Get base multiplier from pattern learner
        base_multiplier = 1.5  # Default conservative multiplier
        
        if event_name in self.pattern_learner.surge_patterns:
            pattern = self.pattern_learner.surge_patterns[event_name]
            base_multiplier = pattern.get('multiplier_mean', 1.5)
        
        # Apply daily progression adjustment
        if ramadan_day is not None:
            progression_factor = self.pattern_learner.get_day_adjustment_factor(ramadan_day)
            adjusted_multiplier = base_multiplier * progression_factor
        else:
            adjusted_multiplier = base_multiplier
        
        return adjusted_multiplier
    
    def get_model_summary(self) -> Dict:
        """Get summary of trained models.
        
        Returns:
            Dictionary with model statistics
        """
        if not self.is_trained:
            return {'trained': False}
        
        return {
            'trained': True,
            'baseline_summary': self.baseline_model.get_pattern_summary(),
            'pattern_summary': self.pattern_learner.get_pattern_summary(),
            'forecast_horizon_hours': self.FORECAST_HORIZON_HOURS,
            'trigger_rules': self.TRIGGER_RULES
        }
