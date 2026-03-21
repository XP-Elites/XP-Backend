import os
import logging
import sys

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_ssm.client import SSMClient


def get_logger(name, level: int | str):
    new_logger = logging.getLogger(name)
    new_logger.setLevel(level)
    new_logger.propagate = False
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    new_logger.addHandler(handler)
    return new_logger


logger = get_logger(__name__, logging.DEBUG)

ssm: SSMClient = boto3.client(service_name="ssm", region_name="eu-north-1")


def get_var(name: str, default: str | None = None, use_ssm: bool = False) -> str:
    """Retrieve a required variable from SSM or environment or raise an error if missing."""
    value = os.getenv(name)
    if value is not None:
        logger.debug(f"Retrieved var from env: {name}")
        return value
    if use_ssm:
        try:
            ssm_value = (
                ssm.get_parameter(Name=name, WithDecryption=True)
                .get("Parameter")
                .get("Value")
            )
            if ssm_value is not None:
                logger.debug(f"Retrieved var from SSM: {name}")
                return ssm_value
        except ssm.exceptions.ParameterNotFound:
            pass
        except ClientError as e:
            if e.response["Error"]["Code"] == "AccessDeniedException":
                pass
            else:
                raise
    if default is not None:
        logger.debug(f"Falling back to default: {name}/{default}")
        return default
    raise RuntimeError(f"Required variable '{name}' is not set.")
