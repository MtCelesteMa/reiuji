"""Core multiblock classes."""

from abc import ABC, abstractmethod

from .. import utils
from . import models


class BaseMultiblock(ABC):
    @abstractmethod
    def to_blocks(self) -> utils.multi_sequence.MultiSequence[models.MCBlock]: ...

    @abstractmethod
    def print(self) -> None: ...
