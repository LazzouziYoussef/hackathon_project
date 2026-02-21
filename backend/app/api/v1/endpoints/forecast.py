from fastapi import APIRouter, HTTPException
from backend.app.api.core.engine import brain

router = APIRouter()

@router.get("/recommend/{tenant_id}")
async def get_recommendation(tenant_id: str):
    try:
        data = await brain.sync_and_predict(tenant_id)
        
        factor = data["factor"]
        ramadan_day = data["day"]
        
        # Deterministic Rules based on Project Charter
        recommendation = "STABLE"
        priority = "LOW"
        
        if ramadan_day and ramadan_day >= 21:
            priority = "CRITICAL"
            recommendation = "SCALE_UP_PREEMPTIVE"
            reason = "Final 10 nights of Ramadan detected. Significant surge expected."
        elif factor > 1.2:
            priority = "MEDIUM"
            recommendation = "SCALE_UP_ADVISORY"
            reason = f"Learned traffic factor ({factor}) shows rising trend."
        else:
            reason = "Traffic within seasonal baseline."

        return {
            "tenant_id": tenant_id,
            "ramadan_day": ramadan_day,
            "prediction": {
                "multiplier": round(factor, 2),
                "confidence": data["summary"]["surge_patterns"].get("iftar", {}).get("confidence", 0.6)
            },
            "recommendation": recommendation,
            "priority": priority,
            "reasoning": reason,
            "action_required": recommendation != "STABLE"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))