
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.crud.metrices import get_metrices_as_df, insert_scaling_event
from ml_engine.models.pattern_learner import RamadanPatternLearner
from ml_engine.preprocessing.feature_engineering import FeatureEngineer
from uuid import UUID
import numpy as np



class MLservice:
    def __init__(self, db : AsyncSession):
        self.db = db
        self.engineer = FeatureEngineer()
    async def sync_and_predict(self,tenant_id:UUID):
        df = await get_metrices_as_df(
            self.db,
            tenant_id=tenant_id,
            metric_type="http_requests",
            start="2026-02-18",
            end="2026-03-22"
        )
        full_data = []
        print(f">>>>>>>rows from DB :{df}")

        if df.empty:
            return{"message": "no metrics data found for this tenant"}
        
        df = self.engineer.engineer_all_features(df,year=2026,drop_na=False)
        # add these prints
        print(df["ramadan_day"].value_counts().sort_index() )
        print(f"is_ramadan counts: {df['is_ramadan'].value_counts()}")
        print(f"index sample: {df.index[:3]}")

        print(f"rows after feature_engineering :{len(df)}")#lagro: using manual debugging
        
        learner = RamadanPatternLearner() #using yousef ML-model for learning 
        learner.learn_surge_patterns(df)
        learner.learn_daily_progression(df)
        
        ramdan_df = df[df["ramadan_day"] > 0 ]#felter
        print("ramadan_df",ramdan_df)
        if ramdan_df.empty:
            return {"message": "NO data damadan data found ", "factor": 1.0,"day": 0}
        for day in sorted(ramdan_df["ramadan_day"].unique()):
            factor = float(learner.get_day_adjustment_factor(day))
            full_data.append({
            "day": int(day),
            "factor": factor,
            "event_type": "SURGE_DETECTED" if factor > 1.2 else "DROP_EXPECTED",
            "recommended_replicas": round(2 * factor)
             })

    # Save scaling event for the current/last Ramadan day
        current_day = int(ramdan_df["ramadan_day"].iloc[-1])
        current_factor = float(learner.get_day_adjustment_factor(current_day))

        await insert_scaling_event(self.db,{
                "tenant_id": tenant_id,
            "event_type": "SURGE_DETECTED" if factor > 1.2 else "DROP_EXPECTED",
            "current_replicas": 2,                    # pull from k8s or config
            "recommended_replicas": round(2 * factor),
            "confidence": 0.85,
            "reason": f"Ramadan day {ramdan_df}, adjustment factor {factor:.2f}",
            "cost_impact_usd": None
        })
    
    
        
        return {" ": full_data}

    def _to_python(self,obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: self._to_python(v) for k, v in obj.items()}
        if isinstance(obj, list): return [self._to_python(i) for i in obj]
        return obj