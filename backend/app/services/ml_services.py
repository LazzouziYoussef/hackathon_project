
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.crud.metrices import get_metrices_as_df, insert_scaling_event
from ml_engine.models.pattern_learner import RamadanPatternLearner
from ml_engine.preprocessing.feature_engineering import FeatureEngineer
import numpy as np



class MLservice:
    def __init__(self, db : AsyncSession):
        self.db = db
        self.engineer = FeatureEngineer()
    async def sync_and_predict(self,tenant_id:str):
        df = await get_metrices_as_df(
            self.db,
            tenant_id=tenant_id,
            metric_type="http_requests",
            start="2026-02-18",
            end="2026-03-22"
        )
        print(f">>>>>>>rows from DB :{len(df)}")

        if df.empty:
            return{"message": "no metrics data found for this tenant"}
        
        df = self.engineer.engineer_all_features(df,year="2026",drop_na=False)
        
        print(f"rows after feature_engineering :{len(df)}")#lagro: using manual debugging
        
        learner = RamadanPatternLearner() #using yousef ML-model for learning 
        learner = learner.learn_surge_patterns(df)
        learner = learner.learn_daily_progression(df)
        
        ramdan_df = df[df["ramadan_day"] > 0 ]#felter

        ramadan_day = int(df["ramadan_day"].iloc[-1])
        print(f">> ramadan_day: {ramadan_day}")
        factor = float(learner.get_day_adjustment_factor(ramadan_day))
        summary = self._to_python(learner.get_pattern_summary())
        
        await insert_scaling_event(self.db,{
                "tenant_id": tenant_id,
            "event_type": "SURGE_DETECTED" if factor > 1.2 else "DROP_EXPECTED",
            "current_replicas": 2,                    # pull from k8s or config
            "recommended_replicas": round(2 * factor),
            "confidence": 0.85,
            "reason": f"Ramadan day {ramadan_day}, adjustment factor {factor:.2f}",
            "cost_impact_usd": None
        })

    def _to_python(self,obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: self._to_python(v) for k, v in obj.items()}
        if isinstance(obj, list): return [self._to_python(i) for i in obj]
        return obj