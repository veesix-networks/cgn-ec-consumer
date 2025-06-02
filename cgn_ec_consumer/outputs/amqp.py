import json
from typing import Optional

from structlog import get_logger
from amqp import Connection, Message

from cgn_ec_consumer.models.enums import NATEventEnum
from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.outputs.amqp")


class AMQPOutput(BaseOutput):
    def __init__(
        self,
        host: str,
        port: int = 5672,
        virtual_host: str = "/",
        username: Optional[str] = None,
        password: Optional[str] = None,
        exchange: str = "cgnat.events",
        exchange_type: str = "topic",
        routing_key: Optional[str] = None,
        default_routing_key: str = "cgnat.events",
        routing_key_event_map: Optional[dict] = {
            NATEventEnum.SESSION_MAPPING.value: "cgnat.events.sessionmapping",
            NATEventEnum.ADDRESS_MAPPING.value: "cgnat.events.addressmapping",
            NATEventEnum.PORT_MAPPING.value: "cgnat.events.portmapping",
            NATEventEnum.PORT_BLOCK_MAPPING.value: "cgnat.events.portblockmapping",
        },
        connection_extra_config: dict = {},
        preprocessors: list[str] = [],
    ):
        super().__init__(preprocessors)
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.default_routing_key = default_routing_key
        self.routing_key_event_map = routing_key_event_map
        self.connection_extra_config = connection_extra_config

        self._connection = Connection(
            host=self.host,
            port=self.port,
            userid=self.username,
            password=self.password,
            virtual_host=self.virtual_host,
            **self.connection_extra_config,
        )
        self._channel = self._connection.channel()

        # Declare the exchange if it doesn't exist
        self._channel.exchange_declare(
            exchange=self.exchange,
            type=self.exchange_type,
            durable=True,
            auto_delete=False,
        )

    def process_metrics(self, metrics: list[dict]):
        processed_metrics = self._preprocess_metrics(metrics)
        try:
            for metric in processed_metrics:
                current_routing_key = self.routing_key

                if not current_routing_key and self.routing_key_event_map:
                    if event_type := metric.get("type"):
                        if routing_key := self.routing_key_event_map.get(
                            event_type.value
                        ):
                            current_routing_key = routing_key
                        else:
                            current_routing_key = self.default_routing_key

                if not current_routing_key:
                    current_routing_key = self.default_routing_key

                message_body = json.dumps(metric).encode("utf-8")
                self._channel.basic_publish(
                    Message(
                        body=message_body,
                        content_type="application/json",
                        delivery_mode=2,
                    ),
                    exchange=self.exchange,
                    routing_key=current_routing_key,
                )
        except Exception as err:
            logger.warning("Unable to process metrics", exception=str(err))

    def __del__(self):
        try:
            if hasattr(self, "_connection") and self._connection:
                if hasattr(self, "_channel") and self._channel:
                    self._channel.close()
                self._connection.close()
        except Exception as err:
            logger.warning("Error closing AMQP connection", exception=str(err))
