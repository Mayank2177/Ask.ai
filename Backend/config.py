from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    MILVUS_HOST: str
    MILVUS_PORT: int
    ALLOWED_ORIGINS: list[str]
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
