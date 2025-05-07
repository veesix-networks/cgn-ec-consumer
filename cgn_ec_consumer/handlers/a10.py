# Port Mapping Creation: [timestamp] [hostname] NAT-UDP-C: 100.100.100.100:10000 -> 150.150.150.150: 10000
# Session Creation:  Tstamp AX_hostname NAT-TCP-C: fwd_src_ip:fwd_src_port<->fwd_dest_ip:fwd_dest_port, rev_src_ip:rev_src_port<-->rev_dest_ip:rev_dest_port
# Fixed-NAT: FIXED-NAT-PORTS 10.10.10.172->192.168.9.173:3000-4000

# CEF Formats:
# cgn0.thn2/cgn-demo CEF:0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.161.0 spt=48856 sourceTranslatedAddress=99.99.99.13 sourceTranslatedPort=48856 dst=8.8.8.8 dpt=0
# cgn0.thn2/cgn-demo CEF:0|A10|CFW|6.0.0-P1|CGN 101|Nat Port Freed|5|proto=ICMP src=100.65.150.5 spt=37892 sourceTranslatedAddress=99.99.99.8 sourceTranslatedPort=37892
# cgn0.thn2/cgn-demo CEF:0|A10|CFW|6.0.0-P1|CGN 106|Nat Port Batch Pool Allocated|5|proto=UDP src=100.65.140.73 sourceTranslatedAddress=99.99.99.12 sourceTranslatedPort=22016 cn3=22271 cn3Label=Last Nat Port
# cgn0.thn2/cgn-demo CEF:0|A10|CFW|6.0.0-P1|CGN 107|Nat Port Batch Pool Freed|5|proto=UDP src=100.65.140.73 sourceTranslatedAddress=99.99.99.12 sourceTranslatedPort=22016 cn3=22271 cn3Label=Last Nat Port

# Need to handle ASCII, COmpact and Binary logging formats
import regex as re
from typing import Any
from datetime import datetime
from structlog import get_logger
from cgn_ec_models.enums import NATEventTypeEnum, NATEventEnum, NATProtocolEnum

from cgn_ec_consumer.handlers.generic import GenericSyslogHandler

import pycef

logger = get_logger("cgn-ec.handlers.a10_thunder")


class A10ThunderSyslogHandler(GenericSyslogHandler):
    TOPIC = "cgnat.syslog.a10_thunder"

    REGEX_PORT_MAPPING = r"NAT-(\w+)-(\w+): (\d+.\d+.\d+.\d+):(\d+)<-->(\d+.\d+.\d+.\d+):(\d+) to (\d+.\d+.\d+.\d+):(\d+)$"
    REGEX_SESSION_MAPPING = r"NAT-(\w+)-(\w+): (\d+.\d+.\d+.\d+):(\d+)<->(\d+.\d+.\d+.\d+):(\d+),(\d+.\d+.\d+.\d+):(\d+)<-->(\d+.\d+.\d+.\d+):(\d+)$"
    REGEX_PARSE_CEF = r"^((CEF:)?0|A10|CFW|.*)$"

    PATTERNS = [
        (re.compile(REGEX_SESSION_MAPPING), "parse_session_mapping"),
        (re.compile(REGEX_PORT_MAPPING), "parse_port_mapping"),
        (re.compile(REGEX_PARSE_CEF), "parse_cef_message"),
    ]

    def parse_message(self, data: dict) -> dict:
        syslog_message = data["message"]
        host_ip = data["ip"]
        host_name = data["host"]
        timestamp = data["timestamp"]

        for compiled_pattern, parse_func in self.PATTERNS:
            has_match = compiled_pattern.search(syslog_message)
            if not has_match:
                continue

            parse_method = getattr(self, parse_func)
            event_data = has_match.groups()

            result = parse_method(event_data, host_ip, host_name, timestamp)
            return result

        logger.debug(f"Could not find a valid regex pattern to parse syslog message: {data}")

    def parse_cef_message(
        self, data: tuple[str | Any], host_ip: str, host_name: str, timestamp: datetime
    ) -> dict:
        cef = pycef.parse(f"CEF:{data[0]}")

        vrf_name = host_name.split("/", 1)[1] or ""

        __event_type__, __event__ = self._cef_event_map(cef['DeviceEventClassID'])

        metric = None
        if __event_type__ == NATEventEnum.PORT_MAPPING:
            metric = {
                "type": __event_type__,
                "timestamp": timestamp,
                "host": host_ip,
                "event": __event__,
                "vrf_id": 0,
                "vrf_name": vrf_name,
                "protocol":  NATProtocolEnum.from_string(cef["proto"]),
                "src_ip": cef["src"],
                "src_port": cef["spt"],
                "x_ip": cef["sourceTranslatedAddress"],
                "x_port": int(cef["sourceTranslatedPort"]),
            }
        elif __event_type__ == NATEventEnum.PORT_BLOCK_MAPPING:
            metric = {
                "type": __event_type__,
                "timestamp": timestamp,
                "host": host_ip,
                "event": __event__,
                "vrf_id": 0,
                "vrf_name": vrf_name,
                "protocol":  NATProtocolEnum.from_string(cef["proto"]),
                "src_ip": cef["src"],
                "x_ip": cef["sourceTranslatedAddress"],
                "start_port": int(cef["sourceTranslatedPort"]),
                "end_port": int(cef["Last Nat Port"]),
            }

        if metric is not None:
            return metric

    def _cef_event_map(
            self, tag: str
    ) -> list:
        match tag:
            case "CGN 100":
                __event_type__ = NATEventEnum.PORT_MAPPING
                __event__ = NATEventTypeEnum.CREATED
            case "CGN 101":
                __event_type__ = NATEventEnum.PORT_MAPPING
                __event__ = NATEventTypeEnum.DELETED
            case "CGN 106":
                __event_type__ = NATEventEnum.PORT_BLOCK_MAPPING
                __event__ = NATEventTypeEnum.CREATED
            case "CGN 107":
                __event_type__ = NATEventEnum.PORT_BLOCK_MAPPING
                __event__ = NATEventTypeEnum.DELETED
            case _:
                __event_type__ = None
                __event__ = None

        return [__event_type__, __event__]

    def parse_port_mapping(
        self, data: tuple[str | Any], host_ip: str, host_name: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.PORT_MAPPING
        if len(data) != 8:
            return

        logger.debug("Parsing Port Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data[1]),
            "vrf_id": 0,
            "protocol": NATProtocolEnum.from_string(data[0]),
            "src_ip": data[2],
            "src_port": int(data[3]),
            "x_ip": data[4],
            "x_port": int(data[5]),
        }
        return metric

    def parse_session_mapping(
        self, data: tuple[str | Any], host_ip: str, host_name: str, timestamp: datetime
    ) -> dict:
        __event_type__ = NATEventEnum.SESSION_MAPPING
        if len(data) != 10:
            return

        logger.debug("Parsing Session Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data[1]),
            "vrf_id": 0,
            "protocol": NATProtocolEnum.from_string(data[0]),
            "src_ip": data[2],
            "src_port": data[3],
            "x_ip": data[6],
            "x_port": int(data[7]),
            "dst_ip": data[4],
            "dst_port": int(data[5]),
        }
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
