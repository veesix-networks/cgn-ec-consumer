from abc import ABC, abstractmethod
from structlog import get_logger

from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.handlers.generic")


class BaseHandler(ABC):
    TOPIC = None

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
    PATTERNS = []

    def parse_message(self, data: dict) -> dict:
        syslog_message = data["message"]
        host_ip = data["ip"]
        timestamp = data["timestamp"]

        for compiled_pattern, parse_func in self.PATTERNS:
            has_match = compiled_pattern.search(syslog_message)
            if not has_match:
                continue

            parse_method = getattr(self, parse_func)
            event_data = has_match.groups()

            result = parse_method(event_data, host_ip, timestamp)
            return result

        logger.debug("Could not find a valid regex pattern to parse syslog message")
