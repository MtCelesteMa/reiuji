"""Base classes for representing calculations in Reiuji."""

from ... import core
from ...components.types import *

from ortools.sat.python import cp_model


class Calculation:
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        """Calculate and return a float value based on the given sequence.

        Args:
            seq (core.multi_sequence.MultiSequence[core.components.Component]): The input sequence.

        Returns:
            float: The calculated value.
        """
        raise NotImplementedError
    
    def to_model(
                self,
                model: cp_model.CpModel,
                seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
                components: list[Component]
    ) -> cp_model.IntVar:
        """Applies the calculation to the given CP model.

        Args:
            model (cp_model.CpModel): The CP model to apply the calculation to.
            seq (core.multi_sequence.MultiSequence[cp_model.IntVar]): The input sequence
            components (list[core.components.Component]): The list of multiblock components.

        Returns:
            cp_model.IntVar: The resulting CP variable representing the result of the calculation.
        """
        raise NotImplementedError


class SequenceCalculation:
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> list[float]:
        """Calculate and return a float value based on the given sequence.

        Args:
            seq (core.multi_sequence.MultiSequence[core.components.Component]): The input sequence.

        Returns:
            list[float]: The calculated value.
        """
        raise NotImplementedError
    
    def to_model(
                self,
                model: cp_model.CpModel,
                seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
                components: list[Component]
    ) -> list[cp_model.IntVar]:
        """Applies the calculation to the given CP model.

        Args:
            model (cp_model.CpModel): The CP model to apply the calculation to.
            seq (core.multi_sequence.MultiSequence[cp_model.IntVar]): The input sequence
            components (list[core.components.Component]): The list of multiblock components.

        Returns:
            list[cp_model.IntVar]: A list of CP variables representing the result of the calculation.
        """
        raise NotImplementedError
