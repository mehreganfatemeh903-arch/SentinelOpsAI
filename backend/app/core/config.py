from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name:str='SentinelOps AI'
    environment:str='development'
    database_url:str='postgresql+psycopg://sentinelops:sentinelops@db:5432/sentinelops'
    jwt_secret:str='change-me-in-production-use-32-plus-random-chars'
    access_token_expire_minutes:int=60
    model_config=SettingsConfigDict(env_file='.env', extra='ignore')
settings=Settings()
