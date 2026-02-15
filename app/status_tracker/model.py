from enum import Enum

from sqlalchemy import UUID, Column
from sqlalchemy.types import Enum as SQLEnum

from core import Base


class StatusTypes(Enum):
    IN_QUEUE = 0
    PROCESSING = 1
    COMPLETE = 2
    ERROR = 500


class JobStatus(Base):
    __tablename__ = "job_status"

    uuid = Column(UUID, primary_key=True)
    status = Column(SQLEnum(StatusTypes), nullable=False, default=StatusTypes.IN_QUEUE)
