"""Base class for multiblock designers."""

from ... import core
from ...components.types import *


import uuid
import math

from ortools.sat.python import cp_model
from ortools.sat import cp_model_pb2


class Designer:
    """Base class for multiblock designers."""
    def __init__(self, *, components: list[Component]) -> None:
        self.components = components
    
    @property
    def seq_shape(self) -> tuple[int, ...]:
        """The shape of the sequence.

        Returns:
            tuple[int, ...]: The shape of the sequence.
        """
        raise NotImplementedError

    def build_model(self, model: cp_model.CpModel, seq: core.multi_sequence.MultiSequence[cp_model.IntVar]) -> None:
        """Build the constraint programming model.

        Args:
            model (cp_model.CpModel): The constraint programming model.
            seq (core.multi_sequence.MultiSequence[cp_model.IntVar]): The sequence of components.
        """
        raise NotImplementedError
    
    def design(self, *, timeout: float | None = None) -> tuple[cp_model_pb2.CpSolverStatus, core.multi_sequence.MultiSequence[Component] | None]:
        """Design a multiblock structure.

        Returns:
            tuple[cp_model_pb2.CpSolverStatus, core.multi_sequence.MultiSequence[core.components.Component]]: The status of the solver and the designed multiblock structure.
        """
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for _ in range(math.prod(self.seq_shape))], self.seq_shape)
        self.build_model(model, seq)

        solver = cp_model.CpSolver()
        if isinstance(timeout, float):
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return status, core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], self.seq_shape)
        return status, None
