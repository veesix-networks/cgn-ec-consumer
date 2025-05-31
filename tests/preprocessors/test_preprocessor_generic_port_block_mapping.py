import secrets

from cgn_ec_consumer.preprocessors.generic import filter_keys, match_kv, match_kvs, key_exists, exclude_by_kv, exclude_by_kvs, exclude_by_kv_values

def test_preprocessors_generic_port_block_mapping_filter_keys(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)

    preprocessed_metrics = filter_keys(metrics, ["src_ip"])
    for metric in preprocessed_metrics:
        keys = list(metric.keys())
        assert len(keys) == 1
        assert keys[0] == "src_ip"

def test_preprocessors_generic_port_block_mapping_match_kv(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)

    index = secrets.randbelow(len(metrics) - 1) 
    filtered_metric = metrics[index]


    kv_to_filter = secrets.choice(["start_port", "end_port"])
    value_to_match = filtered_metric[kv_to_filter]

    matched = match_kv(metrics, kv_to_filter, value_to_match)
    assert filtered_metric == matched[0]

def test_preprocessors_generic_port_block_mapping_match_kv(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)

    index = secrets.randbelow(len(metrics) - 1) 
    filtered_metric = metrics[index]

    matched = match_kvs(metrics, filtered_metric)
    assert filtered_metric == matched[0]

def test_preprocessors_generic_port_block_mapping_key_exists_none(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)

    matched = key_exists(metrics, "fake_key")
    assert len(matched) == 0

def test_preprocessors_generic_key_exists_none(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)

    matched = key_exists(metrics, "start_port")
    assert len(matched) == 10

def test_preprocessors_generic_port_block_mapping_exclude_by_kv(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)
    metric = secrets.choice(metrics)
    kv_to_filter = secrets.choice(["x_ip", "src_ip", "start_port", "end_port"])

    processed_metrics = exclude_by_kv(metrics, kv_to_filter, metric[kv_to_filter])
    assert len(processed_metrics) == len(metrics) - 1

def test_preprocessors_generic_port_block_mapping_exclude_by_kvs(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)
    metric = secrets.choice(metrics)

    processed_metrics = exclude_by_kvs(metrics, {"src_ip": metric["src_ip"], "x_ip": metric["x_ip"]})
    assert len(processed_metrics) == len(metrics) - 1

def test_preprocessors_generic_port_block_mapping_exclude_by_kv_values(generate_port_block_mapping_metrics: list[dict]):
    metrics = generate_port_block_mapping_metrics(10)
    how_many = secrets.choice(range(1, len(metrics)))
    kv_to_filter = secrets.choice(["x_ip", "src_ip", "start_port", "end_port"])

    values = list({metric[kv_to_filter] for metric in metrics})
    selected = secrets.SystemRandom().sample(values, min(how_many, len(values)))

    processed_metrics = exclude_by_kv_values(metrics, kv_to_filter, selected)
    expected_remaining = len(metrics) - sum(1 for m in metrics if m[kv_to_filter] in selected)
    assert len(processed_metrics) == expected_remaining