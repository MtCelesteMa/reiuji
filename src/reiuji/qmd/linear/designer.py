"""Designer for QMD linear accelerators."""

from ... import core
from . import models, constraints, calculations

import uuid

from ortools.sat.python import cp_model


class LinearAcceleratorDesigner(core.designer.Designer):
    def __init__(
            self,
            length: int,
            minimum_energy: int,
            maximum_energy: int,
            target_focus: float,
            *,
            charge: float,
            beam_strength: int,
            scaling_factor: int = 10000,
            initial_focus: float = 0.0,
            heat_neutral: bool = True,
            y_symmetry: bool = False,
            z_symmetry: bool = False,
            components: list[core.models.MultiblockComponent] | None = None,
            component_limits: dict[str, tuple[int, int]] | None = None
    ) -> None:
        self.length = length
        self.minimum_energy = minimum_energy
        self.maximum_energy = maximum_energy
        self.target_focus = target_focus
        self.charge = charge
        self.beam_strength = beam_strength
        self.scaling_factor = scaling_factor
        self.initial_focus = initial_focus
        self.heat_neutral = heat_neutral
        self.y_symmetry = y_symmetry
        self.z_symmetry = z_symmetry
        self.components = components if not isinstance(components, type(None)) else models.DEFAULT_COMPONENTS
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    def design(self, *, timeout: float | None = None) -> core.multi_sequence.MultiSequence[core.models.MultiblockComponent] | None:
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for i in range((self.length + 2) * 5 * 5)], (self.length + 2, 5, 5))
        core.constraints.CasingConstraint().to_model(model, seq, self.components)
        core.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        constraints.BeamConstraint().to_model(model, seq, self.components)
        constraints.CavityConstraint().to_model(model, seq, self.components)
        constraints.MagnetConstraint().to_model(model, seq, self.components)
        if self.heat_neutral:
            constraints.HeatNeutralConstraint().to_model(model, seq, self.components)
        if self.y_symmetry:
            core.constraints.SymmetryConstraint(1).to_model(model, seq, self.components)
        if self.z_symmetry:
            core.constraints.SymmetryConstraint(2).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            core.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        constraints.BeamFocusConstraint(self.target_focus, self.charge, self.beam_strength, self.scaling_factor, self.initial_focus).to_model(model, seq, self.components)
        constraints.EnergyConstraint(self.minimum_energy, self.maximum_energy, self.charge).to_model(model, seq, self.components)
        
        solver = cp_model.CpSolver()
        if isinstance(timeout, float):
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], (self.length + 2, 5, 5))
        elif status == cp_model.INFEASIBLE:
            return None
        raise RuntimeError(f"Solver status: {status}")
