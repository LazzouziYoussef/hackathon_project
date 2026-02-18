import sys
import os
import pytest

# Add ml_engine to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scaling_calculator import ScalingCalculator, ScalingRecommendation


def test_calculator_initialization_defaults():
    """Test that calculator initializes with correct defaults."""
    calc = ScalingCalculator()
    
    assert calc.capacity_per_pod == 100.0
    assert calc.safety_factor == 1.2
    assert calc.cost_per_replica_per_hour == 0.10
    assert calc.max_replicas == 50
    assert calc.cost_cap_per_hour is None


def test_calculator_initialization_custom():
    """Test that calculator accepts custom configuration."""
    calc = ScalingCalculator(
        capacity_per_pod=200.0,
        safety_factor=1.5,
        cost_per_replica_per_hour=0.25,
        max_replicas=100,
        cost_cap_per_hour=50.0
    )
    
    assert calc.capacity_per_pod == 200.0
    assert calc.safety_factor == 1.5
    assert calc.cost_per_replica_per_hour == 0.25
    assert calc.max_replicas == 100
    assert calc.cost_cap_per_hour == 50.0


def test_calculator_validation_capacity_per_pod():
    """Test that invalid capacity_per_pod raises ValueError."""
    with pytest.raises(ValueError, match="capacity_per_pod must be > 0"):
        ScalingCalculator(capacity_per_pod=0)
    
    with pytest.raises(ValueError, match="capacity_per_pod must be > 0"):
        ScalingCalculator(capacity_per_pod=-10)


def test_calculator_validation_safety_factor():
    """Test that safety_factor must be >= 1.0."""
    with pytest.raises(ValueError, match="safety_factor must be >= 1.0"):
        ScalingCalculator(safety_factor=0.9)
    
    # Should work with exactly 1.0
    calc = ScalingCalculator(safety_factor=1.0)
    assert calc.safety_factor == 1.0


def test_calculator_validation_cost():
    """Test that cost_per_replica_per_hour must be >= 0."""
    with pytest.raises(ValueError, match="cost_per_replica_per_hour must be >= 0"):
        ScalingCalculator(cost_per_replica_per_hour=-0.01)
    
    # Should work with 0
    calc = ScalingCalculator(cost_per_replica_per_hour=0.0)
    assert calc.cost_per_replica_per_hour == 0.0


def test_calculator_validation_max_replicas():
    """Test that max_replicas must be >= 1."""
    with pytest.raises(ValueError, match="max_replicas must be >= 1"):
        ScalingCalculator(max_replicas=0)


def test_calculator_validation_cost_cap():
    """Test that cost_cap_per_hour must be >= 0 or None."""
    with pytest.raises(ValueError, match="cost_cap_per_hour must be >= 0 or None"):
        ScalingCalculator(cost_cap_per_hour=-10.0)
    
    # Should work with None
    calc = ScalingCalculator(cost_cap_per_hour=None)
    assert calc.cost_cap_per_hour is None


def test_basic_scaling_calculation():
    """Test basic replica calculation with safety factor."""
    calc = ScalingCalculator(
        capacity_per_pod=100.0,
        safety_factor=1.2
    )
    
    # Predicted: 500 req/s, Current: 3 replicas
    # Base needed: ceil(500 / 100) = 5
    # With safety: ceil(5 * 1.2) = ceil(6.0) = 6
    rec = calc.calculate_recommendation(
        predicted_traffic=500.0,
        current_replicas=3,
        reason="Forecast shows 5× load in 4h"
    )
    
    assert rec.recommended_replicas == 6
    assert rec.current_replicas == 3
    assert rec.predicted_traffic == 500.0
    assert rec.safety_factor == 1.2
    assert rec.capped_at_max is False


def test_scaling_with_fractional_result():
    """Test that fractional results are properly rounded up."""
    calc = ScalingCalculator(
        capacity_per_pod=100.0,
        safety_factor=1.3
    )
    
    # Predicted: 250 req/s
    # Base needed: ceil(250 / 100) = 3
    # With safety: ceil(3 * 1.3) = ceil(3.9) = 4
    rec = calc.calculate_recommendation(
        predicted_traffic=250.0,
        current_replicas=2,
        reason="Test fractional rounding"
    )
    
    assert rec.recommended_replicas == 4


def test_max_replicas_cap():
    """Test that recommendations are capped at MAX_REPLICAS."""
    calc = ScalingCalculator(
        capacity_per_pod=100.0,
        safety_factor=1.2,
        max_replicas=50
    )
    
    # Predicted: 10000 req/s would need 120 replicas, but capped at 50
    rec = calc.calculate_recommendation(
        predicted_traffic=10000.0,
        current_replicas=10,
        reason="Massive traffic surge"
    )
    
    assert rec.recommended_replicas == 50
    assert rec.capped_at_max is True


