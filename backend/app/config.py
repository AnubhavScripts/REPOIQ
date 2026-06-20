from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    DATABASE_URL:str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION:str

    GEMINI_API_KEY: str
    GEMINI_EMBEDDING_MODEL: str

    GROQ_API_KEY: str
    GROQ_MODEL: str
    
    DEBUG: bool
    MAX_REPO_SIZE_MB: int
    MAX_FILES: int
    MAX_CHUNKS: int 

    TEMP_REPO_PATH: str

    ENVIRONMENT: str

settings=Settings()
