# cgn-ec-consumer

CGN Event Collector Consumer Implementation

## Overview

This project consumes syslog messages from NAT/CGN devices via Kafka, processes them using device-specific handlers, and outputs the processed data to various destinations like TimescaleDB or HTTP endpoints.

## Configuration

The application can be configured using either YAML or JSON files. To use file-based configuration, set the `CONFIG_FILE` environment variable to the path of your config file. The file type is automatically detected based on the file extension (`.yaml`, `.yml`, or `.json`).

Example:
```bash
CONFIG_FILE=/path/to/config.yaml python app_single_process.py
# or
CONFIG_FILE=/path/to/config.json python app_single_process.py
```

### Configuration File Format

#### YAML Example

```yaml
# CGN EC Consumer Configuration
kafka_bootstrap_servers: "localhost:9094"
kafka_group_id: "syslog-consumers"
kafka_max_records_poll: 500
batch_size: 30000

# Handler Configuration
handler:
  type: "cgn_ec_consumer.handlers.nfware.NFWareSyslogHandler"
  options: {}  # Additional parameters if needed

# Outputs Configuration
outputs:
  - type: "cgn_ec_consumer.outputs.timescaledb.TimeScaleDBOutput"
    options:
      address: "tsdb"
      port: 5432
      username: "cgnat"
      password: "password123"
      database: "cgnat"
      batch_size: 30000
```

#### JSON Example

```json
{
  "kafka_bootstrap_servers": "localhost:9094",
  "kafka_group_id": "syslog-consumers",
  "kafka_max_records_poll": 500,
  "batch_size": 30000,
  
  "handler": {
    "type": "cgn_ec_consumer.handlers.nfware.NFWareSyslogHandler",
    "options": {}
  },
  
  "outputs": [
    {
      "type": "cgn_ec_consumer.outputs.timescaledb.TimeScaleDBOutput",
      "options": {
        "address": "tsdb",
        "port": 5432,
        "username": "cgnat",
        "password": "password123",
        "database": "cgnat",
        "batch_size": 30000
      }
    }
  ]
}
```

### Available Handlers

- `cgn_ec_consumer.handlers.nfware.NFWareSyslogHandler` - NFWare NAT/CGN
- `cgn_ec_consumer.handlers.a10.A10ThunderSyslogHandler` - A10 Thunder
- `cgn_ec_consumer.handlers.sixwind.SixWindSyslogHandler` - SixWind
- `cgn_ec_consumer.handlers.f5.F5BIGIPSyslogHandler` - F5 BIG-IP
- `cgn_ec_consumer.handlers.juniper.JuniperJUNOSSyslogHandler` - Juniper JUNOS

### Available Outputs

- `cgn_ec_consumer.outputs.timescaledb.TimeScaleDBOutput` - TimescaleDB output
- `cgn_ec_consumer.outputs.http.HTTPOutput` - HTTP output
- `cgn_ec_consumer.outputs.influx.InfluxV1Output` - InfluxDB output (if enabled)

## Environment Variables

If you're not using file-based configuration, the application can also be configured with environment variables:

- `KAFKA_BOOTSTRAP_SERVERS` - Kafka bootstrap servers (default: "localhost:9094")
- `KAFKA_GROUP_ID` - Kafka consumer group ID (default: "syslog-consumers")
- `KAFKA_MAX_RECORDS_POLL` - Maximum number of records to poll (default: 500)
- `BATCH_SIZE` - Batch size for database operations (default: 30000)
- `CONFIG_FILE` - Path to configuration file (optional, file type is auto-detected from extension)

## Development

### Installing Dependencies

```bash
poetry install
```

### Running the Application

```bash
poetry run python app_single_process.py
```

Or with configuration file:

```bash
CONFIG_FILE=config.yaml poetry run python app_single_process.py
```