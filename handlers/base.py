from abc import ABC, abstractmethod


class BaseHandler(ABC):
    """Base class for all handlers.

    This class defines the interface for all handlers. It is an abstract base class that requires
    subclasses to implement the `handle` method.
    """

    @abstractmethod
    def handle(self, *args):
        pass
