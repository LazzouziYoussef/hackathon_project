"""Tests for training pipeline.

Test Coverage:
- TrainingPipeline initialization and validation
- Data loading with various configurations
- Feature engineering integration
- Model training workflow
- Model saving and versioning
- Summary generation
- End-to-end pipeline execution
- Error handling and edge cases
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import tempfile
import shutil

# Import from training module (assumes ml_engine is in PYTHONPATH)
from training.train import TrainingPipeline


# Test Fixtures

class FakeMetricsDataLoader:
    """Test double for MetricsDataLoader that records load_historical_metrics() calls."""
    
    def __init__(self, df):
        self.df = df
        self.calls = []
    
    def load_historical_metrics(self, tenant_id, start_date, end_date):
        self.calls.append({
            'tenant_id': tenant_id,
            'start_date': start_date,
            'end_date': end_date
        })
        return self.df.copy()


@pytest.fixture
def temp_model_dir():
    """Create temporary directory for model storage."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_training_data():
    """Generate sample training data for testing."""
    # 90 days of hourly data
    start_date = datetime(2024, 2, 1)
    hours = 90 * 24
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    
    # Use a deterministic RNG to avoid flaky tests
    rng = np.random.default_rng(42)
    
    # Simulate traffic patterns with daily seasonality
    values = []
    for ts in timestamps:
        hour = ts.hour
        # Higher traffic during evening hours
        base_value = 100 + (50 * np.sin((hour - 12) * np.pi / 12))
        noise = rng.normal(0, 10)
        values.append(max(0, base_value + noise))
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'value': values
    })
    df.set_index('timestamp', inplace=True)
    
    return df


# Initialization Tests

def test_pipeline_initialization(temp_model_dir):
    """Test pipeline initialization with valid parameters."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=30
    )
    
    assert pipeline.tenant_id == "test_tenant"
    assert pipeline.model_dir == Path(temp_model_dir)
    assert pipeline.min_training_days == 30
    assert pipeline.training_timestamp is None


def test_pipeline_initialization_strips_whitespace(temp_model_dir):
    """Test that tenant_id whitespace is stripped."""
    pipeline = TrainingPipeline(
        tenant_id="  test_tenant  ",
        model_dir=temp_model_dir
    )
    
    assert pipeline.tenant_id == "test_tenant"


def test_pipeline_initialization_creates_model_dir(temp_model_dir):
    """Test that model directory is created if it doesn't exist."""
    model_dir = Path(temp_model_dir) / "subdir" / "models"
    
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=str(model_dir)
    )
    
    assert model_dir.exists()
    assert model_dir.is_dir()


def test_pipeline_initialization_empty_tenant_id(temp_model_dir):
    """Test that empty tenant_id raises error."""
    with pytest.raises(ValueError, match="tenant_id must be a non-empty string"):
        TrainingPipeline(tenant_id="", model_dir=temp_model_dir)
    
    with pytest.raises(ValueError, match="tenant_id must be a non-empty string"):
        TrainingPipeline(tenant_id="   ", model_dir=temp_model_dir)


def test_pipeline_initialization_invalid_min_training_days(temp_model_dir):
    """Test that invalid min_training_days raises error."""
    with pytest.raises(ValueError, match="min_training_days must be >= 1"):
        TrainingPipeline(
            tenant_id="test_tenant",
            model_dir=temp_model_dir,
            min_training_days=0
        )
    
    with pytest.raises(ValueError, match="min_training_days must be >= 1"):
        TrainingPipeline(
            tenant_id="test_tenant",
            model_dir=temp_model_dir,
            min_training_days=-5
        )


# Data Loading Tests

def test_load_data_passes_correct_parameters_to_data_loader(temp_model_dir):
    """DB-backed load_data should delegate tenant_id/start_date/end_date correctly."""
    end_date = datetime(2024, 3, 31)
    days_history = 30
    tenant_id = "tenant-abc"
    
    # Create DataFrame spanning exactly 30 days
    df = pd.DataFrame({
        'timestamp': pd.date_range(
            start=datetime(2024, 3, 1),
            end=end_date,
            freq='D'
        ),
        'value': np.arange(31)
    })
    df.set_index('timestamp', inplace=True)
    
    loader = FakeMetricsDataLoader(df)
    pipeline = TrainingPipeline(
        tenant_id=tenant_id,
        model_dir=temp_model_dir,
        min_training_days=10
    )
    
    result = pipeline.load_data(
        days_history=days_history,
        end_date=end_date,
        data_loader=loader
    )
    
    # Returned dataframe is from the loader
    assert len(result) == len(df)
    
    # The loader is called exactly once with the expected arguments
    assert len(loader.calls) == 1
    call = loader.calls[0]
    assert call['tenant_id'] == tenant_id
    assert call['end_date'] == end_date
    
    # start_date should be end_date - days_history
    expected_start = end_date - timedelta(days=days_history)
    assert call['start_date'] == expected_start


