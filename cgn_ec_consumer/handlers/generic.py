from abc import ABC, abstractmethod
from datetime import datetime
from structlog import get_logger
import re

from cgn_ec_consumer.models.enums import NATEventEnum

from cgn_ec_consumer.outputs.base import BaseOutput

try:
    from cgn_ec_rust_parsers import RegexMatcher

    HAS_RUST_BINDINGS = True
except ImportError:
    HAS_RUST_BINDINGS = False

logger = get_logger("cgn-ec.handlers.generic")
logger.debug("Checking status of rust bindings", HAS_RUST_BINDINGS=HAS_RUST_BINDINGS)


class BaseHandler(ABC):
    TOPIC = None
    PARSER = None

    def __init__(self, outputs: list[BaseOutput] = []):
        logger.info(f"Loading Handler: {self.__class__.__name__}")
        output_info = []
        for x in outputs:
            class_name = x.__class__.__name__
            if len(x.preprocessors) > 0:
                preprocessor_names = ", ".join(
                    [preprocessor.name for preprocessor in x.preprocessors]
                )
                output_info.append(
                    f"{class_name} ({len(x.preprocessors)} preprocessors - {preprocessor_names})"
                )
            else:
                output_info.append(class_name)

        logger.info(f"Outputs loaded: {', '.join(output_info)}")
        self._outputs = outputs

    @abstractmethod
    def parse_message(self, message: str) -> dict:
        raise NotImplementedError("parse_message not implemented")

    def parse_messages_batch(self, messages: list[dict]) -> list[dict]:
        metrics = []
        for message in messages:
            metric = self.parse_message(message)
            if metric:
                metrics.append(metric)
        return metrics

    def process_outputs(self, metrics: list[dict]):
        for output in self._outputs:
            if output.preprocessors:
                metrics = output._preprocess_metrics(metrics)

            if not metrics:
                continue

            output.process_metrics(metrics)


class BaseSyslogHandler(BaseHandler):
    pass


class BaseNetFlowBaseHandler(BaseHandler):
    pass


class GenericNetFlowV9Handler(BaseHandler):
    pass


class GenericRADIUSAccountingHandler(BaseHandler):
    pass


class GenericSyslogHandler(BaseHandler):
    DEFAULT_REGEX_PATTERNS = []
    PATTERNS = []

    def __init__(
        self,
        regex_patterns: list[dict] = [],
        *args,
        **kwargs,
    ):
        self.regex = None
        if HAS_RUST_BINDINGS:
            self.regex = RegexMatcher()
            if self.regex:
                for pattern in regex_patterns:
                    self.regex.add_pattern(pattern["regex"], pattern["handler"])

                for pattern in self.DEFAULT_REGEX_PATTERNS:
                    self.regex.add_pattern(pattern["regex"], pattern["handler"])

        for pattern in regex_patterns:
            self.PATTERNS.append((re.compile(pattern["regex"]), pattern["handler"]))

        super().__init__(*args, **kwargs)

    def parse_message(self, data: dict) -> dict:
        syslog_message = data["message"]
        host_ip = data["ip"]
        timestamp = data["timestamp"]

        if HAS_RUST_BINDINGS and self.regex:
            try:
                result = self.regex.match_message(syslog_message)
                if result:
                    parse_func, event_data = result
                    parse_method = getattr(self, parse_func)
                    return parse_method(event_data, host_ip, timestamp)
            except Exception as err:
                logger.debug(
                    "Failed to parse using rust binding due to an error", err=str(err)
                )
                pass
        else:
            for compiled_pattern, parse_func in self.PATTERNS:
                has_match = compiled_pattern.search(syslog_message)
                if not has_match:
                    continue

                parse_method = getattr(self, parse_func)
                event_data = has_match.groupdict()
                result = parse_method(event_data, host_ip, timestamp)
                return result

        logger.debug("Could not find a valid regex pattern to parse syslog message")

    def parse_messages_batch(self, messages: list[dict]) -> list[dict]:
        if (
            not HAS_RUST_BINDINGS
            or not self.regex
            or not hasattr(self.regex, "match_messages_batch_native")
        ):
            metrics = []
            for message in messages:
                metric = self.parse_message(message)
                if metric:
                    metrics.append(metric)
            return metrics

        message_texts = []
        host_ips = []
        timestamps = []

        for data in messages:
            message_texts.append(data["message"])
            host_ips.append(data["ip"])
            timestamps.append(data["timestamp"])

        try:
            batch_results = self.regex.match_messages_batch_native(message_texts)

            metrics = []
            for i, result in enumerate(batch_results):
                if result:
                    event_type, capture_data = result
                    event_data = {k: v for k, v in capture_data}
                    parse_method = getattr(self, event_type)
                    metric = parse_method(event_data, host_ips[i], timestamps[i])
                    metrics.append(metric)

            return metrics
        except Exception as err:
            logger.error("Failed to batch parse using rust binding", err=str(err))

            # Fallback
            metrics = []
            for message in messages:
                metric = self.parse_message(message)
                if metric:
                    metrics.append(metric)
            return metrics

    def parse_address_mapping(
        self, data: dict, host_ip: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.ADDRESS_MAPPING
        if not all(key in data for key in ["event", "src_ip", "x_ip"]):
            return

        logger.debug("Parsing Address Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["event"]),
            "vrf_id": int(data.get("vrf_id", 0)),
            "src_ip": data["src_ip"],
            "x_ip": data["x_ip"],
        }
        return metric

    def parse_port_mapping(self, data: dict, host_ip: str, timestamp: datetime) -> dict:
        __event_type__ = NATEventEnum.PORT_MAPPING
        if not all(
            key in data
            for key in ["event", "protocol", "src_ip", "src_port", "x_ip", "x_port"]
        ):
            return

        logger.debug("Parsing Port Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["event"]),
            "vrf_id": int(data.get("vrf_id", 0)),
            "protocol": int(data["protocol"]),
            "src_ip": data["src_ip"],
            "src_port": int(data["src_port"]),
            "x_ip": data["x_ip"],
            "x_port": int(data["x_port"]),
        }
        return metric

    def parse_session_mapping(
        self, data: dict, host_ip: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.SESSION_MAPPING
        if not all(
            key in data
            for key in [
                "event",
                "protocol",
                "src_ip",
                "src_port",
                "x_ip",
                "x_port",
                "dst_ip",
                "dst_port",
            ]
        ):
            return

        logger.debug("Parsing Session Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["event"]),
            "vrf_id": int(data.get("vrf_id", 0)),
            "protocol": int(data["protocol"]),
            "src_ip": data["src_ip"],
            "src_port": data["src_port"],
            "x_ip": data["x_ip"],
            "x_port": int(data["x_port"]),
            "dst_ip": data["dst_ip"],
            "dst_port": int(data["dst_port"]),
        }
        return metric

    def parse_port_block_mapping(
        self, data: dict, host_ip: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.PORT_BLOCK_MAPPING
        if not all(
            key in data for key in ["event", "src_ip", "x_ip", "start_port", "end_port"]
        ):
            return

        logger.debug("Parsing Port Block Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["event"]),
            "vrf_id": int(data.get("vrf_id", 0)),
            "src_ip": data["src_ip"],
            "x_ip": data["x_ip"],
            "start_port": int(data["start_port"]),
            "end_port": int(data["end_port"]),
        }
        return metric

    @abstractmethod
    def event_to_enum(event: str) -> str:
        raise NotImplementedError("event_to_enum not implemented")
