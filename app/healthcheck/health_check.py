import time

from sqlalchemy.exc import OperationalError

from core import health_engine


def database_latency():
    start = time.monotonic()
    try:
        with health_engine.connect():
            pass
    except OperationalError:
        return None
    return round(time.monotonic() - start, 2)
