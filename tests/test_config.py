from cgn_ec_consumer.config import Settings


def test_config_json(yaml_config: Settings):
    assert "config.test.yaml" in yaml_config.CONFIG_FILE

    assert yaml_config.KAFKA_BOOTSTRAP_SERVERS == "localhost:9094"
    assert yaml_config.KAFKA_GROUP_ID == "syslog-consumers"
    assert yaml_config.KAFKA_MAX_RECORDS_POLL
    assert yaml_config.BATCH_SIZE

    assert yaml_config.HANDLER
    assert len(yaml_config.OUTPUTS) == 4


def test_config_yaml(json_config: Settings):
    assert "config.test.json" in json_config.CONFIG_FILE

    assert json_config.KAFKA_BOOTSTRAP_SERVERS == "localhost:9094"
    assert json_config.KAFKA_GROUP_ID == "syslog-consumers"
    assert json_config.KAFKA_MAX_RECORDS_POLL
    assert json_config.BATCH_SIZE

    assert json_config.HANDLER
    assert len(json_config.OUTPUTS) == 4
