"""Scaling Calculator for Sadaqa Tech ML Engine.

Calculates required replica counts and cost impacts for scaling recommendations.
Implements safety constraints and cost caps per system design.

Core principle: Prediction before automation. No auto-scaling.
"""
from dataclasses import dataclass
from typing import Optional
import math


@dataclass
class ScalingRecommendation:
    """Scaling recommendation with full transparency and cost impact.
    
    Attributes:
        current_replicas: Current number of replicas
        recommended_replicas: Recommended number of replicas
        predicted_traffic: Predicted traffic (requests/second)
        capacity_per_pod: Capacity per pod (requests/second)
        safety_factor: Safety multiplier applied (default: 1.2)
        cost_per_replica_per_hour: Cost of one replica per hour ($)
        current_cost_per_hour: Current cost per hour ($)
        recommended_cost_per_hour: Recommended cost per hour ($)
        cost_increase_per_hour: Additional cost per hour ($)
        reason: Human-readable justification for recommendation
        capped_at_max: Whether recommendation was capped at MAX_REPLICAS
        within_cost_cap: Whether recommendation is within cost cap
    """
    current_replicas: int
    recommended_replicas: int
    predicted_traffic: float
    capacity_per_pod: float
    safety_factor: float
    cost_per_replica_per_hour: float
    current_cost_per_hour: float
    recommended_cost_per_hour: float
    cost_increase_per_hour: float
    reason: str
    capped_at_max: bool = False
    within_cost_cap: bool = True


