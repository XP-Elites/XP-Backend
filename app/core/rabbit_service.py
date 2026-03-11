import aio_pika

from core.util import get_var


class RabbitService:
    def __init__(self, host: str):
        self._host = host
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractRobustChannel | None = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(host=self._host)
        self._channel = await self._connection.channel()

    def is_ok(self) -> bool:
        return self._connection.connected.is_set()

    async def close(self):
        # noinspection PyBroadException
        try:
            await self._channel.close()
            await self._connection.close()
        except Exception:
            pass

    @property
    def channel(self) -> aio_pika.abc.AbstractRobustChannel:
        if self._channel is None:
            raise RuntimeError("RabbitService not connected")
        return self._channel


async def create_rabbit_from_env():
    rabbit_host = get_var("XP_WEBSERVER_RABBIT_HOST")
    rabbit_service = RabbitService(host=rabbit_host)
    await rabbit_service.connect()
    return rabbit_service
