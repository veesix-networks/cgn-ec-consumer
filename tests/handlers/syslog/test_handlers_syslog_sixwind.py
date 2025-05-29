import pytest

from cgn_ec_consumer.handlers import SixWindSyslogHandler

from tests.handlers.base import BaseSyslogHandlerTest

class TestHandlersSyslogSixwind(BaseSyslogHandlerTest):
    handler: SixWindSyslogHandler
    
    def get_handler(self) -> SixWindSyslogHandler:
        return SixWindSyslogHandler()
    
    @pytest.mark.skip(reason="Session mapping not supported for this vendor")
    def test_session_mapping_parsing(self): ...

    @pytest.mark.skip(reason="Address mapping not supported for this vendor")
    def test_address_mapping_parsing(self): ...

    @pytest.mark.skip(reason="Port mapping not supported for this vendor")
    def test_port_mapping_parsing(self): ...

    @pytest.mark.skip(reason="Port block mapping not supported for this vendor")
    def test_port_block_mapping_parsing(self): ...