import pandas as pd
from  ml_engine.models.pattern_learner import RamadanPatternLearner
from  ml_engine.preprocessing.feature_engineering import FeatureEngineer

class MLservice:
    def __init__(self):
        self.learner = RamadanPatternLearner()
        self.engineer = FeatureEngineer()

    def get_pattern(self):
        return self.learner.get_pattern_summary(self)
    
    def get_day_adjustement(self, day: int):
        return self.engineer.get_day_adjustement_factor(day)
    
    def predict(self , dt : pd.Timestamp):
        df = pd.DataFrame(index=[dt])
        df = self.engineer.engineer_all_features(df , drop_na=False)
        #simple prediction 
        day_factor = self.learner.get_day_adjustment_factor(df['ramadan_day'].iloc[0])
        value = df['value'].iloc[0] if 'value' in df.columns else 100
        predicted = value*day_factor

        return predicted


