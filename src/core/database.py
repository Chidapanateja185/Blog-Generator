import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from src.config.database_config import get_database_config
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


load_dotenv()

ENV = os.getenv("ENV", "prod").lower()


def get_database_url():
    config = get_database_config()
    db_url = config.get("DATABASE_URL")

    if db_url:
        return db_url

    return (
        f"postgresql://{config['username']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )



config = get_database_config()
DATABASE_URL = get_database_url()

print("🔗 DATABASE URL:", DATABASE_URL)  


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=config["pool_pre_ping"],
    pool_size=config["pool_size"],
    max_overflow=config["max_overflow"],
    echo=config["echo"]
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