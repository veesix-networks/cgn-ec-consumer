__all__ = [
    "HTTPWebhookOutput",
    "TimeScaleDBOutput",
    "KafkaOutput",
    "RedisOutput",
    "AMQPOutput",
]

from cgn_ec_consumer.outputs.http import HTTPWebhookOutput
from cgn_ec_consumer.outputs.timescaledb import TimeScaleDBOutput
from cgn_ec_consumer.outputs.kafka import KafkaOutput
from cgn_ec_consumer.outputs.redis import RedisOutput
from cgn_ec_consumer.outputs.amqp import AMQPOutput
