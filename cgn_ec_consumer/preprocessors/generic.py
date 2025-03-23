from structlog import get_logger

logger = get_logger("cgn-ec.preprocessors")


def filter_keys(metrics: list[dict], keys: list[str]) -> list[dict]:
    return [{k: metric[k] for k in keys if k in metric} for metric in metrics]


def match_kv(metrics: list[dict], key: str, value: str) -> list[dict]:
    return [metric for metric in metrics if metric.get(key) == value]


def match_kvs(metrics: list[dict], kvs: dict) -> list[dict]:
    matched_metrics = []
    for metric in metrics:
        if all(metric.get(k) == v for k, v in kvs.items()):
            matched_metrics.append(metric)
    return matched_metrics


def key_exists(metrics: list[dict], key: str, ignore_none: bool = True) -> list[dict]:
    if ignore_none:
        return [
            metric for metric in metrics if key in metric and metric[key] is not None
        ]
    else:
        return [metric for metric in metrics if key in metric]
