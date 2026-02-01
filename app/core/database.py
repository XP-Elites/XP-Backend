import boto3
import dotenv
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, NullPool
from mypy_boto3_ssm import SSMClient
from sqlalchemy.orm import sessionmaker
import os

dotenv.load_dotenv()


def _get_var(name: str, default: str | None = None) -> str:
    """Retrieve a required variable from SSM or environment or raise an error if missing."""

    value = os.getenv(name)
    if value is not None:
        return value
    try:
        ssm_value = (ssm.get_parameter(Name=name, WithDecryption=True)
                     .get("Parameter")
                     .get("Value"))
        if ssm_value is not None:
            return ssm_value
    except ssm.exceptions.ParameterNotFound:
        pass
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDeniedException":
            pass
        else:
            raise
    if default is not None:
        return default
    raise RuntimeError(f"Required environment variable '{name}' is not set.")

ssm: SSMClient = boto3.client("ssm")


DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{_get_var('XP_WEBSERVER_POSTGRES_USER', 'postgres')}:"
    f"{_get_var('XP_WEBSERVER_POSTGRES_PASSWORD','postgres')}@"
    f"{_get_var('XP_WEBSERVER_POSTGRES_HOST', 'localhost')}:"
    f"{_get_var('XP_WEBSERVER_POSTGRES_PORT','5432')}/"
    f"{_get_var('XP_WEBSERVER_POSTGRES_DB','api')}"
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
