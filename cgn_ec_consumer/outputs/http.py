from requests import Session
from structlog import get_logger

from cgn_ec_consumer.outputs.base import BaseOutput

logger = get_logger("cgn-ec.outputs.http")


class HTTPWebhookOutput(BaseOutput):
    def __init__(
        self,
        url: str,
        headers: dict = {},
        timeout: int = 5,
        preprocessors: list[str] = [],
    ):
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.preprocessors = preprocessors
        self._session = Session()

        if self.headers:
            self._session.headers.update(self.headers)

    def process_metrics(self, metrics: dict):
        logger.debug("Processing event data")

        try:
            with self._session as session:
                session.post(self.url, json=metrics, timeout=self.timeout)
        except Exception as err:
            logger.warning("Unable to process metrics", exception=str(err))
