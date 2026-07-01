"""
db_config.py
Central place for database connection settings.
Reads from .env file so credentials are never hardcoded.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "autoparts_ops")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_engine():
    """Returns a SQLAlchemy engine. Reused across the app (connection pooling)."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)
