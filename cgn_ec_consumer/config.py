import os
import yaml
import json
import importlib
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from cgn_ec_consumer.handlers.generic import GenericSyslogHandler
from cgn_ec_consumer.outputs.base import BaseOutput


class HandlerConfig(BaseModel):
    type: str
    options: Dict[str, Any] = {}


class OutputConfig(BaseModel):
    type: str
    options: Dict[str, Any] = {}


class ConfigModel(BaseModel):
    kafka_bootstrap_servers: str = "localhost:9094"
    kafka_group_id: str = "syslog-consumers"
    kafka_max_records_poll: int = 500
    batch_size: int = 30000
    handler: HandlerConfig
    outputs: list[OutputConfig]


class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9094"
    KAFKA_GROUP_ID: str = "syslog-consumers"
    KAFKA_MAX_RECORDS_POLL: int = 500

    CONFIG_FILE: Optional[str] = "config.yaml"
    BATCH_SIZE: int = 30000

    # Default configuration that will be overridden by file if provided
    HANDLER: GenericSyslogHandler | None = None
    OUTPUTS: list[BaseOutput] = []

    def load_handler(self, handler_config: HandlerConfig) -> Type[GenericSyslogHandler]:
        """Load handler class from configuration."""
        try:
            module_path, class_name = handler_config.type.rsplit(".", 1)
            module = importlib.import_module(module_path)
            handler_class = getattr(module, class_name)

            # Validate that it's a subclass of GenericSyslogHandler
            if not issubclass(handler_class, GenericSyslogHandler):
                raise ValueError(
                    f"Handler {handler_config.type} is not a subclass of GenericSyslogHandler"
                )

            return handler_class
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Failed to load handler {handler_config.type}: {str(e)}")

    def load_output(self, output_config: OutputConfig) -> BaseOutput:
        """Load and instantiate output from configuration."""
        try:
            module_path, class_name = output_config.type.rsplit(".", 1)
            module = importlib.import_module(module_path)
            output_class = getattr(module, class_name)

            # Validate that it's a subclass of BaseOutput
            if not issubclass(output_class, BaseOutput):
                raise ValueError(
                    f"Output {output_config.type} is not a subclass of BaseOutput"
                )

            # Instantiate the output with options from config
            return output_class(**output_config.options)
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Failed to load output {output_config.type}: {str(e)}")

    def load_config_from_file(self):
        """Load configuration from YAML or JSON file based on file extension."""
        if not self.CONFIG_FILE or not os.path.exists(self.CONFIG_FILE):
            return

        try:
            # Auto-detect file type based on extension
            file_ext = os.path.splitext(self.CONFIG_FILE)[1].lower()

            with open(self.CONFIG_FILE, "r") as f:
                if file_ext in [".yaml", ".yml"]:
                    config_data = yaml.safe_load(f)
                elif file_ext == ".json":
                    config_data = json.load(f)
                else:
                    raise ValueError(
                        f"Unsupported config file extension: {file_ext}. Use .yaml, .yml, or .json"
                    )

                # Parse with pydantic model to validate
                config = ConfigModel(**config_data)

                # Update settings from file
                self.KAFKA_BOOTSTRAP_SERVERS = config.kafka_bootstrap_servers
                self.KAFKA_GROUP_ID = config.kafka_group_id
                self.KAFKA_MAX_RECORDS_POLL = config.kafka_max_records_poll
                self.BATCH_SIZE = config.batch_size

                # Load handler
                self.HANDLER = self.load_handler(config.handler)

                # Load outputs
                self.OUTPUTS = [
                    self.load_output(output_config) for output_config in config.outputs
                ]
        except Exception as e:
            raise ValueError(
                f"Error loading configuration from {self.CONFIG_FILE}: {str(e)}"
            )


# Initialize settings
settings = Settings()

# Load config from file if specified
if settings.CONFIG_FILE:
    settings.load_config_from_file()
