import pandas as pd
from datetime import datetime, timedelta


class MetricsDataLoader:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def load_historical_metrics(self, tenant_id, start_date, end_date, metric_name='requests_per_minute'):
        query = """
        SELECT 
            time,
            value
        FROM metrics
        WHERE tenant_id = $1
          AND metric_type = $2
          AND time >= $3
          AND time <= $4
        ORDER BY time ASC
        """
        
        rows = self.db.fetch_all(query, tenant_id, metric_name, start_date, end_date)
        
        df = pd.DataFrame(rows, columns=['time', 'value'])
        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')
        
        return df
    
    def resample_to_minutely(self, df):
        return df.resample('1T').mean().ffill()
    
    def validate_data_quality(self, df):
        if len(df) == 0:
            raise ValueError("No data available for given parameters")
        
        missing_pct = df['value'].isna().sum() / len(df) * 100
        
        if missing_pct > 20:
            raise ValueError(f"Data quality too low: {missing_pct:.1f}% missing")
        
        return True
