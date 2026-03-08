
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.crud.metrices import get_metrices_as_df
from backend.app.crud.scalling_event import insert_scaling_event 
from backend.app.crud.forcast import  insert_forecast, get_upcoming_forecasts
from ml_engine.forecaster import HybridForecaster
from ml_engine.preprocessing.feature_engineering import FeatureEngineer
from datetime import datetime
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
        
        print(f">>>>>>>rows from DB :{df}")

        if df.empty:
            return{"message": "no metrics data found for this tenant"}
        
        df = self.engineer.engineer_all_features(df,year=2026,drop_na=False)
       
        print(df["ramadan_day"].value_counts().sort_index() )
        print(f"is_ramadan counts: {df['is_ramadan'].value_counts()}")
        print(f"index sample: {df.index[:3]}")

        print(f"rows after feature_engineering :{len(df)}")#lagro: using manual debugging
        
            
        ramdan_df = df[df["ramadan_day"] > 0 ]#felter
        print("ramadan_df",ramdan_df)
        if ramdan_df.empty:       
            return {"message": "NO data damadan data found ", "factor": 1.0,"day": 0}

        forecaster = HybridForecaster()
        forecaster.train(ramdan_df)

        current_time = ramdan_df.index[-1].to_pydatetime()
        current_traffic = float(ramdan_df["value"].iloc[-1])
        print("current_time",current_time)

        forecast_results = forecaster.forecast(
            current_time=current_time,
            current_traffic=current_traffic,
            historical_df=ramdan_df
        )

        if forecast_results:
            await insert_forecast(self.db,
                tenant_id,
                [
                    {
                        "forecast_time": f.event_time,
                        "metric_type": "http_requests",
                        "predicted_value": f.predicted_traffic,
                        "confidence": f.confidence,
                        "model_version": f"v1.0-{'ml' if f.used_ml else 'baseline'}"
                    }
                    for f in forecast_results
                ])

        learner = forecaster.pattern_learner
        current_day = int(ramdan_df["ramadan_day"].iloc[-1])
        factor = float(learner.get_day_adjustment_factor(current_day))
        confidence = forecast_results[0].confidence if forecast_results else 0.7
 


            # full_data.append({
            # "day": int(day),
            # "factor": factor,
            # "event_type": "SURGE_DETECTED" if factor > 1.2 else "DROP_EXPECTED",
            # "recommended_replicas": round(2 * factor)
            #  })
            
        await insert_scaling_event(self.db,{
            "tenant_id": tenant_id,
            "event_type": "SURGE_DETECTED" if factor > 1.2 else "DROP_EXPECTED",
            "current_replicas": 2,
            "recommended_replicas": round(2 * factor),
            "confidence": confidence,
            "reason": f"Ramadan day {current_day}, factor {factor:.2f}",
            "cost_impact_usd": None
        })
        
        stored_forcast = await get_upcoming_forecasts(self.db,tenant_id)

        
        return {
            "current_day": current_day,
            "current_factor": factor,
            "model_summary": self._to_python(forecaster.get_model_summary()),
            "upcoming_forecasts": [
                {
                    "event": f.event_name,
                    "event_time": f.event_time.isoformat(),
                    "predicted_traffic": round(f.predicted_traffic, 2),
                    "confidence": round(f.confidence, 3),
                    "confidence_level": forecaster.confidence_scorer.get_confidence_level(f.confidence),
                    "time_to_impact_hours": round(f.time_to_impact, 2),
                    "model_used": "pattern_learner" if f.used_ml else "seasonal_baseline",
                    "recommended_replicas": round(2 * f.multiplier)
                }
                for f in forecast_results
            ],
            "stored_forecasts_count": len(stored_forcast)
        }


    def _to_python(self,obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: self._to_python(v) for k, v in obj.items()}
        if isinstance(obj, list): return [self._to_python(i) for i in obj]
        return obj