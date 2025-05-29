import pytest

from cgn_ec_consumer.handlers import F5BIGIPSyslogHandler

from tests.handlers.base import BaseSyslogHandlerTest

class TestHandlersSyslogF5BIGIP(BaseSyslogHandlerTest):
    handler: F5BIGIPSyslogHandler
    
    def get_handler(self) -> F5BIGIPSyslogHandler:
        return F5BIGIPSyslogHandler()
    
    @pytest.mark.skip(reason="Session mapping not supported for this vendor")
    def test_session_mapping_parsing(self): ...

    @pytest.mark.skip(reason="Address mapping not supported for this vendor")
    def test_address_mapping_parsing(self): ...

    @pytest.mark.skip(reason="Port mapping not supported for this vendor")
    def test_port_mapping_parsing(self): ...

    @pytest.mark.skip(reason="Port block mapping not supported for this vendor")
    def test_port_block_mapping_parsing(self): ...