class ScalingCalculator:
    """Calculate scaling recommendations with safety constraints and cost impact.
    
    Implements the decision engine's replica calculation logic:
    - needed_replicas = ceil(predicted_traffic / capacity_per_pod) * safety_factor
    - Cap at MAX_REPLICAS = 50
    - Calculate cost impact
    - Enforce cost caps
    
    All recommendations require human approval (no auto-execution).
    """
    
    # Safety constraints from system design
    MAX_REPLICAS = 50
    MIN_REPLICAS = 1
    DEFAULT_SAFETY_FACTOR = 1.2  # 20% headroom
    DEFAULT_CAPACITY_PER_POD = 100.0  # requests/second
    DEFAULT_COST_PER_REPLICA_PER_HOUR = 0.10  # $0.10/replica/hour
    
    def __init__(
        self,
        capacity_per_pod: float = DEFAULT_CAPACITY_PER_POD,
        safety_factor: float = DEFAULT_SAFETY_FACTOR,
        cost_per_replica_per_hour: float = DEFAULT_COST_PER_REPLICA_PER_HOUR,
        max_replicas: int = MAX_REPLICAS,
        cost_cap_per_hour: Optional[float] = None
    ):
        """Initialize scaling calculator with configuration.
        
        Args:
            capacity_per_pod: Capacity per pod in requests/second
            safety_factor: Safety multiplier (>= 1.0) for headroom
            cost_per_replica_per_hour: Cost per replica per hour in dollars
            max_replicas: Maximum allowed replicas (safety cap)
            cost_cap_per_hour: Optional cost cap per hour in dollars
        
        Raises:
            ValueError: If configuration values are invalid
        """
        if capacity_per_pod <= 0:
            raise ValueError(f"capacity_per_pod must be > 0, got {capacity_per_pod}")
        if safety_factor < 1.0:
            raise ValueError(f"safety_factor must be >= 1.0, got {safety_factor}")
        if cost_per_replica_per_hour < 0:
            raise ValueError(f"cost_per_replica_per_hour must be >= 0, got {cost_per_replica_per_hour}")
        if max_replicas < 1:
            raise ValueError(f"max_replicas must be >= 1, got {max_replicas}")
        if cost_cap_per_hour is not None and cost_cap_per_hour < 0:
            raise ValueError(f"cost_cap_per_hour must be >= 0 or None, got {cost_cap_per_hour}")
        
        self.capacity_per_pod = capacity_per_pod
        self.safety_factor = safety_factor
        self.cost_per_replica_per_hour = cost_per_replica_per_hour
        self.max_replicas = max_replicas
        self.cost_cap_per_hour = cost_cap_per_hour
    
    def calculate_recommendation(
        self,
        predicted_traffic: float,
        current_replicas: int,
        reason: str
    ) -> ScalingRecommendation:
        """Calculate scaling recommendation for predicted traffic.
        
        Args:
            predicted_traffic: Predicted traffic in requests/second
            current_replicas: Current number of replicas
            reason: Human-readable justification (e.g., "Forecast shows 3× load in 4h")
        
        Returns:
            ScalingRecommendation with full cost impact and justification
        
        Raises:
            ValueError: If inputs are invalid or reason is empty
        """
        if predicted_traffic < 0:
            raise ValueError(f"predicted_traffic must be >= 0, got {predicted_traffic}")
        if current_replicas < 1:
            raise ValueError(f"current_replicas must be >= 1, got {current_replicas}")
        if not reason or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        
        # Calculate needed replicas with safety factor
        # Formula: ceil(predicted_traffic / capacity_per_pod) * safety_factor
        base_replicas = math.ceil(predicted_traffic / self.capacity_per_pod)
        needed_replicas = math.ceil(base_replicas * self.safety_factor)
        
        # Apply minimum constraint
        needed_replicas = max(self.MIN_REPLICAS, needed_replicas)
        
        # Check if capped at max
        capped_at_max = needed_replicas > self.max_replicas
        recommended_replicas = min(needed_replicas, self.max_replicas)
        
        # Calculate costs
        current_cost = current_replicas * self.cost_per_replica_per_hour
        recommended_cost = recommended_replicas * self.cost_per_replica_per_hour
        cost_increase = recommended_cost - current_cost
        
        # Check cost cap
        within_cost_cap = True
        if self.cost_cap_per_hour is not None:
            within_cost_cap = recommended_cost <= self.cost_cap_per_hour
        
        return ScalingRecommendation(
            current_replicas=current_replicas,
            recommended_replicas=recommended_replicas,
            predicted_traffic=predicted_traffic,
            capacity_per_pod=self.capacity_per_pod,
            safety_factor=self.safety_factor,
            cost_per_replica_per_hour=self.cost_per_replica_per_hour,
            current_cost_per_hour=current_cost,
            recommended_cost_per_hour=recommended_cost,
            cost_increase_per_hour=cost_increase,
            reason=reason.strip(),
            capped_at_max=capped_at_max,
            within_cost_cap=within_cost_cap
        )
    
    def should_scale(
        self,
        recommendation: ScalingRecommendation,
        min_replica_change: int = 2
    ) -> bool:
        """Determine if scaling action should be recommended.
        
        Applies hysteresis to avoid thrashing on small changes.
        
        Args:
            recommendation: ScalingRecommendation to evaluate
            min_replica_change: Minimum replica change to recommend scaling
        
        Returns:
            True if scaling should be recommended, False otherwise
        """
        replica_change = abs(recommendation.recommended_replicas - recommendation.current_replicas)
        
        # Don't recommend if change is below threshold
        if replica_change < min_replica_change:
            return False
        
        # Don't recommend if exceeds cost cap
        if not recommendation.within_cost_cap:
            return False
        
        return True
    
    def format_recommendation(self, recommendation: ScalingRecommendation) -> str:
        """Format recommendation as human-readable string for logging/alerts.
        
        Args:
            recommendation: ScalingRecommendation to format
        
        Returns:
            Formatted string with all relevant information
        """
        lines = [
            f"Scaling Recommendation:",
            f"  Reason: {recommendation.reason}",
            f"  Current replicas: {recommendation.current_replicas}",
            f"  Recommended replicas: {recommendation.recommended_replicas}",
            f"  Predicted traffic: {recommendation.predicted_traffic:.1f} req/s",
            f"  Capacity per pod: {recommendation.capacity_per_pod:.1f} req/s",
            f"  Safety factor: {recommendation.safety_factor:.2f}",
            f"  Current cost: ${recommendation.current_cost_per_hour:.2f}/hour",
            f"  Recommended cost: ${recommendation.recommended_cost_per_hour:.2f}/hour",
            f"  Cost impact: ${recommendation.cost_increase_per_hour:+.2f}/hour",
        ]
        
        if recommendation.capped_at_max:
            lines.append(f"  ⚠️  CAPPED at MAX_REPLICAS ({self.max_replicas})")
        
        if not recommendation.within_cost_cap:
            lines.append(f"  ❌ EXCEEDS cost cap (${self.cost_cap_per_hour:.2f}/hour)")
        
        return "\n".join(lines)
    
    def get_config_summary(self) -> dict:
        """Get current calculator configuration.
        
        Returns:
            Dictionary with current configuration values
        """
        return {
            'capacity_per_pod': self.capacity_per_pod,
            'safety_factor': self.safety_factor,
            'cost_per_replica_per_hour': self.cost_per_replica_per_hour,
            'max_replicas': self.max_replicas,
            'min_replicas': self.MIN_REPLICAS,
            'cost_cap_per_hour': self.cost_cap_per_hour
        }
