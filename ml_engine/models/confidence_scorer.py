import numpy as np
import pandas as pd
from typing import Dict, Optional


class ConfidenceScorer:
    """Multi-factor confidence scoring for traffic predictions.
    
    Combines data quality, variance, sample size, Ramadan day, and time of day
    to produce a final confidence score between 0.5 and 0.99.
    
    System Design Alignment:
    - Confidence threshold: 0.7 (use LSTM if ≥0.7, fallback to baseline if <0.7)
    - Iftar predictions more confident than Suhoor
    - Confidence increases as Ramadan progresses
    """
    
    # Configuration constants
    MIN_CONFIDENCE = 0.5
    MAX_CONFIDENCE = 0.99
    CONFIDENCE_THRESHOLD = 0.7  # Threshold for using ML vs fallback
    
    # Event base confidence (domain knowledge)
    EVENT_BASE_CONFIDENCE = {
        'iftar': 0.85,      # Most predictable (everyone breaks fast together)
        'taraweeh': 0.80,   # Predictable (night prayer after Iftar)
        'suhoor': 0.75,     # Less predictable (pre-dawn meal timing varies)
        'other': 0.70       # General traffic
    }
    
    # Confidence factor weights (must sum to 1.0)
    FACTOR_WEIGHTS = {
        'base': 0.20,
        'model': 0.35,
        'quality': 0.25,
        'ramadan': 0.10,
        'time': 0.07,
        'sample': 0.03
    }
    
    def __init__(self):
        pass
    
    def calculate_confidence(
        self,
        event_name: str,
        model_confidence: float,
        data_quality: float,
        ramadan_day: Optional[int] = None,
        hour: Optional[int] = None,
        sample_size: Optional[int] = None
    ) -> float:
        """Calculate final confidence score combining multiple factors.
        
        Args:
            event_name: Event type ('suhoor', 'iftar', 'taraweeh', 'other')
            model_confidence: Base confidence from pattern learner or baseline model (0-1)
            data_quality: Data quality score (0-1, based on completeness)
            ramadan_day: Day of Ramadan (1-30), None if not Ramadan
            hour: Hour of day (0-23), used for time-based confidence adjustment
            sample_size: Number of samples used for prediction
        
        Returns:
            Final confidence score between MIN_CONFIDENCE and MAX_CONFIDENCE
        """
        # Validate and clamp inputs
        model_confidence = max(0.0, min(1.0, model_confidence))
        data_quality = max(0.0, min(1.0, data_quality))
        if hour is not None:
            hour = max(0, min(23, int(hour)))
        if ramadan_day is not None:
            ramadan_day = max(1, min(30, int(ramadan_day)))
        
        # Normalize event_name to avoid typos/casing issues
        normalized_event_name = (
            event_name.strip().lower()
            if isinstance(event_name, str) and event_name.strip()
            else 'other'
        )
        base = self.EVENT_BASE_CONFIDENCE.get(
            normalized_event_name,
            self.EVENT_BASE_CONFIDENCE['other']
        )
        
        # Use class-level weights
        weights = self.FACTOR_WEIGHTS
        
        # Factor 1: Base event confidence
        base_factor = base * weights['base']
        
        # Factor 2: Model confidence
        model_factor = model_confidence * weights['model']
        
        # Factor 3: Data quality
        data_factor = data_quality * weights['quality']
        
        # Factor 4: Ramadan day progression
        # Confidence increases as Ramadan progresses (more data, better patterns)
        # Note: ramadan_day is already validated to [1, 30] range above
        if ramadan_day is not None and 1 <= ramadan_day <= 30:
            if ramadan_day <= 10:
                ramadan_boost = 0.6  # Early days: 60% of max boost
            elif ramadan_day <= 20:
                ramadan_boost = 0.8  # Mid Ramadan: 80% of max boost
            else:
                ramadan_boost = 1.0  # Last 10 nights: full boost
        else:
            ramadan_boost = 0.5  # Not Ramadan or invalid: minimal boost
        ramadan_factor = ramadan_boost * weights['ramadan']
        
        # Factor 5: Time of day
        # Peak hours are more predictable
        if hour is not None:
            if hour in [3, 4, 5, 18, 19, 20, 21]:  # Prayer window hours
                time_boost = 1.0  # Full boost
            elif hour in [10, 11, 12, 13, 14]:  # Midday baseline hours
                time_boost = 0.8  # Moderate boost
            else:  # Other hours
                time_boost = 0.6  # Minimal boost
        else:
            time_boost = 0.7  # Default
        time_factor = time_boost * weights['time']
        
        # Factor 6: Sample size
        # Treat missing or invalid (<=0) sample size separately from small valid samples
        if sample_size is None:
            sample_boost = 0.7  # Default for missing data
        elif sample_size <= 0:
            sample_boost = 0.3  # Lower penalty for invalid/zero data (worse than tiny valid samples)
        else:
            # Valid positive sample sizes
            if sample_size >= 30:
                sample_boost = 1.0
            elif sample_size >= 15:
                sample_boost = 0.8
            elif sample_size >= 5:
                sample_boost = 0.6
            else:
                # Explicitly represents "few but valid samples" (1-4)
                sample_boost = 0.4
        sample_factor = sample_boost * weights['sample']
        
        # Combine all factors
        confidence = (
            base_factor +
            model_factor +
            data_factor +
            ramadan_factor +
            time_factor +
            sample_factor
        )
        
        # Normalize to ensure within bounds
        confidence = max(self.MIN_CONFIDENCE, min(self.MAX_CONFIDENCE, confidence))
        
        return confidence
    
    def calculate_data_quality(self, df: pd.DataFrame, required_cols: list = None) -> float:
        """Calculate data quality score based on completeness.
        
        Args:
            df: DataFrame to assess
            required_cols: List of required columns, if None checks all
        
        Returns:
            Data quality score (0-1)
        """
        if len(df) == 0:
            return 0.0
        
        if required_cols is None:
            required_cols = df.columns.tolist()
        
        # Validate that all required columns exist
        available_cols = [col for col in required_cols if col in df.columns]
        missing_cols = set(required_cols) - set(available_cols)
        
        if missing_cols:
            raise ValueError(
                f"Required columns not found in DataFrame: {sorted(missing_cols)}"
            )
        
        # Calculate missing data percentage
        missing_counts = df[available_cols].isna().sum()
        total_cells = len(df) * len(available_cols)
        missing_pct = missing_counts.sum() / total_cells if total_cells > 0 else 1.0
        
        # Quality score: 1.0 - missing_pct
        quality = 1.0 - missing_pct
        
        # Apply penalty if too much missing data
        if missing_pct > 0.2:  # More than 20% missing
            quality *= 0.6  # Significant penalty
        elif missing_pct > 0.1:  # More than 10% missing
            quality *= 0.8  # Moderate penalty
        
        return max(0.0, min(1.0, quality))
    
    def should_use_ml(self, confidence: float) -> bool:
        """Determine if ML model should be used or fallback to baseline.
        
        Args:
            confidence: Calculated confidence score
        
        Returns:
            True if confidence >= threshold, False to use fallback
        """
        return confidence >= self.CONFIDENCE_THRESHOLD
    
    def get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level.
        
        Args:
            confidence: Confidence score
        
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.8:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        elif confidence >= 0.6:
            return "low"
        else:
            return "very_low"
