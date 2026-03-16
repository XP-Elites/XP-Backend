import logging
from uuid import UUID

from aio_pika.abc import (
    AbstractRobustQueue,
    AbstractIncomingMessage,
    AbstractRobustExchange,
)
from aio_pika import Message, DeliveryMode, ExchangeType
from edwh_uuid7 import uuid7
from sqlalchemy import update, select

from core import RabbitService, DatabaseService
from .model import JobStatus, StatusTypes


class JobStatusService:
    def __init__(self, session: DatabaseService, rabbit_service: RabbitService):
        self._database_service = session
        self._rabbit_service = rabbit_service
        self._job_queue: AbstractRobustQueue | None = None
        self._status_queue: AbstractRobustQueue | None = None
        self._exchange: AbstractRobustExchange | None = None

    async def init(self):
        self._exchange = await self._rabbit_service.channel.declare_exchange(
            "processing", ExchangeType.DIRECT
        )

        self._job_queue = await self._rabbit_service.channel.declare_queue(
            "jobs", durable=True
        )
        self._status_queue = await self._rabbit_service.channel.declare_queue(
            "status", durable=True
        )

        await self._job_queue.bind(self._exchange, "jobs")
        await self._status_queue.bind(self._exchange, "status")

        await self._status_queue.consume(callback=self.change_status_from_message)

    async def get_status(self, uuid: UUID) -> JobStatus | None:
        async with self._database_service.session_local()() as session:
            result = await session.execute(
                select(JobStatus).where(JobStatus.uuid == uuid)
            )
            return result.scalar_one_or_none()

    async def init_status(self) -> UUID:
        uuid = uuid7()  # V7 UUID with timestamp info
        async with self._database_service.session_local()() as session:
            session.add(JobStatus(uuid=uuid))
            await session.commit()
        logging.info(f"New job created: {uuid}")
        return uuid

    async def progress_to_in_queue(self, uuid: UUID):
        logging.info(f"Sending to queue: {uuid}")
        async with self._database_service.session_local()() as session:
            query = (
                update(JobStatus)
                .where(JobStatus.uuid == uuid)
                .values(status=StatusTypes.IN_QUEUE)
            )
            await session.execute(query)
            await session.commit()

    async def change_status_from_message(self, message: AbstractIncomingMessage):
        result = message.body.decode().split("//", 1)
        logging.info(f"Received status update: {result}")
        if len(result) != 2:
            raise ValueError(
                f"Invalid message body format: {message.body!r}, expected '<uuid>/<status>'"
            )
        uuid, status = UUID(result[0]), StatusTypes(int(result[1]))
        async with self._database_service.session_local()() as session:
            query = (
                update(JobStatus).where(JobStatus.uuid == uuid).values(status=status)
            )
            await session.execute(query)
            await session.commit()
        await message.ack()

    async def send_job(self, uuid: UUID):
        message = Message(uuid.bytes, delivery_mode=DeliveryMode.PERSISTENT)
        await self._exchange.publish(message, routing_key="jobs")
        await self.progress_to_in_queue(uuid)


async def create_job_status_service(
    database_service: DatabaseService, rabbit_service: RabbitService
):
    service = JobStatusService(database_service, rabbit_service)
    await service.init()
    return service
