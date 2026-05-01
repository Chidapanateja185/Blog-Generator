import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from src.config.database_config import get_database_config
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


load_dotenv()

ENV = os.getenv("ENV", "prod").lower()


# def get_database_url():
#     config = get_database_config()

#     if config.get("DATABASE_URL"):
#         db_url = config["DATABASE_URL"]

#         # if "sslmode" not in db_url:
#         #     db_url += "?sslmode=require"

#         return db_url

#     return (
#         f"postgresql://{config['username']}:"
#         f"{config['password']}@{config['host']}:"
#         f"{config['port']}/{config['database']}"
#     )


def get_database_url():
    config = get_database_config()
    db_url = config.get("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL must be set for production")

    url = urlparse(db_url)
    query = dict(parse_qsl(url.query))
    query.setdefault("sslmode", "require")

    return urlunparse(url._replace(query=urlencode(query)))


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