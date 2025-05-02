import os
from pathlib import Path

import pytest
from pytest import FixtureRequest
from tests import generate_test_data as randomize_data

from cgn_ec_consumer.config import Settings

from cgn_ec_consumer.handlers.generic import GenericSyslogHandler, GenericNetFlowV9Handler, GenericRADIUSAccountingHandler

@pytest.fixture(scope="module")
def syslog_settings(request: FixtureRequest):
    """Load Settings config and inject a different handler per test run."""
    handler: GenericSyslogHandler = request.param

    settings = Settings(
        HANDLER=handler(),
    )
    return settings

@pytest.fixture(scope="module")
def dynamic_syslog_handler(request: FixtureRequest):
    """Load Settings config and inject a different handler per test run."""
    config_file = Path("tests/config.test.yaml")
    assert config_file.is_file()

    settings = Settings(CONFIG_FILE=str(config_file.resolve()))
    settings.load_config_from_file()

    settings.HANDLER = request.param
    return settings.HANDLER

@pytest.fixture(scope="module")
def yaml_config(request: FixtureRequest):
    config_file = Path("tests/config.test.yaml")
    assert config_file.is_file()

    from cgn_ec_consumer.config import Settings

    settings = Settings(CONFIG_FILE=str(config_file.resolve()))
    settings.load_config_from_file()
    return settings

@pytest.fixture(scope="module")
def json_config(request: FixtureRequest):
    config_file = Path("tests/config.test.json")
    assert config_file.is_file()

    os.environ.setdefault("CONFIG_FILE", str(config_file.resolve()))

    from cgn_ec_consumer.config import Settings

    settings = Settings(CONFIG_FILE=str(config_file.resolve()))
    settings.load_config_from_file()
    return settings

@pytest.fixture(scope="module")
def generate_session_mapping_metrics():
    def _generate(n=1):
        metrics = []
        for _ in range(n):
            metric = {
                "type": "session-mapping",
                "timestamp": randomize_data.random_timestamp_past_month(),
                "host": randomize_data.random_x_ip(),
                "event": randomize_data.random_session_event_type(),
                "vrf_id": 0,
                "protocol": randomize_data.random_protocol(),
                "src_ip": randomize_data.random_src_ip(),
                "src_port": randomize_data.random_src_port(),
                "x_ip": randomize_data.random_x_ip(),
                "x_port": randomize_data.random_src_port(),
                "dst_ip": randomize_data.random_dst_ip(),
                "dst_port": randomize_data.random_dst_port(),
            }
            metrics.append(metric)

        if n == 1:
            return metrics[0]
        return metrics

    return _generate

@pytest.fixture(scope="module")
def generate_address_mapping_metrics():
    def _generate(n=1):
        metrics = []
        for _ in range(n):
            metric = {
                "type": "address-mapping",
                "timestamp": randomize_data.random_timestamp_past_month(),
                "host": randomize_data.random_x_ip(),
                "event": randomize_data.random_session_event_type(),
                "vrf_id": 0,
                "src_ip": randomize_data.random_src_ip(),
                "x_ip": randomize_data.random_x_ip(),
            }
            metrics.append(metric)

        if n == 1:
            return metrics[0]
        return metrics

    return _generate

@pytest.fixture(scope="module")
def generate_port_mapping_metrics():
    def _generate(n=1):
        metrics = []
        for _ in range(n):
            metric = {
                "type": "port-mapping",
                "timestamp": randomize_data.random_timestamp_past_month(),
                "host": randomize_data.random_x_ip(),
                "event": randomize_data.random_session_event_type(),
                "vrf_id": 0,
                "protocol": randomize_data.random_protocol(),
                "src_ip": randomize_data.random_src_ip(),
                "src_port": randomize_data.random_src_port(),
                "x_ip": randomize_data.random_x_ip(),
                "x_port": randomize_data.random_src_port(),
            }
            metrics.append(metric)

        if n == 1:
            return metrics[0]
        return metrics

    return _generate

@pytest.fixture(scope="module")
def generate_port_block_mapping_metrics():
    def _generate(n=1):
        metrics = []
        for _ in range(n):
            metric = {
                "type": "port-mapping",
                "timestamp": randomize_data.random_timestamp_past_month(),
                "host": randomize_data.random_x_ip(),
                "event": randomize_data.random_session_event_type(),
                "vrf_id": 0,
                "protocol": randomize_data.random_protocol(),
                "src_ip": randomize_data.random_src_ip(),
                "x_ip": randomize_data.random_x_ip(),
                "start_port": randomize_data.random_src_port(),
                "end_port": randomize_data.random_src_port(),
            }
            metrics.append(metric)

        if n == 1:
            return metrics[0]
        return metrics

    return _generate