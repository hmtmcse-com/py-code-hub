from abc import ABC, abstractmethod


class BaseABC(ABC):

    @abstractmethod
    def implement_it(self, name: str, age: int, **kwargs): ...

    @abstractmethod
    def unlimited(self, **kwargs): ...
