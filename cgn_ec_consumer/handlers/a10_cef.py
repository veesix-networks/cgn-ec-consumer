from datetime import datetime
from structlog import get_logger
from cgn_ec_models.enums import NATEventTypeEnum, NATEventEnum, NATProtocolEnum

from cgn_ec_consumer.handlers.generic import GenericSyslogHandler
from cgn_ec_consumer.parsers.cef import CEFParser, CEFEvent

logger = get_logger("cgn-ec.handlers.a10_thunder_cef")


class A10ThunderCEFSyslogHandler(GenericSyslogHandler):
    TOPIC = "cgnat.syslog.a10_thunder_cef"
    PARSER = CEFParser()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = None  # Will fix in another PR when I move rust binding logic under the RegexParser()

    def parse_message(self, data: dict) -> dict:
        syslog_message = data["message"]
        host_ip = data["ip"]
        timestamp = data["timestamp"]
        vrf = data.get("program", "").split("/")[-1]

        event = self.PARSER.parse_event(syslog_message)
        parse_method = None
        match event.name:
            case "Nat Port Allocated":
                parse_method = self.parse_port_mapping
            case "Nat Port Freed":
                parse_method = self.parse_port_mapping
            case "Nat Port Batch Pool Allocated":
                parse_method = self.parse_port_block_mapping
            case "Nat Port Batch Pool Freed":
                parse_method = self.parse_port_block_mapping

            # Need to find other messages for session/address mapping, potential radius attributes they may have carreid into the other OS
            # https://data.nag.wiki/%D0%90%D1%80%D1%85%D0%B8%D0%B2/a10/AX_Admin_Guide_266GR1-2013.05.08.pdf

        result = parse_method(event, host_ip, vrf, timestamp)
        return result

    def parse_address_mapping(
        self, data: CEFEvent, host_ip: str, vrf: str, timestamp: datetime
    ):
        raise NotImplementedError

    def parse_session_mapping(
        self, data: CEFEvent, host_ip: str, vrf: str, timestamp: datetime
    ):
        raise NotImplementedError

    def parse_port_mapping(
        self, data: CEFEvent, host_ip: str, vrf: str, timestamp: datetime
    ):
        __event_type__ = NATEventEnum.PORT_MAPPING
        if not all(
            key in data.extension
            for key in [
                "proto",
                "src",
                "spt",
                "sourceTranslatedAddress",
                "sourceTranslatedPort",
            ]
        ):
            return

        logger.debug("Parsing Port Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data.event_class),
            "vrf_id": vrf,
            "protocol": NATProtocolEnum.from_string(data.extension["proto"]),
            "src_ip": data.extension["src"],
            "src_port": data.extension["spt"],
            "x_ip": data.extension["sourceTranslatedAddress"],
            "x_port": data.extension["sourceTranslatedPort"],
        }
        return metric

    def parse_port_block_mapping(
        self, data: CEFEvent, host_ip: str, vrf: str, timestamp: datetime
    ):
        __event_type__ = NATEventEnum.PORT_BLOCK_MAPPING
        if not all(
            key in data.extension
            for key in [
                "proto",
                "src",
                "sourceTranslatedAddress",
                "sourceTranslatedPort",
                "cn3",
            ]
        ):
            return

        logger.debug("Parsing Port Block Mapping", data=data)
        metric = {
            "type": __event_type__,
            "timestamp": timestamp,
            "host": host_ip,
            "event": self.event_to_enum(data.event_class),
            "vrf_id": vrf,
            "src_ip": data.extension["src"],
            "x_ip": data.extension["sourceTranslatedAddress"],
            "start_port": int(data.extension["sourceTranslatedPort"]),
            "end_port": int(data.extension["cn3"]),
        }
        return metric

    def event_to_enum(self, event_class: str) -> NATEventTypeEnum:
        match event_class:
            case "CGN 100" | "CGN 106":
                return NATEventTypeEnum.CREATED
            case "CGN 101" | "CGN 107":
                return NATEventTypeEnum.DELETED
            case _:
                return NATEventTypeEnum.CREATED
