# Port Mapping Creation: [timestamp] [hostname] NAT-UDP-C: 100.100.100.100:10000 -> 150.150.150.150: 10000
# Session Creation:  Tstamp AX_hostname NAT-TCP-C: fwd_src_ip:fwd_src_port<->fwd_dest_ip:fwd_dest_port, rev_src_ip:rev_src_port<-->rev_dest_ip:rev_dest_port
# Fixed-NAT: FIXED-NAT-PORTS 10.10.10.172->192.168.9.173:3000-4000

# Need to handle ASCII, Compact and Binary logging formats
from typing import Any
from datetime import datetime
from structlog import get_logger
from cgn_ec_models.enums import NATEventTypeEnum, NATEventEnum, NATProtocolEnum

from cgn_ec_consumer.handlers.generic import GenericSyslogHandler
from cgn_ec_consumer.patterns.a10 import A10_VTHUNDER_SYSLOG_REGEX_PATTERNS

logger = get_logger("cgn-ec.handlers.a10_thunder")


class A10ThunderSyslogHandler(GenericSyslogHandler):
    TOPIC = "cgnat.syslog.a10_thunder"
    DEFAULT_REGEX_PATTERNS = A10_VTHUNDER_SYSLOG_REGEX_PATTERNS

    def parse_port_mapping(
        self, data: tuple[str | Any], host_ip: str, timestamp: datetime
    ) -> dict:
        data["protocol"] = NATProtocolEnum.from_string(data["protocol"])
        metric = super().parse_port_mapping(data, host_ip, timestamp)
        return metric

    def parse_session_mapping(
        self, data: tuple[str | Any], host_ip: str, timestamp: datetime
    ) -> dict:
        data["protocol"] = NATProtocolEnum.from_string(data["protocol"])
        metric = super().parse_session_mapping(data, host_ip, timestamp)
        return metric

    def event_to_enum(self, event_str: str):
        match event_str:
            case "C":
                event = NATEventTypeEnum.CREATED
            case "B":
                event = NATEventTypeEnum.CREATED
            case "D":
                event = NATEventTypeEnum.DELETED
            case "U":
                event = NATEventTypeEnum.UPDATED
            case _:
                event = NATEventTypeEnum.CREATED
        return event
