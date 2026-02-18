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
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from training.train import TrainingPipeline


# Test Fixtures

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
    
    # Simulate traffic patterns with daily seasonality
    values = []
    for ts in timestamps:
        hour = ts.hour
        # Higher traffic during evening hours
        base_value = 100 + (50 * np.sin((hour - 12) * np.pi / 12))
        noise = np.random.normal(0, 10)
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
    """Test that empty DataFrame raises error."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    empty_df = pd.DataFrame(columns=['timestamp', 'value'])
    empty_df.set_index('timestamp', inplace=True)
    
    with pytest.raises(Exception):
        pipeline.run(df=empty_df)


def test_single_data_point_raises_error(temp_model_dir):
    """Test that single data point raises error during training."""
    pipeline = TrainingPipeline(
        tenant_id="test_tenant",
        model_dir=temp_model_dir
    )
    
    single_point_df = pd.DataFrame({
        'timestamp': [datetime(2024, 2, 1)],
        'value': [100.0]
    })
    single_point_df.set_index('timestamp', inplace=True)
    
    with pytest.raises(Exception):
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
