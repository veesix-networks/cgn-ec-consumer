import json
from typing import Optional

from structlog import get_logger
from kafka import KafkaProducer

from cgn_ec_models.enums import NATEventEnum
from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.outputs.kafka")


class KafkaOutput(BaseOutput):
    def __init__(
        self,
        bootstrap_servers: str,
        topic: Optional[str] = None,
        default_topic: str = "cgnat.events",
        topic_event_map: Optional[dict] = {
            NATEventEnum.SESSION_MAPPING.value: "cgnat.events.sessionmapping",
            NATEventEnum.ADDRESS_MAPPING.value: "cgnat.events.addressmapping",
            NATEventEnum.PORT_MAPPING.value: "cgnat.events.portmapping",
            NATEventEnum.PORT_BLOCK_MAPPING.value: "cgnat.events.portblockmapping",
        },
        key_field: Optional[str] = None,
        producer_extra_config: dict = {},
        preprocessors: list[str] = [],
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.default_topic = default_topic
        self.topic_event_map = topic_event_map
        self.key_field = key_field
        self.producer_extra_config = producer_extra_config
        self.preprocessors = preprocessors

        self._producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            **self.producer_extra_config,
        )

    def process_metrics(self, metrics: list[dict]):
        try:
            for metric in metrics:
                key = None
                if self.key_field:
                    key_value = metric.get(self.key_field)
                    if key_value is not None:
                        key = str(key_value).encode("utf-8")
                    else:
                        logger.debug(
                            f"Key field '{self.key_field}' not found in metric, using default partitioning"
                        )

                if not self.topic and not self.topic_event_map:
                    self.topic = self.default_topic

                if (event_type := metric.get("type")) and not self.topic:
                    logger.info(event_type, metric=metric)
                    if topic := self.topic_event_map.get(event_type.value):
                        self.topic = topic
                    else:
                        self.topic = self.default_topic

                self._producer.send(self.topic, value=metric, key=key)
        except Exception as err:
            logger.warning("Unable to process metrics", exception=str(err))
