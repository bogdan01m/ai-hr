import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url():
    """Construct database URL from environment variables"""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Fallback: construct from individual components
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "ai_hr")
    db_user = os.getenv("DB_USER", "ai_hr_user")
    db_password = os.getenv("DB_PASSWORD", "ai_hr_password")

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
