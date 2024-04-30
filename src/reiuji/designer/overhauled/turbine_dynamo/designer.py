"""Designer for NuclearCraft: Overhauled turbine dynamos."""

from ... import core
from . import models, constraints, calculations

import uuid

from ortools.sat.python import cp_model


class TurbineDynamoDesigner(core.designer.Designer):
    def __init__(
            self,
            side_length: int,
            *,
            shaft_width: int = 1,
            x_symmetry: bool = False,
            y_symmetry: bool = False,
            components: list[core.models.MultiblockComponent] | None = None,
            component_limits: dict[str, tuple[int, int]] | None = None
    ) -> None:
        self.side_length = side_length
        self.shaft_width = shaft_width
        self.x_symmetry = x_symmetry
        self.y_symmetry = y_symmetry
        self.components = components if not isinstance(components, type(None)) else models.DEFAULT_COMPONENTS
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    def design(self, *, timeout: float | None = None) -> core.multi_sequence.MultiSequence[core.models.MultiblockComponent] | None:
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for i in range((self.side_length + 2) ** 2)], (self.side_length + 2, self.side_length + 2))
        core.constraints.CasingConstraint().to_model(model, seq, self.components)
        core.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        constraints.CenteredBearingConstraint(self.shaft_width).to_model(model, seq, self.components)
        if self.x_symmetry:
            core.constraints.SymmetryConstraint(1).to_model(model, seq, self.components)
        if self.y_symmetry:
            core.constraints.SymmetryConstraint(0).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            core.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Maximize(calculations.TurbineDynamoConductivity().to_model(model, seq, self.components))

        solver = cp_model.CpSolver()
        if isinstance(timeout, float):
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], (self.side_length + 2, self.side_length + 2))
        elif status == cp_model.INFEASIBLE:
            return None
        raise RuntimeError(f"Solver status: {status}")