import os
from pathlib import Path

import pytest
from pytest import FixtureRequest


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
