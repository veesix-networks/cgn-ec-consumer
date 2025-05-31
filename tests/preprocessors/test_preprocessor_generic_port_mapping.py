import secrets

from cgn_ec_consumer.preprocessors.generic import filter_keys, match_kv, match_kvs, key_exists, exclude_by_kv, exclude_by_kvs, exclude_by_kv_values

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


    kv_to_filter = secrets.choice(["src_port", "src_ip", "x_port", "x_ip"])
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

def test_preprocessors_generic_port_mapping_exclude_by_kv(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)
    metric = secrets.choice(metrics)
    kv_to_filter = secrets.choice(["src_port", "src_ip", "x_port", "x_ip"])
    processed = exclude_by_kv(metrics, kv_to_filter, metric[kv_to_filter])
    assert len(processed) == len(metrics) - 1

def test_preprocessors_generic_port_mapping_exclude_by_kvs(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)
    metric = secrets.choice(metrics)
    processed = exclude_by_kvs(metrics, {
        "src_port": metric["src_port"],
        "x_port": metric["x_port"]
    })
    assert len(processed) == len(metrics) - 1

def test_preprocessors_generic_port_mapping_exclude_by_kv_values(generate_port_mapping_metrics: list[dict]):
    metrics = generate_port_mapping_metrics(10)
    kv_to_filter = secrets.choice(["src_port", "src_ip", "x_port", "x_ip"])
    unique_values = list({m[kv_to_filter] for m in metrics})
    how_many = secrets.choice(range(1, len(unique_values)+1))
    selected_values = secrets.SystemRandom().sample(unique_values, how_many)
    processed = exclude_by_kv_values(metrics, kv_to_filter, selected_values)
    expected_remaining = len(metrics) - sum(1 for m in metrics if m[kv_to_filter] in selected_values)
    assert len(processed) == expected_remaining