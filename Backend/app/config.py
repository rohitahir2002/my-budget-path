import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from Backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    # MongoDB connection: check MONGO_URI or MONGODB_URL
    MONGO_URI: str = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL") or "mongodb://localhost:27017"
    DB_NAME: str = os.getenv("DB_NAME", "budgetpath")

    # JWT Security settings
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "budgetpath_super_secret_jwt_key_2026_secure_key_change_in_production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # CORS origins
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]


settings = Settings()
