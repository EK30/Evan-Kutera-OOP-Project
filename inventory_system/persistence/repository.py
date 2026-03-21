from abc import ABC, abstractmethod

class Repository(ABC):
    """
    Abstract base class for all repository implementations.
    """

    @abstractmethod
    def insert(self, item):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_name(self, name: str):
        pass

    @abstractmethod
    def update(self, item):
        pass

    @abstractmethod
    def delete(self, name: str):
        pass