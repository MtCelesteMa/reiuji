"""Designer for QMD nucleosynthesis chambers."""

from ... import core
from . import models, constraints, calculations

import uuid

from ortools.sat.python import cp_model


class NucleosynthesisDesigner(core.designer.Designer):
    def __init__(
            self,
            *,
            recipe_heat: int,
            x_symmetry: bool = False,
            z_symmetry: bool = False,
            components: list[core.models.MultiblockComponent] | None = None,
            component_limits: dict[str, tuple[int, int]] | None = None
    ) -> None:
        self.recipe_heat = recipe_heat
        self.x_symmetry = x_symmetry
        self.z_symmetry = z_symmetry
        self.components = components if not isinstance(components, type(None)) else models.DEFAULT_COMPONENTS
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    def design(self, *, timeout: float | None = None) -> core.multi_sequence.MultiSequence[core.models.MultiblockComponent] | None:
        shape = (5, 11, 7)
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for i in range(shape[0] * shape[1] * shape[2])], shape)
        core.constraints.CasingConstraint().to_model(model, seq, self.components)
        core.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        constraints.StructureConstraint().to_model(model, seq, self.components)
        heating = calculations.TotalHeatingRate().to_model(model, seq, self.components)
        cooling = calculations.TotalCoolingRate().to_model(model, seq, self.components)
        if self.x_symmetry:
            core.constraints.SymmetryConstraint(0).to_model(model, seq, self.components)
        if self.z_symmetry:
            core.constraints.SymmetryConstraint(1).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            core.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Add(self.recipe_heat <= cooling)
        model.Minimize(cooling - self.recipe_heat)

        solver = cp_model.CpSolver()
        if timeout:
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], (5, 11, 7))
        elif status == cp_model.INFEASIBLE:
            return None
        raise RuntimeError(f"Solver status: {status}")
