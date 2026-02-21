import os
from sqlalchemy import create_engine, text

class DatabaseWrapper:
    def __init__(self):
        self.engine = create_engine("postgresql://sadaqa_admin:your_password_here@localhost:5432/sadaqa_observability")

    def fetch_all(self, query, *args):
        # Maps $1, $2 etc to SQLAlchemy named parameters
        formatted_query = query.replace('$1', ':v1').replace('$2', ':v2').replace('$3', ':v3').replace('$4', ':v4')
        params = {f"v{i+1}": arg for i, arg in enumerate(args)}
        
        with self.engine.connect() as conn:
            result = conn.execute(text(formatted_query), params)
            return result.fetchall()

db = DatabaseWrapper()