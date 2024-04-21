"""Calculations for designing multiblocks."""

from . import multi_sequence
from . import models

from ortools.sat.python import cp_model


class Calculation:
    def __call__(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> float:
        """Calculate and return a float value based on the given sequence.

        Args:
            seq (multi_sequence.MultiSequence[models.MultiblockComponent]): The sequence to perform calculations on.

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
        """Converts the result of the calculation to an IntVar in the given model.

        Args:
            model (cp_model.CpModel): The model to which the calculation will be added.
            seq (multi_sequence.MultiSequence[cp_model.IntVar]): The sequence to which the calculation will be applied.
            components (list[models.MultiblockComponent]): The list of multiblock components.

        Returns:
            cp_model.IntVar: The IntVar representing the result calculation.
        """
        raise NotImplementedError
