from pydantic_settings import BaseSettings
#from dotenv import load_dotenv


class Settings(BaseSettings):
    DATABASE_URL:str =  "postgresql+asyncpg://sadaqa_admin:your_password_here@localhost:5432/sadaqa_observability"
    
    model_config ={"env_file": ".env"}

settings = Settings()        