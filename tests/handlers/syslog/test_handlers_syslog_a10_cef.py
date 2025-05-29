import pytest

from cgn_ec_consumer.handlers import A10ThunderCEFSyslogHandler

from tests.handlers.base import BaseSyslogHandlerTest

class TestHandlersSyslogA10ThunderCEFSyslog(BaseSyslogHandlerTest):
    handler: A10ThunderCEFSyslogHandler
    
    SESSION_MAPPING_SYSLOG = "0|A10|ADC|6.0.7|CGN 102|Nat Session Created|5|proto=UDP src=10.44.55.100 spt=38951 dst=142.250.179.238 dpt=443 sourceTranslatedAddress=99.99.99.13 sourceTranslatedPort=38951 destinationTranslatedAddress=142.250.179.238 destinationTranslatedPort=443"
    PORT_MAPPING_SYSLOG = "0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.161.0 spt=48856 sourceTranslatedAddress=99.99.99.13 sourceTranslatedPort=48856 dst=8.8.8.8 dpt=0"
    PORT_BLOCK_MAPPING_SYSLOG = "0|A10|CFW|6.0.0-P1|CGN 106|Nat Port Batch Pool Allocated|5|proto=UDP src=100.65.140.73 sourceTranslatedAddress=99.99.99.12 sourceTranslatedPort=22016 cn3=22271 cn3Label=Last Nat Port"

    EXTRA_KVS = {"program": "CEF"}

    def get_handler(self) -> A10ThunderCEFSyslogHandler:
        return A10ThunderCEFSyslogHandler()
    
    @pytest.mark.skip(reason="Address mapping not supported")
    def test_address_mapping_parsing(self): ...
