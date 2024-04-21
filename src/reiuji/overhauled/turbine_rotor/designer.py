"""Designer for NuclearCraft: Overhauled turbine rotors."""

from ... import core
from . import models, calculations

import uuid

from ortools.sat.python import cp_model


class TurbineRotorDesigner(core.designer.Designer):
    def __init__(
            self,
            length: int,
            optimal_expansion: float,
            *,
            components: list[core.models.MultiblockComponent] | None = None,
            component_limits: dict[str, tuple[int, int]] | None = None
    ) -> None:
        self.length = length
        self.optimal_expansion = optimal_expansion
        self.components = components if not isinstance(components, type(None)) else models.DEFAULT_COMPONENTS
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()

    def design(self, *, timeout: float | None = None) -> core.multi_sequence.MultiSequence[core.models.MultiblockComponent] | None:
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for i in range(self.length)], (self.length,))
        for component, (min_, max_) in self.component_limits.items():
            core.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Maximize(calculations.TurbineRotorEfficiency(self.optimal_expansion).to_model(model, seq, self.components))

        solver = cp_model.CpSolver()
        if isinstance(timeout, float):
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], (self.length,))
        elif status == cp_model.INFEASIBLE:
            return None
        raise RuntimeError(f"Solver status: {status}")
