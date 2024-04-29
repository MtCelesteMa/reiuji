"""Base classes for representing calculations in Reiuji."""

from . import multi_sequence
from . import models

from ortools.sat.python import cp_model


class Calculation:
    def __call__(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> float:
        """Calculate and return a float value based on the given sequence.

        Args:
            seq (multi_sequence.MultiSequence[models.MultiblockComponent]): The input sequence.

        Returns:
            float: The calculated value.
        """
        raise NotImplementedError
    
    def to_model(
                self,
                model: cp_model.CpModel,
                seq: multi_sequence.MultiSequence[cp_model.IntVar],
                components: list[models.MultiblockComponent]
    ) -> cp_model.IntVar:
        """Applies the calculation to the given CP model.

        Args:
            model (cp_model.CpModel): The CP model to apply the calculation to.
            seq (multi_sequence.MultiSequence[cp_model.IntVar]): The input sequence
            components (list[models.MultiblockComponent]): The list of multiblock components.

        Returns:
            cp_model.IntVar: The resulting CP variable representing the result of the calculation.
        """
        raise NotImplementedError


class SequenceCalculation:
    def __call__(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> list[float]:
        """Calculate and return a float value based on the given sequence.

        Args:
            seq (multi_sequence.MultiSequence[models.MultiblockComponent]): The input sequence.

        Returns:
            list[float]: The calculated value.
        """
        raise NotImplementedError
    
    def to_model(
                self,
                model: cp_model.CpModel,
                seq: multi_sequence.MultiSequence[cp_model.IntVar],
                components: list[models.MultiblockComponent]
    ) -> list[cp_model.IntVar]:
        """Applies the calculation to the given CP model.

        Args:
            model (cp_model.CpModel): The CP model to apply the calculation to.
            seq (multi_sequence.MultiSequence[cp_model.IntVar]): The input sequence
            components (list[models.MultiblockComponent]): The list of multiblock components.

        Returns:
            list[cp_model.IntVar]: A list of CP variables representing the result of the calculation.
        """
        raise NotImplementedError
