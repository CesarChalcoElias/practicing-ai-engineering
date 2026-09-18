from abc import ABC, abstractmethod

from app.models.llm import ApplicationRequest, ApplicationResult


class BaseAdapter(ABC):
    @abstractmethod
    def send(self, request: ApplicationRequest) -> ApplicationResult: ...
