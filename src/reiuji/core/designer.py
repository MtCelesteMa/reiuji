"""Base class for multiblock designers."""

from . import multi_sequence
from . import models


class Designer:
    def design(self, timeout: str | None = None) -> multi_sequence.MultiSequence[models.MultiblockComponent]:
        """Design a multiblock structure.

        Args:
            timeout (str, optional): The timeout for the design process. Defaults to None.

        Returns:
            multi_sequence.MultiSequence[models.MultiblockComponent]: The designed multiblock structure.
        """
        raise NotImplementedError
