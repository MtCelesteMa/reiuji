"""Designer for QMD synchrotrons."""

from ... import core
from . import models, constraints, calculations

import uuid

from ortools.sat.python import cp_model


class SynchrotronDesigner(core.designer.Designer):
    def __init__(
            self,
            side_length: int,
            minimum_energy: int,
            maximum_energy: int,
            *,
            charge: float,
            mass: float,
            heat_neutral: bool = True,
            internal_symmetry: bool = False,
            components: list[core.models.MultiblockComponent] | None = None,
            component_limits: dict[str, tuple[int, int]] | None = None
    ) -> None:
        self.side_length = side_length
        self.minimum_energy = minimum_energy
        self.maximum_energy = maximum_energy
        self.charge = charge
        self.mass = mass
        self.heat_neutral = heat_neutral
        self.internal_symmetry = internal_symmetry
        self.components = components if not isinstance(components, type(None)) else models.DEFAULT_COMPONENTS
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    def design(self, *, timeout: float | None = None) -> core.multi_sequence.MultiSequence[core.models.MultiblockComponent] | None:
        side_length = self.side_length + 4
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for i in range(side_length * side_length * 5)], (side_length, side_length, 5))
        constraints.CasingConstraint().to_model(model, seq, self.components)
        constraints.BeamConstraint().to_model(model, seq, self.components)
        constraints.AirConstraint().to_model(model, seq, self.components)
        constraints.CavityConstraint().to_model(model, seq, self.components)
        constraints.MagnetConstraint().to_model(model, seq, self.components)
        core.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        if self.heat_neutral:
            constraints.HeatNeutralConstraint().to_model(model, seq, self.components)
        if self.internal_symmetry:
            constraints.InnerSymmetryConstraint().to_model(model, seq, self.components)
        constraints.EnergyConstraint(self.minimum_energy, self.maximum_energy, self.charge, (seq.shape[0] - 4) / 2, self.mass).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            core.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)

        solver = cp_model.CpSolver()
        if isinstance(timeout, float):
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], (side_length, side_length, 5))
        elif status == cp_model.INFEASIBLE:
            return None
        raise RuntimeError(f"Solver status: {status}")
