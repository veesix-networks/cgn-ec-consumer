from cgn_ec_consumer.handlers import NFWareSyslogHandler

from tests.handlers.base import BaseSyslogHandlerTest

class TestHandlersSyslogNFWare(BaseSyslogHandlerTest):
    handler: NFWareSyslogHandler
    
    SESSION_MAPPING_SYSLOG = "A VRF 0 6 INT 10.0.0.1:57938 EXT 100.64.0.1:28475 DST 185.165.123.206:443 DIR OUT"
    ADDRESS_MAPPING_SYSLOG = "A VRF 0 INT 10.0.0.1 EXT 100.64.0.1"
    PORT_MAPPING_SYSLOG = "A VRF 0 6 INT 10.0.0.1:57938 EXT 100.64.0.1:28475"
    PORT_BLOCK_MAPPING_SYSLOG = "A VRF 0 INT 10.0.0.1 EXT 100.64.0.1:1024-1535"

    def get_handler(self) -> NFWareSyslogHandler:
        return NFWareSyslogHandler()
