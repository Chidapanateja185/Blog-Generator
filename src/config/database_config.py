import os

DATABASE_URLS = {
    "dev": {
        "username": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": "5432",
        "database": "blog_db",
        "DATABASE_URL": None
    },
    "prod": {
        "username": "postgres",
        "password": "nsLeFYCpw9AEeVB4",
        "host": "db.xxxxxx.supabase.co",
        "port": "5432",
        "database": "postgres",
        "DATABASE_URL": "postgresql://neondb_owner:npg_rYiWdOV56Jbn@ep-aged-violet-a4um97tc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    }
}

#postgresql://postgres.btkuwlrezzatyimpsfxa:nsLeFYCpw9AEeVB4@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require

COMMON_DATABASE_CONFIG = {
    "pool_pre_ping": True,
    "pool_size": 2,
    "max_overflow": 5,
    "echo": False
}


def get_database_config():
    ENV = os.getenv("ENV", "prod").lower()

    env_config = DATABASE_URLS.get(ENV, DATABASE_URLS["dev"])

    config = {**COMMON_DATABASE_CONFIG, **env_config}

    config["username"] = os.getenv("DB_USERNAME", config["username"])
    config["password"] = os.getenv("DB_PASSWORD", config["password"])
    config["host"] = os.getenv("DB_HOST", config["host"])
    config["port"] = os.getenv("DB_PORT", config["port"])
    config["database"] = os.getenv("DB_NAME", config["database"])
    config["DATABASE_URL"] = os.getenv("DATABASE_URL", config["DATABASE_URL"])

    return config