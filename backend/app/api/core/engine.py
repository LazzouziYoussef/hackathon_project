from ml_engine.preprocessing.data_loader import MetricsDataLoader
from ml_engine.preprocessing.feature_engineering import FeatureEngineer
from ml_engine.models.pattern_learner import RamadanPatternLearner
import numpy as np

class MLservice:
    def __init__(self,db_connection):
        self.db = db_connection
        self.loader = MetricsDataLoader(db_connection)
        self.engineer = FeatureEngineer()

    async def sync_and_predict(self,tenant_id):
        df = self.loader.load_historical_metrics(tenant_id=tenant_id,start_date="2026-01-01",end_date="2026-03-22")
        df = self.loader.resample_to_minutely(df)
        self.loader.validate_data_quality(df)

        df = self.engineer.engineer_all_features(df, year="2026")

        learner = RamadanPatternLearner()
        learner.learn_surge_patterns(df)
        learner.learn_daily_progression(df)

        summary = learner.get_pattern_summary()
        #calculate currne adjustement
        print(df.head())
        print(df.columns)
        print(df.shape) 
        ramadan_day = df["ramadan_day"].iloc[-1]
        factor  = learner.get_day_adjustment_factor(ramadan_day)

        return  {"factor": self._to_python(factor), "day": self._to_python(ramadan_day),"summary": self._to_python(summary)}

    def _to_python(self, obj):
        """Recursively convert numpy types to native Python types."""
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: self._to_python(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._to_python(i) for i in obj]
        return obj

class MockDB:
    def fetch_all(self, query, tenant_id, metric_name, start, end):
        import pandas as pd
        import numpy as np
        dates = pd.date_range(start=start, end=end, freq="min")
        values = np.random.randint(50, 500, len(dates))
        return list(zip(dates, values))

brain = MLservice(db_connection=MockDB())        

