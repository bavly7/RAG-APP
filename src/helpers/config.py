from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    APP_NAME: str
    VERSION: str

    LIST_FORMATE:list
    MAX_FILE_SIZE : int
    FILE_CHUNCK_SIZE : int
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",  #It controls what happens when Pydantic finds configuration values that aren't defined as fields in your Settings class.
    )

    MONGODB_URL : str
    MONGODB_DATABASE :str


def get_settings():
    return Settings()

# print(BASE_DIR)