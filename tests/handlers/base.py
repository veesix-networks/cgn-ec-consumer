import pytest
from abc import ABC, abstractmethod
from cgn_ec_models.enums import NATEventEnum

from cgn_ec_consumer.handlers.generic import BaseSyslogHandler

class BaseSyslogHandlerTest(ABC):
    handler: BaseSyslogHandler

    SESSION_MAPPING_SYSLOG: str = ""
    ADDRESS_MAPPING_SYSLOG: str = ""
    PORT_MAPPING_SYSLOG: str = ""
    PORT_BLOCK_MAPPING_SYSLOG: str = ""

    EXTRA_KVS: dict = {}

    @pytest.fixture
    def generic_syslog_payload(self) -> dict:
        payload = {
            "ip": "192.168.1.100",
            "timestamp": "2025-05-29T12:00:00",
            "message": ""
        }
        payload.update(self.EXTRA_KVS)
        return payload

    @pytest.fixture(autouse=True)
    def setup_handler(self):
        self.handler = self.get_handler()

    @abstractmethod
    def get_handler(self): ...

    @pytest.fixture
    def session_mapping(self, generic_syslog_payload: dict) -> dict:
        generic_syslog_payload["message"] = self.SESSION_MAPPING_SYSLOG
        return generic_syslog_payload

    @pytest.fixture
    def address_mapping(self, generic_syslog_payload: dict) -> dict:
        generic_syslog_payload["message"] = self.ADDRESS_MAPPING_SYSLOG
        return generic_syslog_payload

    @pytest.fixture
    def port_mapping(self, generic_syslog_payload: dict) -> dict:
        generic_syslog_payload["message"] = self.PORT_MAPPING_SYSLOG
        return generic_syslog_payload
    
    @pytest.fixture
    def port_block_mapping(self, generic_syslog_payload: dict) -> dict:
        generic_syslog_payload["message"] = self.PORT_BLOCK_MAPPING_SYSLOG
        return generic_syslog_payload

    def test_session_mapping_parsing(self, session_mapping: str):
        if not self.SESSION_MAPPING_SYSLOG:
            raise AssertionError("Session mapping syslog message not provided for this vendor")
        
        metric = self.handler.parse_message(session_mapping)
        assert metric["type"] == NATEventEnum.SESSION_MAPPING

    def test_address_mapping_parsing(self, address_mapping: str):
        if not self.ADDRESS_MAPPING_SYSLOG:
            raise AssertionError("Address mapping syslog message not provided for this vendor")
        
        metric = self.handler.parse_message(address_mapping)
        assert metric["type"] == NATEventEnum.ADDRESS_MAPPING

    def test_port_mapping_parsing(self, port_mapping: str):
        if not self.PORT_MAPPING_SYSLOG:
            raise AssertionError("Port mapping syslog message not provided for this vendor")
        
        metric = self.handler.parse_message(port_mapping)
        assert metric["type"] == NATEventEnum.PORT_MAPPING

    def test_port_block_mapping_parsing(self, port_block_mapping: str):
        if not self.PORT_BLOCK_MAPPING_SYSLOG:
            raise AssertionError("Port block mapping syslog message not provided for this vendor")
        
        metric = self.handler.parse_message(port_block_mapping)
        assert metric["type"] == NATEventEnum.PORT_BLOCK_MAPPING