def test_min_replicas_floor():
    """Test that recommendations respect MIN_REPLICAS = 1."""
    calc = ScalingCalculator(
        capacity_per_pod=100.0,
        safety_factor=1.2
    )
    
    # Very low traffic should still recommend at least 1 replica
    rec = calc.calculate_recommendation(
        predicted_traffic=1.0,
        current_replicas=5,
        reason="Very low traffic"
    )
    
    assert rec.recommended_replicas >= 1


def test_cost_calculation():
    """Test that cost calculations are accurate."""
    calc = ScalingCalculator(
        cost_per_replica_per_hour=0.10
    )
    
    rec = calc.calculate_recommendation(
        predicted_traffic=500.0,
        current_replicas=3,
        reason="Cost calculation test"
    )
    
    # Current: 3 * $0.10 = $0.30/hour
    # Recommended: 6 * $0.10 = $0.60/hour
    # Increase: $0.30/hour
    assert abs(rec.current_cost_per_hour - 0.30) < 0.001
    assert abs(rec.recommended_cost_per_hour - 0.60) < 0.001
    assert abs(rec.cost_increase_per_hour - 0.30) < 0.001


def test_cost_cap_enforcement():
    """Test that cost cap is properly tracked."""
    calc = ScalingCalculator(
        capacity_per_pod=100.0,
        cost_per_replica_per_hour=1.0,
        cost_cap_per_hour=5.0
    )
    
    # Within cap
    rec1 = calc.calculate_recommendation(
        predicted_traffic=300.0,
        current_replicas=2,
        reason="Within cap"
    )
    assert rec1.within_cost_cap is True
    
    # Exceeds cap
    rec2 = calc.calculate_recommendation(
        predicted_traffic=1000.0,
        current_replicas=2,
        reason="Exceeds cap"
    )
    assert rec2.within_cost_cap is False


def test_no_cost_cap():
    """Test that without cost cap, within_cost_cap is always True."""
    calc = ScalingCalculator(
        cost_per_replica_per_hour=10.0,
        cost_cap_per_hour=None
    )
    
    rec = calc.calculate_recommendation(
        predicted_traffic=10000.0,
        current_replicas=1,
        reason="No cap test"
    )
    
    assert rec.within_cost_cap is True


def test_should_scale_with_sufficient_change():
    """Test that should_scale returns True for significant changes."""
    calc = ScalingCalculator()
    
    rec = ScalingRecommendation(
        current_replicas=3,
        recommended_replicas=8,  # Change of 5
        predicted_traffic=500.0,
        capacity_per_pod=100.0,
        safety_factor=1.2,
        cost_per_replica_per_hour=0.10,
        current_cost_per_hour=0.30,
        recommended_cost_per_hour=0.80,
        cost_increase_per_hour=0.50,
        reason="Test",
        within_cost_cap=True
    )
    
    assert calc.should_scale(rec, min_replica_change=2) is True


def test_should_scale_with_insufficient_change():
    """Test that should_scale returns False for small changes (hysteresis)."""
    calc = ScalingCalculator()
    
    rec = ScalingRecommendation(
        current_replicas=5,
        recommended_replicas=6,  # Change of 1
        predicted_traffic=500.0,
        capacity_per_pod=100.0,
        safety_factor=1.2,
        cost_per_replica_per_hour=0.10,
        current_cost_per_hour=0.50,
        recommended_cost_per_hour=0.60,
        cost_increase_per_hour=0.10,
        reason="Test",
        within_cost_cap=True
    )
    
    assert calc.should_scale(rec, min_replica_change=2) is False


def test_should_scale_respects_cost_cap():
    """Test that should_scale returns False if cost cap exceeded."""
    calc = ScalingCalculator()
    
    rec = ScalingRecommendation(
        current_replicas=3,
        recommended_replicas=10,  # Change of 7
        predicted_traffic=1000.0,
        capacity_per_pod=100.0,
        safety_factor=1.2,
        cost_per_replica_per_hour=1.0,
        current_cost_per_hour=3.0,
        recommended_cost_per_hour=10.0,
        cost_increase_per_hour=7.0,
        reason="Test",
        within_cost_cap=False  # Exceeds cap
    )
    
    assert calc.should_scale(rec, min_replica_change=2) is False


