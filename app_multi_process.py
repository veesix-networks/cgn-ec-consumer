import json
import os
from time import time, sleep
from os import getpid
from confluent_kafka import Consumer, Message
from multiprocessing import Process, Value, Lock
from threading import Thread
from structlog import get_logger
from wsgiref.simple_server import make_server

from prometheus_client import (
    generate_latest,
    Counter,
    Gauge,
    multiprocess,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
)

from cgn_ec_consumer.handlers.generic import BaseHandler
from cgn_ec_consumer.config import settings
from cgn_ec_consumer.logger import setup_logging

logger = get_logger()

# Enable multiprocess mode for Prometheus
os.environ["PROMETHEUS_MULTIPROC_DIR"] = "/tmp/prometheus_multiproc"
if not os.path.exists("/tmp/prometheus_multiproc"):
    os.makedirs("/tmp/prometheus_multiproc", exist_ok=True)

PROCESSING_TIME = Gauge(
    "cgn_message_processing_seconds",
    "Time spent processing messages",
    ["process_id", "handler_type"],
)

PARSE_FAILURES = Counter(
    "cgn_parse_failures_total",
    "Number of message parse failures",
    ["process_id", "handler_type"],
)

PROCESSED_METRICS = Counter(
    "cgn_process_metrics_total",
    "Number of metrics processed by this process",
    ["process_id", "handler_type"],
)

PROCESS_ERRORS = Counter(
    "cgn_process_errors_total",
    "Number of errors encountered by this process",
    ["process_id", "error_type"],
)

TOTAL_METRICS_PROCESSED = Gauge(
    "cgn_total_metrics_processed",
    "Total number of metrics processed across all processes",
)

METRICS_PER_SECOND = Gauge(
    "cgn_metrics_per_second",
    "Average number of metrics processed per second",
)

ACTIVE_PROCESSES = Gauge(
    "cgn_active_processes",
    "Number of active worker processes",
)


def _process_metrics(
    records: list[Message],
    consumer: Consumer,
    handler: BaseHandler,
    metrics_count: Value,
    metrics_lock: Lock,
):
    process_id = str(getpid())
    handler_type = handler.__class__.__name__

    start_time = time()
    messages = []
    failed_parses = 0

    for msg in records:
        try:
            message = json.loads(msg.value().decode("utf-8"))
            messages.append(message)
        except Exception:
            failed_parses += 1
            continue

    if not messages:
        if failed_parses > 0:
            PARSE_FAILURES.labels(process_id=process_id, handler_type=handler_type).inc(
                failed_parses
            )
        consumer.commit()
        return

    try:
        metrics = handler.parse_messages_batch(messages)
        failed_parses += len(messages) - len(metrics)
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        failed_parses += len(messages)
        metrics = []

    if failed_parses > 0:
        PARSE_FAILURES.labels(process_id=process_id, handler_type=handler_type).inc(
            failed_parses
        )

    handler.process_outputs(metrics)

    metrics_total = len(metrics)
    with metrics_lock:
        metrics_count.value += metrics_total

    PROCESSING_TIME.labels(process_id=process_id, handler_type=handler_type).set(
        time() - start_time
    )

    logger.debug(f"Total metrics processed by process[{getpid()}]: {metrics_total}")
    consumer.commit()


def build_config():
    config = {
        "group.id": settings.KAFKA_GROUP_ID,
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "fetch.max.bytes": 524288000,
        "partition.assignment.strategy": "roundrobin",
    }
    return config


def print_metrics_count(metrics_count: Value):
    prev_count = 0
    prev_time = time()

    while True:
        current_count = metrics_count.value
        current_time = time()

        metrics_diff = current_count - prev_count
        time_diff = current_time - prev_time

        if time_diff > 0:
            avg_metrics_per_second = metrics_diff / time_diff
        else:
            avg_metrics_per_second = 0

        logger.info(
            "Metric statistics",
            total_metrics_processed=current_count,
            avg_metrics_per_last_second=f"{avg_metrics_per_second:.2f}"
            if avg_metrics_per_second
            else 0,
        )

        prev_count = current_count
        prev_time = current_time

        sleep(5)


def worker_process(
    pid: int, handler: BaseHandler, metrics_count: Value, metrics_lock: Lock
):
    """Worker process function that runs a Kafka consumer and processes messages"""
    logger.info(f"Starting worker process {pid}")

    config = build_config()
    consumer = Consumer(config)
    consumer.subscribe([handler.TOPIC])
    process_id = str(pid)
    handler_type = handler.__class__.__name__

    while True:
        try:
            records = consumer.consume(settings.KAFKA_MAX_RECORDS_POLL, timeout=1)
            if not records:
                sleep(0.01)
                continue

            _process_metrics(records, consumer, handler, metrics_count, metrics_lock)

            processed_count = len([r for r in records if r is not None])
            if processed_count > 0:
                PROCESSED_METRICS.labels(
                    process_id=process_id, handler_type=handler_type
                ).inc(processed_count)

        except Exception as err:
            logger.error(f"Error in worker {getpid()}: {err}")
            error_type = type(err).__name__
            PROCESS_ERRORS.labels(process_id=process_id, error_type=error_type).inc()
            consumer.close()
            break

        sleep(0.01)

    consumer.close()


def prometheus_metrics_thread(metrics_count: Value, metrics_lock: Lock):
    prev_count = 0
    prev_time = time()

    while True:
        with metrics_lock:
            current_count = metrics_count.value
        current_time = time()

        metrics_diff = current_count - prev_count
        time_diff = current_time - prev_time

        if time_diff > 0:
            rate = metrics_diff / time_diff
        else:
            rate = 0

        TOTAL_METRICS_PROCESSED.set(current_count)
        METRICS_PER_SECOND.set(rate)

        prev_count = current_count
        prev_time = current_time

        sleep(5)


# Shared counter for metrics across all processes
metrics_count = Value("i", 0)
metrics_lock = Lock()


def prometheus_app(environ, start_response):
    if environ["PATH_INFO"] != "/metrics":
        status = "404 Not Found"
        start_response(status, [("Content-Type", "text/plain")])
        return [b"Not Found"]

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    status = "200 OK"
    response_headers = [
        ("Content-type", CONTENT_TYPE_LATEST),
        ("Content-Length", str(len(data))),
    ]
    start_response(status, response_headers)
    return iter([data])


if __name__ == "__main__":
    setup_logging()

    if not settings.HANDLER:
        exit("A HANDLER must be configured to handle the metrics")

    logger.info(f"Starting Prometheus metrics server on port {settings.METRICS_PORT}")
    httpd = make_server("", settings.METRICS_PORT, prometheus_app)
    Thread(target=httpd.serve_forever, daemon=True).start()

    # Set active processes gauge
    ACTIVE_PROCESSES.set(settings.PROCESSES)

    # Start internal monitoring threads
    logger_t = Thread(target=print_metrics_count, args=(metrics_count,), daemon=True)
    logger_t.start()

    prom_t = Thread(
        target=prometheus_metrics_thread,
        args=(metrics_count, metrics_lock),
        daemon=True,
    )
    prom_t.start()

    handler = settings.HANDLER(outputs=settings.OUTPUTS)
    processes = []
    logger.info(f"Starting {settings.PROCESSES} worker processes")

    for i in range(settings.PROCESSES):
        p = Process(
            target=worker_process,
            args=(i, handler, metrics_count, metrics_lock),
            daemon=True,
        )
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down workers")
        for p in processes:
            p.terminate()
            p.join()
