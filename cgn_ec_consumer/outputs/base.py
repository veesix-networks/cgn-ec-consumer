from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cgn_ec_consumer.config import PreProcessorConfig

from structlog import get_logger

from cgn_ec_consumer.preprocessors import preprocessing

logger = get_logger("cgn-ec.outputs")


class BaseOutput(ABC):
    def __init__(self, preprocessors: list["PreProcessorConfig"] = []):
        self.preprocessors = preprocessors

    def _preprocess_metrics(self, metrics: list[dict]) -> list[dict]:
        new_metrics = []
        for preprocessor in self.preprocessors:
            if preprocessor.name not in preprocessing:
                raise NotImplementedError(
                    f"preprocessor '{preprocessor.name}' is not implemented"
                )

            logger.debug(f"({preprocessor.name}) preprocessing starting")
            new_metrics = preprocessing[preprocessor.name](
                metrics if not new_metrics else new_metrics, **preprocessor.arguments
            )
            logger.debug(
                f"({preprocessor.name}) preprocessing finished: {len(new_metrics)}"
            )
        return new_metrics

    @abstractmethod
    def process_metrics(self, metrics: list[dict]):
        raise NotImplementedError(
            "process_metrics needs to be implemented on all Output implementations"
        )
