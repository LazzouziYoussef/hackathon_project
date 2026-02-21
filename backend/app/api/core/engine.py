import sys
import os
from datetime import datetime

# Ensuring ml_engine is importable
# Goes up: core -> api -> app -> backend -> hackathon_project
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if BASE_PATH not in sys.path:
    sys.path.append(BASE_PATH)


from ml_engine.models.pattern_learner import RamadanPatternLearner
from ml_engine.preprocessing.feature_engineering import FeatureEngineer
from ml_engine.preprocessing.data_loader import MetricsDataLoader
from backend.app.database import db

class SadaqaBrain:
    def __init__(self):
        self.learner = RamadanPatternLearner()
        self.engineer = FeatureEngineer()
        self.loader = MetricsDataLoader(db)

    async def sync_and_predict(self, tenant_id: str):
        # 1. Load historical data to learn from
        # In a real scenario, start_date would be dynamic based on Ramadan 2026
        df = self.loader.load_historical_metrics(
            tenant_id, 
            start_date="2026-02-17", 
            end_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # 2. Process data using your ML logic
        df_rich = self.engineer.engineer_all_features(df, year=2026)
        
        # 3. Retrain patterns in-memory
        self.learner.learn_surge_patterns(df_rich)
        self.learner.learn_daily_progression(df_rich)
        
        # 4. Get current context for today
        now = datetime.now()
        ramadan_day = self.engineer.ramadan_calendar.get_ramadan_day(now, year=2026)
        
        return {
            "day": ramadan_day,
            "factor": self.learner.get_day_adjustment_factor(ramadan_day) if ramadan_day else 1.0,
            "summary": self.learner.get_pattern_summary()
        }

brain = SadaqaBrain()