import secrets

from cgn_ec_consumer.preprocessors.generic import filter_keys, match_kv, match_kvs, key_exists

def test_preprocessors_generic_port_mapping_filter_keys(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)

    preprocessed_metrics = filter_keys(metrics, ["src_ip"])
    for metric in preprocessed_metrics:
        keys = list(metric.keys())
        assert len(keys) == 1
        assert keys[0] == "src_ip"

def test_preprocessors_generic_port_mapping_match_kv(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)

    index = secrets.randbelow(len(metrics) - 1) 
    filtered_metric = metrics[index]


    kv_to_filter = secrets.choice(["src_port", "dst_port", "x_port"])
    value_to_match = filtered_metric[kv_to_filter]

    matched = match_kv(metrics, kv_to_filter, value_to_match)
    assert filtered_metric == matched[0]

def test_preprocessors_generic_port_mapping_match_kv(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)

    index = secrets.randbelow(len(metrics) - 1) 
    filtered_metric = metrics[index]

    matched = match_kvs(metrics, filtered_metric)
    assert filtered_metric == matched[0]

def test_preprocessors_generic_port_mapping_key_exists_none(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)

    matched = key_exists(metrics, "fake_key")
    assert len(matched) == 0

def test_preprocessors_generic_key_exists_none(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)

    matched = key_exists(metrics, "x_port")
    assert len(matched) == 10