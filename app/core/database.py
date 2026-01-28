import dotenv
from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker
import os

dotenv.load_dotenv()


def _get_env_var(name: str) -> str:
    """Retrieve a required environment variable or raise a clear error if missing."""
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Required environment variable '{name}' is not set.")
    return value


DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{_get_env_var('POSTGRES_USER')}:"
    f"{_get_env_var('POSTGRES_PASSWORD')}@"
    f"{_get_env_var('POSTGRES_HOST')}:"
    f"{_get_env_var('POSTGRES_PORT')}/"
    f"{_get_env_var('POSTGRES_DB')}"
)

engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5}
)

health_engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 1},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
