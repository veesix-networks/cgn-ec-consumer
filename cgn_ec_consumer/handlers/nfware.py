# https://docs.nfware.com/en/6.3/nat/logging.html#message-format
# Address mapping (Static NAT / 1-1 NAT): A VRF 0 INT 10.0.0.1 EXT 100.64.0.1
# Port Mapping: A VRF 0 6 INT 10.0.0.1:57938 EXT 100.64.0.1:28475
# Session: A VRF 0 6 INT 10.0.0.1:57938 EXT 100.64.0.1:28475 DST 185.165.123.206:443 DIR OUT
# Port Blocks: A VRF 0 INT 10.0.0.1 EXT 100.64.0.1:1024-1535
# Typically deterministic CGN should be used with port ranges to avoid large logs

from datetime import datetime
from structlog import get_logger
from cgn_ec_consumer.models.enums import NATEventTypeEnum, NATEventEnum, NATProtocolEnum

from cgn_ec_consumer.handlers.generic import (
    GenericSyslogHandler,
    GenericRADIUSAccountingHandler,
)
from cgn_ec_consumer.patterns.nfware import NFWARE_SYSLOG_REGEX_PATTERNS

logger = get_logger("cgn-ec.handlers.nfware")


class NFWareRADIUSAccountingHandler(GenericRADIUSAccountingHandler):
    TOPIC = "cgnat.accounting.nfware"

    def parse_message(self, message: dict):
        host_ip = message.get("NAS-IP-Address")
        timestamp = message.get("Event-Timestamp")
        if not host_ip or not timestamp:
            return

        result = None
        if message.get("NFWare-vCGNAT-Dest-Addr"):
            result = self._parse_session_mapping(message, host_ip, timestamp)
        elif message.get("NFWare-vCGNAT-NAT-Port"):
            result = self._parse_port_mapping(message, host_ip, timestamp)
        elif message.get("NFWare-vCGNAT-NAT-Port-Start"):
            result = self._parse_port_block_mapping(message, host_ip, timestamp)

        return result

    def _parse_session_mapping(
        self, data: dict, host_ip: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.SESSION_MAPPING

        logger.debug("Parsing Session Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["NFWare-vCGNAT-Action"]),
            "vrf_id": int(data["NFWare-vCGNAT-VRF"]),
            "protocol": NATProtocolEnum.from_string(data["NFWare-vCGNAT-Protocol"]),
            "src_ip": data["NFWare-vCGNAT-Inside-Addr"],
            "src_port": data["NFWare-vCGNAT-Inside-Port"],
            "x_ip": data["NFWare-vCGNAT-NAT-Addr"],
            "x_port": int(data["NFWare-vCGNAT-NAT-Port"]),
            "dst_ip": data["NFWare-vCGNAT-Dest-Addr"],
            "dst_port": int(data["NFWare-vCGNAT-Dest-Port"]),
        }

        return metric

    def _parse_port_mapping(
        self, data: dict, host_ip: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.PORT_MAPPING

        logger.debug("Parsing Port Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["NFWare-vCGNAT-Action"]),
            "vrf_id": int(data["NFWare-vCGNAT-VRF"]),
            "protocol": NATProtocolEnum.from_string(data["NFWare-vCGNAT-Protocol"]),
            "src_ip": data["NFWare-vCGNAT-Inside-Addr"],
            "src_port": data["NFWare-vCGNAT-Inside-Port"],
            "x_ip": data["NFWare-vCGNAT-NAT-Addr"],
            "x_port": int(data["NFWare-vCGNAT-NAT-Port"]),
        }
        return metric

    def _parse_port_block_mapping(
        self, data: dict, host_ip: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.PORT_BLOCK_MAPPING

        logger.debug("Parsing Port Block Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data["NFWare-vCGNAT-Action"]),
            "vrf_id": int(data["NFWare-vCGNAT-VRF"]),
            "src_ip": data["NFWare-vCGNAT-Inside-Addr"],
            "x_ip": data["NFWare-vCGNAT-NAT-Addr"],
            "start_port": int(data["NFWare-vCGNAT-NAT-Port-Start"]),
            "end_port": int(data["NFWare-vCGNAT-NAT-Port-End"]),
        }
        return metric

    def event_to_enum(self, event_str: str):
        created = ("Port-Allocated", "Session-Created", "Port-Block-Allocated")
        deleted = ("Port-Freed", "Session-Deleted", "Port-Block-Freed")

        match event_str:
            case x if x in created:
                event = NATEventTypeEnum.CREATED
            case x if x in deleted:
                event = NATEventTypeEnum.DELETED
            case _:
                event = NATEventTypeEnum.CREATED
        return event


class NFWareSyslogHandler(GenericSyslogHandler):
    TOPIC = "cgnat.syslog.nfware"
    DEFAULT_REGEX_PATTERNS = NFWARE_SYSLOG_REGEX_PATTERNS

    def event_to_enum(self, event_str: str):
        match event_str:
            case "A":
                event = NATEventTypeEnum.CREATED
            case "D":
                event = NATEventTypeEnum.DELETED
            case _:
                event = NATEventTypeEnum.CREATED
        return event
