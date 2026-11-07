from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    APP_NAME: str
    VERSION: str

    LIST_FORMATE: list
    MAX_FILE_SIZE: int
    FILE_CHUNCK_SIZE: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    MONGODB_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    # API keys / URLs
    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None
    GROQ_API_KEY: str = None          # <-- ADDED

    # Models
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None

    # Generation defaults (spelling fixed: DEFAULT)
    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

    # Groq-specific optional settings
    TOP_P: float = 1.0                # <-- default added
    STOP: list[str] = []
    STREAMING: bool = False           # <-- default added

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str = None

    

    DEFAULT_LANGUAGE : str = "en"
    PRIMARY_LANGWAGE :str = "en"



def get_settings():
    return Settings()