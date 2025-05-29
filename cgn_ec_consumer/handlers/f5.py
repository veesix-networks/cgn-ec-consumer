# Port Mapping Creation: [timestamp] [hostname] NAT-UDP-C: 100.100.100.100:10000 -> 150.150.150.150: 10000
# Session Creation:  Tstamp AX_hostname NAT-TCP-C: fwd_src_ip:fwd_src_port<->fwd_dest_ip:fwd_dest_port, rev_src_ip:rev_src_port<-->rev_dest_ip:rev_dest_port
# Fixed-NAT: FIXED-NAT-PORTS 10.10.10.172->192.168.9.173:3000-4000

# Need to handle ASCII, COmpact and Binary logging formats
import regex as re
from typing import Any
from datetime import datetime
from structlog import get_logger
from cgn_ec_models.enums import NATEventTypeEnum, NATEventEnum, NATProtocolEnum

from cgn_ec_consumer.handlers.generic import GenericSyslogHandler
from cgn_ec_consumer.patterns.f5 import F5_BIGIP_SYSLOG_REGEX_PATTERNS

logger = get_logger("cgn-ec.handlers.f5_bigip")


class F5BIGIPSyslogHandler(GenericSyslogHandler):
    TOPIC = "cgnat.syslog.f5_bigip"
    DEFAULT_REGEX_PATTERNS = F5_BIGIP_SYSLOG_REGEX_PATTERNS

    def parse_session_mapping(
        self, data: tuple[str | Any], host_ip: str, timestamp: datetime
    ) -> dict:
        data["protocol"] = NATProtocolEnum(data["protocol"])
        metric = super().parse_session_mapping(data, host_ip, timestamp)
        return metric

    def event_to_enum(self, event_str: str):
        match event_str:
            case "LSN_ADD":
                event = NATEventTypeEnum.CREATED
            case "LSN_INBOUND_ADD":
                event = NATEventTypeEnum.CREATED
            case "LSN_DELETE":
                event = NATEventTypeEnum.DELETED
            case "LSN_INBOUND_DELETE":
                event = NATEventTypeEnum.DELETED
            case _:
                event = NATEventTypeEnum.CREATED
        return event
