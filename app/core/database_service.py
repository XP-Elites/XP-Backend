import logging

from sqlalchemy import NullPool, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from .util import get_logger, get_var

logger = get_logger(__name__, logging.DEBUG)


class Base(DeclarativeBase):
    pass


class DatabaseService:

    def __init__(self, db_url: str):
        self.db_url = db_url
        self._engine: AsyncEngine | None = None
        self._health_engine: AsyncEngine | None = None
        self._SessionLocal: sessionmaker | None = None

    def init(self):
        self._engine = create_async_engine(self.db_url, pool_pre_ping=True, echo=True)
        logger.info("Engine created successfully.")
        self._health_engine = create_async_engine(self.db_url, poolclass=NullPool)
        logger.info("Health engine created successfully.")
        # noinspection PyTypeChecker
        self._SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False, class_=AsyncSession
        )
        logger.info("Session linked to main engine successfully.")
        self.health_engine.connect()
        logger.info(f"DB init ping successful.")

    @property
    def health_engine(self):
        if self._health_engine is None:
            raise RuntimeError("Engine not initialised yet")
        return self._health_engine

    @property
    def engine(self):
        if self._engine is None:
            raise RuntimeError("Engine not initialised yet")
        return self._engine

    def session_local(self) -> sessionmaker[Session]:
        if self._SessionLocal is None:
            raise RuntimeError("Session not initialised yet")
        return self._SessionLocal

    def is_ok(self):
        try:
            self.session_local()().execute(text("SELECT 1;"))
        except Exception as e:
            logger.error(e)
            return False
        return True


def create_db_from_env():
    database_url = (
        f"postgresql+asyncpg://"
        f"{get_var('XP_WEBSERVER_POSTGRES_USER', 'postgres', True)}:"
        f"{get_var('XP_WEBSERVER_POSTGRES_PASSWORD', 'postgres', True)}@"
        f"{get_var('XP_WEBSERVER_POSTGRES_HOST', 'localhost', True)}:"
        f"{get_var('XP_WEBSERVER_POSTGRES_PORT', '5432')}/"
        f"{get_var('XP_WEBSERVER_POSTGRES_DB', 'api')}"
    )
    db = DatabaseService(database_url)
    db.init()
    return db
