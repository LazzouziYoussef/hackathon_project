"""Training pipeline for Sadaqa Tech ML Engine.

Loads historical data, engineers features, trains models, and saves them to disk.
Executed via: python -m ml_engine.training.train --tenant-id=test_ngo

Core principle: Prediction before automation. Models are trained on historical data
and saved for inference; no autonomous actions are taken.
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pickle
from typing import Optional
import warnings

# Import from ml_engine package (assumes ml_engine is in PYTHONPATH)
from preprocessing.data_loader import MetricsDataLoader
from preprocessing.feature_engineering import FeatureEngineer
from models.seasonal_baseline import SeasonalBaselineModel
from models.pattern_learner import RamadanPatternLearner
from models.confidence_scorer import ConfidenceScorer
from forecaster import HybridForecaster


class TrainingPipeline:
    """End-to-end training pipeline for ML models.
    
    Workflow:
    1. Load historical metrics from data loader (or use provided DataFrame)
    2. Engineer features (time, ramadan, rolling, lag, prayer windows)
    3. Train seasonal baseline model
    4. Train ramadan pattern learner
    5. Train hybrid forecaster (combines baseline + pattern learner + confidence scorer)
    6. Save trained models to disk as .pkl files
    
    Models are tenant-scoped and versioned by training timestamp.
    """
    
    def __init__(
        self,
        tenant_id: str,
        model_dir: str = "ml_engine/models_trained",
        min_training_days: int = 60
    ):
        """Initialize training pipeline.
        
        Args:
            tenant_id: Tenant ID for model scoping
            model_dir: Directory to save trained models
            min_training_days: Minimum days of historical data required
        
        Raises:
            ValueError: If tenant_id is empty or min_training_days < 1
        """
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id must be a non-empty string")
        if min_training_days < 1:
            raise ValueError(f"min_training_days must be >= 1, got {min_training_days}")
        
        self.tenant_id = tenant_id.strip()
        self.model_dir = Path(model_dir)
        self.min_training_days = min_training_days
        
        # Create model directory if it doesn't exist
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        # Note: data_loader is not initialized here because it requires a database connection.
        # It should be provided when calling load_data() if actual database loading is needed.
        # For testing with pre-loaded DataFrames, data_loader is not required.
        self.data_loader = None
        self.feature_engineer = FeatureEngineer()
        
        # Training metadata
        self.training_timestamp = None
        self.training_summary = {}
    
    def load_data(
        self,
        days_history: Optional[int] = None,
        end_date: Optional[datetime] = None,
        data_loader=None
    ):
        """Load historical metrics data.
        
        Args:
            days_history: Number of days of history to load (default: min_training_days)
            end_date: End date for data range (default: now)
            data_loader: Optional MetricsDataLoader instance (required for database loading)
        
        Returns:
            DataFrame with historical metrics
        
        Raises:
            ValueError: If data_loader is missing or no historical data is available
        
        Warnings:
            UserWarning: If actual_days < min_training_days (but training continues)
        """
        if data_loader is None and self.data_loader is None:
            raise ValueError(
                "data_loader is required for loading historical data from database. "
                "Either provide a data_loader parameter or pass a DataFrame to run()."
            )
        
        # Use provided data_loader or stored one
        loader = data_loader if data_loader is not None else self.data_loader
        
        if days_history is None:
            days_history = self.min_training_days
        
        if end_date is None:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=days_history)
        
        print(f"Loading {days_history} days of historical data for tenant '{self.tenant_id}'...")
        print(f"Date range: {start_date.date()} to {end_date.date()}")
        
        df = loader.load_historical_metrics(
            tenant_id=self.tenant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if len(df) == 0:
            raise ValueError(
                f"No historical data available for tenant '{self.tenant_id}' "
                f"in range {start_date.date()} to {end_date.date()}"
            )
        
        # Calculate actual days of data
        actual_days = (df.index.max() - df.index.min()).days + 1
        
        if actual_days < self.min_training_days:
            warnings.warn(
                f"Only {actual_days} days of data available, "
                f"minimum recommended is {self.min_training_days} days. "
                "Model quality may be reduced."
            )
        
        print(f"✓ Loaded {len(df)} data points spanning {actual_days} days")
        
        return df
    
    def engineer_features(self, df):
        """Engineer features from raw metrics data.
        
        Args:
            df: DataFrame with raw metrics
        
        Returns:
            DataFrame with engineered features
        """
        print("\nEngineering features...")
        
        # Return early if DataFrame is empty
        if len(df) == 0:
            raise ValueError("Cannot engineer features from empty DataFrame")
        
        # Add time features
        df = self.feature_engineer.add_time_features(df)
        
        # Add Ramadan features
        if len(df) > 0:
            years = {ts.year for ts in df.index}
            if len(years) > 1:
                raise ValueError(
                    "add_ramadan_features currently assumes data from a single calendar year; "
                    f"received multiple years: {sorted(years)}. "
                    "Either restrict the training data to a single year or update "
                    "add_ramadan_features to infer Ramadan dates from the index per row."
                )
            year = next(iter(years))
            df = self.feature_engineer.add_ramadan_features(df, year=year)
        
        # Count features
        feature_cols = [col for col in df.columns if col != 'value']
        print(f"✓ Engineered {len(feature_cols)} features")
        
        return df
    
    def train_models(self, df):
        """Train all models on prepared data.
        
        Args:
            df: DataFrame with engineered features
        
        Returns:
            Dictionary of trained models
        """
        print("\nTraining models...")
        
        # Train hybrid forecaster (which trains baseline + pattern learner internally)
        print("  - Training HybridForecaster (baseline + pattern learner + confidence scorer)...")
        forecaster = HybridForecaster()
        forecaster.train(df)
        
        print("✓ All models trained successfully")
        
        return {
            'forecaster': forecaster,
            'baseline_model': forecaster.baseline_model,
            'pattern_learner': forecaster.pattern_learner,
            'confidence_scorer': forecaster.confidence_scorer
        }
    
    def save_models(self, models):
        """Save trained models to disk.
        
        Models are saved with tenant-scoped naming and timestamp versioning:
        - forecaster_{tenant_id}_{timestamp}.pkl
        - Latest symlink: forecaster_{tenant_id}_latest.pkl
        
        Args:
            models: Dictionary of trained models
        
        Returns:
            Dictionary mapping model names to file paths
        """
        print("\nSaving models to disk...")
        
        self.training_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_paths = {}
        
        # Save forecaster (main model)
        forecaster_filename = f"forecaster_{self.tenant_id}_{self.training_timestamp}.pkl"
        forecaster_path = self.model_dir / forecaster_filename
        
        with open(forecaster_path, 'wb') as f:
            pickle.dump(models['forecaster'], f)
        
        saved_paths['forecaster'] = str(forecaster_path)
        print(f"  ✓ Saved forecaster: {forecaster_path}")
        
        # Create/update symlink to latest version (using absolute path for robustness)
        latest_link = self.model_dir / f"forecaster_{self.tenant_id}_latest.pkl"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        
        latest_link.symlink_to(forecaster_path.resolve())
        print(f"  ✓ Updated latest symlink: {latest_link}")
        
        return saved_paths
    
    def generate_summary(self, df, models, saved_paths):
        """Generate training summary report.
        
        Args:
            df: Training data
            models: Trained models
            saved_paths: Paths where models were saved
        
        Returns:
            Dictionary with training summary
        """
        forecaster = models['forecaster']
        
        summary = {
            'tenant_id': self.tenant_id,
            'training_timestamp': self.training_timestamp,
            'data_stats': {
                'total_points': len(df),
                'date_range_start': str(df.index.min()),
                'date_range_end': str(df.index.max()),
                'days_of_data': (df.index.max() - df.index.min()).days + 1,
                'features_count': len([col for col in df.columns if col != 'value'])
            },
            'model_summaries': {
                'forecaster': forecaster.get_model_summary(),
            },
            'saved_models': saved_paths
        }
        
        self.training_summary = summary
        return summary
    
    def print_summary(self, summary):
        """Print training summary in human-readable format.
        
        Args:
            summary: Training summary dictionary
        """
        print("\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)
        print(f"Tenant ID: {summary['tenant_id']}")
        print(f"Training Timestamp: {summary['training_timestamp']}")
        print(f"\nData Statistics:")
        print(f"  Total Data Points: {summary['data_stats']['total_points']:,}")
        print(f"  Date Range: {summary['data_stats']['date_range_start']} to {summary['data_stats']['date_range_end']}")
        print(f"  Days of Data: {summary['data_stats']['days_of_data']}")
        print(f"  Features: {summary['data_stats']['features_count']}")
        print(f"\nForecaster Configuration:")
        forecaster_summary = summary['model_summaries']['forecaster']
        print(f"  Trained: {forecaster_summary['trained']}")
        print(f"  Forecast Horizon: {forecaster_summary['forecast_horizon_hours']} hours")
        print(f"  Trigger Rules: {len(forecaster_summary['trigger_rules'])} events")
        print(f"\nSaved Models:")
        for model_name, path in summary['saved_models'].items():
            print(f"  {model_name}: {path}")
        print("="*60)
    
    def run(
        self,
        df=None,
        days_history: Optional[int] = None,
        end_date: Optional[datetime] = None
    ):
        """Run complete training pipeline.
        
        Args:
            df: Optional pre-loaded DataFrame (for testing); if None, loads from data_loader
            days_history: Number of days of history to load
            end_date: End date for data range
        
        Returns:
            Dictionary with training summary
        """
        print(f"\nStarting ML Training Pipeline for tenant: {self.tenant_id}")
        print("="*60)
        
        # Step 1: Load data
        if df is None:
            df = self.load_data(days_history=days_history, end_date=end_date)
        else:
            print(f"Using provided DataFrame with {len(df)} data points")
            
            # Check data sufficiency even when DataFrame is provided
            if len(df) > 0:
                actual_days = (df.index.max() - df.index.min()).days + 1
                if actual_days < self.min_training_days:
                    warnings.warn(
                        f"Only {actual_days} days of data available, "
                        f"minimum recommended is {self.min_training_days} days. "
                        "Model quality may be reduced."
                    )
        
        # Step 2: Engineer features
        df = self.engineer_features(df)
        
        # Step 3: Train models
        models = self.train_models(df)
        
        # Step 4: Save models
        saved_paths = self.save_models(models)
        
        # Step 5: Generate summary
        summary = self.generate_summary(df, models, saved_paths)
        
        # Step 6: Print summary
        self.print_summary(summary)
        
        print(f"\n✓ Training pipeline completed successfully!")
        
        return summary


def main():
    """CLI entry point for training pipeline.
    
    Note: This CLI currently requires a database connection to be configured.
    For production use, ensure MetricsDataLoader is properly initialized with
    a database connection. For testing, use the TrainingPipeline class directly
    with a pre-loaded DataFrame.
    
    TODO: Wire up database connection configuration (e.g., from environment
    variables or config file) to enable standalone CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Train ML models for Sadaqa Tech scaling recommendations"
    )
    parser.add_argument(
        '--tenant-id',
        type=str,
        required=True,
        help="Tenant ID for model scoping (e.g., 'test_ngo')"
    )
    parser.add_argument(
        '--days-history',
        type=int,
        default=60,
        help="Number of days of historical data to load (default: 60)"
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        default="ml_engine/models_trained",
        help="Directory to save trained models (default: ml_engine/models_trained)"
    )
    parser.add_argument(
        '--min-training-days',
        type=int,
        default=60,
        help="Minimum days of data required for training (default: 60)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        pipeline = TrainingPipeline(
            tenant_id=args.tenant_id,
            model_dir=args.model_dir,
            min_training_days=args.min_training_days
        )
        
        # TODO: Wire database connection here
        # For now, this will fail at run() when df is None and data_loader is not set.
        # Example: data_loader = MetricsDataLoader(db_connection=get_db_connection())
        # Then: summary = pipeline.run(days_history=args.days_history, data_loader=data_loader)
        
        print("\n❌ CLI usage currently requires database connection setup.")
        print("Please use TrainingPipeline directly with a pre-loaded DataFrame for testing.")
        print("\nExample:")
        print("  from ml_engine.training.train import TrainingPipeline")
        print("  pipeline = TrainingPipeline(tenant_id='test_ngo', model_dir='models/')")
        print("  summary = pipeline.run(df=your_dataframe)")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