def test_recommendation_requires_non_empty_reason():
    """Test that calculate_recommendation requires a non-empty reason."""
    calc = ScalingCalculator()
    
    with pytest.raises(ValueError, match="reason must be a non-empty string"):
        calc.calculate_recommendation(
            predicted_traffic=500.0,
            current_replicas=3,
            reason=""
        )
    
    with pytest.raises(ValueError, match="reason must be a non-empty string"):
        calc.calculate_recommendation(
            predicted_traffic=500.0,
            current_replicas=3,
            reason="   "  # Whitespace only
        )


def test_recommendation_validates_inputs():
    """Test that calculate_recommendation validates all inputs."""
    calc = ScalingCalculator()
    
    # Negative traffic
    with pytest.raises(ValueError, match="predicted_traffic must be >= 0"):
        calc.calculate_recommendation(-100.0, 3, "Test")
    
    # Invalid current replicas
    with pytest.raises(ValueError, match="current_replicas must be >= 1"):
        calc.calculate_recommendation(500.0, 0, "Test")


def test_format_recommendation():
    """Test that recommendation formatting includes all key information."""
    calc = ScalingCalculator()
    
    rec = ScalingRecommendation(
        current_replicas=3,
        recommended_replicas=8,
        predicted_traffic=500.0,
        capacity_per_pod=100.0,
        safety_factor=1.2,
        cost_per_replica_per_hour=0.10,
        current_cost_per_hour=0.30,
        recommended_cost_per_hour=0.80,
        cost_increase_per_hour=0.50,
        reason="Forecast shows 3× load in 4h",
        capped_at_max=False,
        within_cost_cap=True
    )
    
    formatted = calc.format_recommendation(rec)
    
    assert "Scaling Recommendation:" in formatted
    assert "Forecast shows 3× load in 4h" in formatted
    assert "Current replicas: 3" in formatted
    assert "Recommended replicas: 8" in formatted
    assert "500.0 req/s" in formatted
    assert "$0.30/hour" in formatted
    assert "$0.80/hour" in formatted
    assert "$0.50/hour" in formatted or "+0.50" in formatted  # Allow different formatting


def test_format_recommendation_with_warnings():
    """Test that formatting includes warnings for caps."""
    calc = ScalingCalculator(max_replicas=50, cost_cap_per_hour=5.0)
    
    rec = ScalingRecommendation(
        current_replicas=10,
        recommended_replicas=50,
        predicted_traffic=10000.0,
        capacity_per_pod=100.0,
        safety_factor=1.2,
        cost_per_replica_per_hour=1.0,
        current_cost_per_hour=10.0,
        recommended_cost_per_hour=50.0,
        cost_increase_per_hour=40.0,
        reason="Massive surge",
        capped_at_max=True,
        within_cost_cap=False
    )
    
    formatted = calc.format_recommendation(rec)
    
    assert "CAPPED at MAX_REPLICAS" in formatted
    assert "EXCEEDS cost cap" in formatted


def test_get_config_summary():
    """Test that config summary returns all configuration."""
    calc = ScalingCalculator(
        capacity_per_pod=200.0,
        safety_factor=1.5,
        cost_per_replica_per_hour=0.25,
        max_replicas=100,
        cost_cap_per_hour=50.0
    )
    
    config = calc.get_config_summary()
    
    assert config['capacity_per_pod'] == 200.0
    assert config['safety_factor'] == 1.5
    assert config['cost_per_replica_per_hour'] == 0.25
    assert config['max_replicas'] == 100
    assert config['min_replicas'] == 1
    assert config['cost_cap_per_hour'] == 50.0


def test_zero_traffic_handling():
    """Test that zero traffic is handled correctly."""
    calc = ScalingCalculator()
    
    rec = calc.calculate_recommendation(
        predicted_traffic=0.0,
        current_replicas=5,
        reason="Traffic dropped to zero"
    )
    
    # Should recommend at least MIN_REPLICAS (1)
    assert rec.recommended_replicas >= 1


def test_scaling_down_scenario():
    """Test scaling down when traffic decreases."""
    calc = ScalingCalculator(
        capacity_per_pod=100.0,
        safety_factor=1.2
    )
    
    # Current: 10 replicas, Predicted: 200 req/s
    # Needed: ceil(200 / 100) * 1.2 = ceil(2.4) = 3
    rec = calc.calculate_recommendation(
        predicted_traffic=200.0,
        current_replicas=10,
        reason="Traffic decreased significantly"
    )
    
    assert rec.recommended_replicas == 3
    assert rec.cost_increase_per_hour < 0  # Cost savings