def test_load_data_uses_provided_data_loader_over_self_data_loader(temp_model_dir):
    """load_data should prefer the provided data_loader argument."""
    df1 = pd.DataFrame({
        'timestamp': pd.date_range(start=datetime(2024, 3, 1), periods=10, freq='D'),
        'value': [1.0] * 10
    })
    df1.set_index('timestamp', inplace=True)
    
    df2 = pd.DataFrame({
        'timestamp': pd.date_range(start=datetime(2024, 3, 1), periods=10, freq='D'),
        'value': [2.0] * 10
    })
    df2.set_index('timestamp', inplace=True)
    
    loader1 = FakeMetricsDataLoader(df1)
    loader2 = FakeMetricsDataLoader(df2)
    
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=1
    )
    pipeline.data_loader = loader1
    
    # Provide loader2 as argument - it should be used instead of self.data_loader
    result = pipeline.load_data(
        days_history=10,
        end_date=datetime(2024, 3, 10),
        data_loader=loader2
    )
    
    # Should use loader2 (value=2.0) not loader1 (value=1.0)
    assert result['value'].iloc[0] == 2.0
    assert len(loader2.calls) == 1
    assert len(loader1.calls) == 0


def test_load_data_raises_when_no_data_loader(temp_model_dir):
    """load_data should fail when neither self.data_loader nor argument is provided."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    with pytest.raises(ValueError, match="data_loader is required"):
        pipeline.load_data(data_loader=None)


def test_load_data_raises_when_no_historical_data(temp_model_dir):
    """load_data should raise when the DB loader returns an empty dataframe."""
    empty_df = pd.DataFrame(columns=['timestamp', 'value'])
    empty_df.set_index('timestamp', inplace=True)
    
    loader = FakeMetricsDataLoader(empty_df)
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    with pytest.raises(ValueError, match="No historical data available"):
        pipeline.load_data(
            days_history=30,
            end_date=datetime(2024, 3, 31),
            data_loader=loader
        )


def test_load_data_warns_when_not_enough_history(temp_model_dir):
    """DB-backed load_data should warn when actual_days < min_training_days."""
    actual_days = 5
    min_training_days = 10
    end_date = datetime(2024, 3, 5)
    
    df = pd.DataFrame({
        'timestamp': pd.date_range(
            start=datetime(2024, 3, 1),
            end=end_date,
            freq='D'
        ),
        'value': np.arange(5)  # 5 values for 5 days (Mar 1-5)
    })
    df.set_index('timestamp', inplace=True)
    
    loader = FakeMetricsDataLoader(df)
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=min_training_days
    )
    
    with pytest.warns(UserWarning, match="Only .* days of data available"):
        result = pipeline.load_data(
            days_history=30,
            end_date=end_date,
            data_loader=loader
        )
    
    # Data should still be returned even when warning is emitted
    assert not result.empty
    assert len(result) > 0


def test_load_data_uses_min_training_days_as_default(temp_model_dir):
    """load_data should use min_training_days when days_history is not provided."""
    min_training_days = 45
    end_date = datetime(2024, 3, 31)
    
    df = pd.DataFrame({
        'timestamp': pd.date_range(
            start=datetime(2024, 2, 15),
            end=end_date,
            freq='D'
        ),
        'value': np.arange(46)
    })
    df.set_index('timestamp', inplace=True)
    
    loader = FakeMetricsDataLoader(df)
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=min_training_days
    )
    
    result = pipeline.load_data(
        end_date=end_date,
        data_loader=loader
    )
    
    # Should have requested min_training_days worth of data
    assert len(loader.calls) == 1
    call = loader.calls[0]
    expected_start = end_date - timedelta(days=min_training_days)
    assert call['start_date'] == expected_start


# Feature Engineering Tests

def test_engineer_features(temp_model_dir, sample_training_data):
    """Test feature engineering step."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = sample_training_data.copy()
    engineered_df = pipeline.engineer_features(df)
    
    # Check that features were added
    assert 'hour' in engineered_df.columns
    assert 'day_of_week' in engineered_df.columns
    assert 'is_ramadan' in engineered_df.columns
    assert 'ramadan_day' in engineered_df.columns
    
    # Original data should be preserved
    assert 'value' in engineered_df.columns
    assert len(engineered_df) == len(df)


