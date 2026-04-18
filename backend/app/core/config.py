from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Veritabanı
    database_url: str
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 900
    
    # Güvenlik
    secret_key: str
    
    # Scraper
    scrape_concurrency: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()