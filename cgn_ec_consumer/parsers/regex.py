from structlog import get_logger

from cgn_ec_consumer.parsers.base import BaseParser


logger = get_logger("cgn-ec.parsers.regex")


class RegexParser(BaseParser):
    def parse_event(self, event: str):
        return super().parse_event()
