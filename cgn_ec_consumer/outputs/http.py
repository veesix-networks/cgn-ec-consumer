from requests import Session
from structlog import get_logger

from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.outputs.http")


class HTTPOutput(BaseOutput):
    def __init__(self, url: str, headers: dict = {}, timeout: int = 5):
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self._session = Session()

        if self.headers:
            self._session.headers.update(self.headers)

    def process_metrics(self, data: dict):
        logger.debug("Processing event data")
        with self._session as session:
            session.post(self.url, json=data, timeout=self.timeout)
