# https://www.microfocus.com/documentation/arcsight/arcsight-smartconnectors-8.4/pdfdoc/cef-implementation-standard/cef-implementation-standard.pdf
import regex as re
from dataclasses import dataclass
from structlog import get_logger

from cgn_ec_consumer.parsers.base import BaseParser

logger = get_logger("cgn-ec.parsers.cef")


@dataclass
class CEFEvent:
    version: int
    vendor: str
    product: str
    device_version: str
    event_class: str
    name: str
    severity: str
    extension: dict[str, str]


class CEFParser(BaseParser):
    """Common Event Format.

    Mandatory headers but extension are interesting k,v pairs we can parse.
    """

    def parse_event(self, event: str) -> CEFEvent:
        headers = event.split("|", 7)
        if len(headers) != 8:
            return

        (
            version,
            vendor,
            product,
            device_version,
            event_class,
            name,
            severity,
            extensions,
        ) = headers

        kvs = self._split_kvs(extensions)
        return CEFEvent(
            version=int(version),
            vendor=vendor,
            product=product,
            device_version=device_version,
            event_class=event_class,
            name=name,
            severity=severity,
            extension=kvs,
        )

    def _split_kvs(self, message: str) -> dict:
        fields = {}

        # We need to match the first = to the next or end of string, because values can have spaces
        pattern = re.finditer(r"(\w+)=([^=]+?)(?=\s\w+=|$)", message)

        for match in pattern:
            key, value = match.groups()
            fields[key] = value.strip()

        return fields