def test_engineer_features_preserves_index(temp_model_dir, sample_training_data):
    """Test that feature engineering preserves timestamp index."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = sample_training_data.copy()
    original_index = df.index.copy()
    
    engineered_df = pipeline.engineer_features(df)
    
    assert all(engineered_df.index == original_index)


def test_engineer_features_rejects_multi_year_data(temp_model_dir):
    """Test that multi-year data raises ValueError for Ramadan features."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    # Create data spanning 2023 and 2024
    timestamps_2023 = pd.date_range(start=datetime(2023, 11, 1), periods=100, freq='H')
    timestamps_2024 = pd.date_range(start=datetime(2024, 1, 1), periods=100, freq='H')
    all_timestamps = timestamps_2023.append(timestamps_2024)
    
    df = pd.DataFrame({
        'timestamp': all_timestamps,
        'value': np.arange(len(all_timestamps))
    })
    df.set_index('timestamp', inplace=True)
    
    with pytest.raises(ValueError, match="multiple years"):
        pipeline.engineer_features(df)


# Model Training Tests

def test_train_models(temp_model_dir, sample_training_data):
    """Test model training step."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    
    # Check that all models are present
    assert 'forecaster' in models
    assert 'baseline_model' in models
    assert 'pattern_learner' in models
    assert 'confidence_scorer' in models
    
    # Check that forecaster is trained
    assert models['forecaster'].is_trained


def test_train_models_forecaster_contains_submodels(temp_model_dir, sample_training_data):
    """Test that forecaster contains trained baseline and pattern learner."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    
    forecaster = models['forecaster']
    
    # Check that forecaster's internal models match returned models
    assert forecaster.baseline_model is models['baseline_model']
    assert forecaster.pattern_learner is models['pattern_learner']
    assert forecaster.confidence_scorer is models['confidence_scorer']


# Model Saving Tests

def test_save_models(temp_model_dir, sample_training_data):
    """Test model saving to disk."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    saved_paths = pipeline.save_models(models)
    
    # Check that forecaster was saved
    assert 'forecaster' in saved_paths
    assert Path(saved_paths['forecaster']).exists()
    
    # Check filename format
    forecaster_path = Path(saved_paths['forecaster'])
    assert forecaster_path.name.startswith('forecaster_test_tenant_')
    assert forecaster_path.suffix == '.pkl'


def test_save_models_creates_latest_symlink(temp_model_dir, sample_training_data):
    """Test that latest symlink is created."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    pipeline.save_models(models)
    
    latest_link = Path(temp_model_dir) / "forecaster_test_tenant_latest.pkl"
    
    assert latest_link.exists()
    assert latest_link.is_symlink()
    assert latest_link.resolve().exists()


def test_save_models_updates_existing_symlink(temp_model_dir, sample_training_data):
    """Test that latest symlink is updated on subsequent saves."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    
    # First save
    saved_paths_1 = pipeline.save_models(models)
    
    # Second save
    saved_paths_2 = pipeline.save_models(models)
    
    # Latest symlink should point to second save
    latest_link = Path(temp_model_dir) / "forecaster_test_tenant_latest.pkl"
    assert latest_link.resolve().samefile(saved_paths_2['forecaster'])


def test_save_models_can_load_saved_model(temp_model_dir, sample_training_data):
    """Test that saved models can be loaded with pickle."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    saved_paths = pipeline.save_models(models)
    
    # Load forecaster
    with open(saved_paths['forecaster'], 'rb') as f:
        loaded_forecaster = pickle.load(f)
    
    # Check that loaded model is functional
    assert loaded_forecaster.is_trained
    assert loaded_forecaster.baseline_model is not None
    assert loaded_forecaster.pattern_learner is not None


# Summary Generation Tests

def test_generate_summary(temp_model_dir, sample_training_data):
    """Test training summary generation."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    saved_paths = pipeline.save_models(models)
    summary = pipeline.generate_summary(df, models, saved_paths)
    
    # Check summary structure
    assert 'tenant_id' in summary
    assert 'training_timestamp' in summary
    assert 'data_stats' in summary
    assert 'model_summaries' in summary
    assert 'saved_models' in summary
    
    # Check data stats
    assert summary['data_stats']['total_points'] == len(df)
    assert summary['data_stats']['days_of_data'] > 0
    
    # Check model summaries
    assert 'forecaster' in summary['model_summaries']


def test_generate_summary_sets_training_timestamp(temp_model_dir, sample_training_data):
    """Test that generate_summary uses training_timestamp from save_models."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    saved_paths = pipeline.save_models(models)
    
    # Training timestamp should be set by save_models
    assert pipeline.training_timestamp is not None
    
    summary = pipeline.generate_summary(df, models, saved_paths)
    
    # Summary should use the same timestamp
    assert summary['training_timestamp'] == pipeline.training_timestamp


