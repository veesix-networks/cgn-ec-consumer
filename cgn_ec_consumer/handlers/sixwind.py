# https://doc.6wind.com/turbo-router-3.x/user-guide/cli/ip-networking/cgnat.html#events
# Session Mapping:      Jun 14 12:17:35 dut-vm fp-cgnat[2484]: NEW CONN: fwd proto 6 10.100.0.1:4241 -> 10.200.0.1:33815, back proto 6 10.200.0.1:33815 --> 10.175.0.3:10752
#                       Jun 14 12:19:04 dut-vm fp-cgnat[2484]: DESTROY CONN: fwd proto 6 10.100.0.1:4241 -> 10.200.0.1:33815, back proto 6 10.200.0.1:33915 -> 10.175.0.3:10753
# Port Block Mapping:   Jun 11 08:02:46 vsr fp-cgnat[4269]: CGNAT Log listen on 5001
#                       Jun 11 08:03:09 vsr fp-cgnat[4269]: USER 100.64.0.1 (matching rule 1): NEW BLOCK (pool "mypool", ip public 192.0.2.33, proto 6, port 1 - 512)
#                       Jun 11 08:07:30 vsr fp-cgnat[4269]: USER 100.64.0.1 (matching rule 1): DESTROY BLOCK (pool "mypool", ip public 192.0.2.33, proto 6, port 1 - 512)
from structlog import get_logger
from cgn_ec_consumer.models.enums import NATEventTypeEnum

from cgn_ec_consumer.handlers.generic import BaseSyslogHandler
from cgn_ec_consumer.patterns.sixwind import SIXWIND_SYSLOG_REGEX_PATTERS

logger = get_logger("cgn-ec.handlers.sixwind")


class SixWindSyslogHandler(BaseSyslogHandler):
    TOPIC = "cgnat.syslog.sixwind"
    DEFAULT_REGEX_PATTERNS = SIXWIND_SYSLOG_REGEX_PATTERS

    def event_to_enum(self, event_str: str):
        match event_str:
            case "NEW CONN":
                event = NATEventTypeEnum.CREATED
            case "DESTROY CONN":
                event = NATEventTypeEnum.DELETED
            case _:
                event = NATEventTypeEnum.CREATED
        return event
