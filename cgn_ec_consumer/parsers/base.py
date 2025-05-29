from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse_event(self, event: str) -> dict: ...
