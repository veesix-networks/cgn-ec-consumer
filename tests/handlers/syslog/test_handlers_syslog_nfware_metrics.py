import pytest

from tests.data_generators.nfware import generate_syslog_session_mappings, generate_syslog_address_mappings, generate_syslog_port_mappings, generate_syslog_port_block_mappings
from cgn_ec_consumer.config import Settings
from cgn_ec_consumer.handlers import NFWareSyslogHandler
from cgn_ec_models.enums import NATEventEnum

@pytest.mark.parametrize("syslog_settings", [NFWareSyslogHandler], indirect=True)
def test_handlers_syslog_nfware_parse_session_mapping(syslog_settings: Settings):
    handler = syslog_settings.HANDLER
    syslog_messages = generate_syslog_session_mappings(10)

    metrics = []
    for syslog_message in syslog_messages:
        metric = handler.parse_message(syslog_message)
        metrics.append(metric)
        assert metric["type"] == NATEventEnum.SESSION_MAPPING

    assert len(metrics) == 10

@pytest.mark.parametrize("syslog_settings", [NFWareSyslogHandler], indirect=True)
def test_handlers_syslog_nfware_parse_address_mapping(syslog_settings: Settings):
    handler = syslog_settings.HANDLER
    syslog_messages = generate_syslog_address_mappings(10)

    metrics = []
    for syslog_message in syslog_messages:
        metric = handler.parse_message(syslog_message)
        metrics.append(metric)
        assert metric["type"] == NATEventEnum.ADDRESS_MAPPING

    assert len(metrics) == 10

@pytest.mark.parametrize("syslog_settings", [NFWareSyslogHandler], indirect=True)
def test_handlers_syslog_nfware_parse_port_mapping(syslog_settings: Settings):
    handler = syslog_settings.HANDLER
    syslog_messages = generate_syslog_port_mappings(10)

    metrics = []
    for syslog_message in syslog_messages:
        metric = handler.parse_message(syslog_message)
        metrics.append(metric)
        assert metric["type"] == NATEventEnum.PORT_MAPPING

    assert len(metrics) == 10

@pytest.mark.parametrize("syslog_settings", [NFWareSyslogHandler], indirect=True)
def test_handlers_syslog_nfware_parse_port_block_mapping(syslog_settings: Settings):
    handler = syslog_settings.HANDLER
    syslog_messages = generate_syslog_port_block_mappings(10)

    metrics = []
    for syslog_message in syslog_messages:
        metric = handler.parse_message(syslog_message)
        metrics.append(metric)
        assert metric["type"] == NATEventEnum.PORT_BLOCK_MAPPING

    assert len(metrics) == 10