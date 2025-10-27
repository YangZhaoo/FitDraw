from abc import ABC, abstractmethod
from typing import List

from .protocol import Record


class Parser(ABC):

    def __init__(self, file: str):
        self._file = file

    @abstractmethod
    def parser(self) -> List[Record]:
        pass
