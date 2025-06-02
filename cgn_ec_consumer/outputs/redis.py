import json
from typing import Optional

from structlog import get_logger
from redis import Redis

from cgn_ec_consumer.models.enums import NATEventEnum
from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.outputs.redis")


class RedisOutput(BaseOutput):
    def __init__(
        self,
        host: str,
        port: int = 6379,
        key_field: Optional[str] = None,
        key_ttl: Optional[int] = None,
        key_event_map: Optional[dict] = {
            NATEventEnum.SESSION_MAPPING.value: "cgnat:events:sessionmapping",
            NATEventEnum.ADDRESS_MAPPING.value: "cgnat:events:addressmapping",
            NATEventEnum.PORT_MAPPING.value: "cgnat:events:portmapping",
            NATEventEnum.PORT_BLOCK_MAPPING.value: "cgnat:events:portblockmapping",
        },
        redis_extra_config: dict = {},
        preprocessors: list[str] = [],
    ):
        self.host = host
        self.port = port
        self.key_field = key_field
        self.key_ttl = key_ttl
        self.key_event_map = key_event_map
        self.redis_extra_config = redis_extra_config
        self.preprocessors = preprocessors

        self._redis = Redis(host=self.host, port=self.port, **self.redis_extra_config)

    def process_metrics(self, metrics: list[dict]) -> bool:
        try:
            for metric in metrics:
                event_type = self.key_event_map.get(
                    metric.get("type", ""), "cgnat:events"
                )

                key_value = metric.get(self.key_field, metric["src_ip"])
                key = f"{event_type}:{key_value}"

                value = json.dumps(metric)
                self._redis.set(key, value)

                if self.key_ttl:
                    self._redis.expire(key, self.key_ttl)

            logger.debug(f"Processed {len(metrics)} metrics to Redis")
            return True

        except Exception as err:
            logger.error("Failed to process metrics to Redis", exception=str(err))
            return False