def test_print_summary_no_errors(temp_model_dir, sample_training_data, capsys):
    """Test that print_summary executes without errors."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    df = pipeline.engineer_features(sample_training_data)
    models = pipeline.train_models(df)
    saved_paths = pipeline.save_models(models)
    summary = pipeline.generate_summary(df, models, saved_paths)
    
    # Should not raise
    pipeline.print_summary(summary)
    
    # Check that output was printed
    captured = capsys.readouterr()
    assert "TRAINING SUMMARY" in captured.out
    assert "test_tenant" in captured.out


# End-to-End Pipeline Tests

def test_run_end_to_end_with_provided_data(temp_model_dir, sample_training_data):
    """Test complete pipeline execution with provided DataFrame."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=30
    )
    
    summary = pipeline.run(df=sample_training_data)
    
    # Check summary
    assert summary['tenant_id'] == "test_tenant"
    assert summary['data_stats']['total_points'] == len(sample_training_data)
    
    # Check that models were saved
    assert 'forecaster' in summary['saved_models']
    assert Path(summary['saved_models']['forecaster']).exists()


def test_run_insufficient_data_warning(temp_model_dir):
    """Test warning when provided data is less than min_training_days."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=90
    )
    
    # Only 30 days of data during Ramadan 2024 (March 11 - April 9)
    start_date = datetime(2024, 3, 1)  # Before Ramadan start
    hours = 30 * 24
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    values = [100.0 + (i % 24) * 2 for i in range(hours)]  # Add some variation
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'value': values
    })
    df.set_index('timestamp', inplace=True)
    
    # Should warn but still complete
    with pytest.warns(UserWarning, match="Only .* days of data available"):
        summary = pipeline.run(df=df)
    
    assert summary is not None


def test_run_sets_training_summary_attribute(temp_model_dir, sample_training_data):
    """Test that run() sets the training_summary attribute."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    assert pipeline.training_summary == {}
    
    summary = pipeline.run(df=sample_training_data)
    
    assert pipeline.training_summary == summary


def test_run_multiple_tenants_separate_models(temp_model_dir, sample_training_data):
    """Test that different tenants get separate model files."""
    pipeline1 = TrainingPipeline(
        tenant_id="tenant1",
        model_dir=temp_model_dir
    )
    pipeline2 = TrainingPipeline(
        tenant_id="tenant2",
        model_dir=temp_model_dir
    )
    
    summary1 = pipeline1.run(df=sample_training_data)
    summary2 = pipeline2.run(df=sample_training_data)
    
    # Should have different file paths
    assert summary1['saved_models']['forecaster'] != summary2['saved_models']['forecaster']
    
    # Both should exist
    assert Path(summary1['saved_models']['forecaster']).exists()
    assert Path(summary2['saved_models']['forecaster']).exists()
    
    # Check symlinks
    link1 = Path(temp_model_dir) / "forecaster_tenant1_latest.pkl"
    link2 = Path(temp_model_dir) / "forecaster_tenant2_latest.pkl"
    
    assert link1.exists()
    assert link2.exists()


# Edge Cases

def test_empty_dataframe_raises_error(temp_model_dir):
    """Test that empty DataFrame raises ValueError."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    empty_df = pd.DataFrame(columns=['timestamp', 'value'])
    empty_df.set_index('timestamp', inplace=True)
    
    with pytest.raises(ValueError):
        pipeline.run(df=empty_df)


def test_single_data_point_raises_error(temp_model_dir):
    """Test that single data point raises ValueError during training."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    single_point_df = pd.DataFrame({
        'timestamp': [datetime(2024, 2, 1)],
        'value': [100.0]
    })
    single_point_df.set_index('timestamp', inplace=True)
    
    with pytest.raises(ValueError):
        pipeline.run(df=single_point_df)


def test_very_small_dataset(temp_model_dir):
    """Test pipeline with minimal valid dataset."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir,
        min_training_days=10  # Require 10 days minimum
    )
    
    # 7 days of hourly data during Ramadan 2024 (March 11 - April 9)
    start_date = datetime(2024, 3, 12)  # Second day of Ramadan
    hours = 7 * 24
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    values = [100.0 + (i % 24) * 3 for i in range(hours)]  # Add variation
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'value': values
    })
    df.set_index('timestamp', inplace=True)
    
    # Should complete with warning (7 days < 10 days minimum)
    with pytest.warns(UserWarning, match="Only 7 days of data available"):
        summary = pipeline.run(df=df)
    
    assert summary is not None
    assert summary['data_stats']['days_of_data'] == 7
