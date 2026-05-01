import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from typing import Generator
from src.config.database_config import get_database_config

load_dotenv()

ENV = os.getenv("ENV", "prod").lower()


def get_database_url():
    config = get_database_config()

    # ✅ Use Supabase URL directly if available
    if config.get("DATABASE_URL"):
        db_url = config["DATABASE_URL"]

        # Fix SSL param properly
        if "sslmode" not in db_url:
            if "?" in db_url:
                db_url += "&sslmode=require"
            else:
                db_url += "?sslmode=require"

        return db_url

    # fallback (dev/local)
    return (
        f"postgresql://{config['username']}:"
        f"{config['password']}@{config['host']}:"
        f"{config['port']}/{config['database']}"
    )


config = get_database_config()
DATABASE_URL = get_database_url()

print("🔗 DATABASE URL:", DATABASE_URL)


# ✅ FIXED ENGINE (Cloud Run + Supabase safe)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool, 
    pool_pre_ping=True,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10
    }
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)