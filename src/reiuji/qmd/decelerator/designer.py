"""Designer for QMD decelerators."""

from ... import core
from .. import synchrotron
from . import constraints

import uuid

from ortools.sat.python import cp_model


class DeceleratorDesigner(core.designer.Designer):
    def __init__(
            self,
            side_length: int,
            minimum_energy: int,
            maximum_energy: int,
            target_focus: float,
            *,
            charge: float,
            mass: float,
            beam_strength: int,
            env_temperature: int = 300,
            kappa: float = 0.0025,
            scaling_factor: int = 10000,
            initial_focus: float = 0.0,
            heat_neutral: bool = True,
            internal_symmetry: bool = False,
            components: list[core.models.MultiblockComponent] | None = None,
            component_limits: dict[str, tuple[int, int]] | None = None
    ) -> None:
        self.side_length = side_length
        self.minimum_energy = minimum_energy
        self.maximum_energy = maximum_energy
        self.target_focus = target_focus
        self.charge = charge
        self.mass = mass
        self.beam_strength = beam_strength
        self.scaling_factor = scaling_factor
        self.initial_focus = initial_focus
        self.env_temperature = env_temperature
        self.kappa = kappa
        self.heat_neutral = heat_neutral
        self.internal_symmetry = internal_symmetry
        self.components = components if not isinstance(components, type(None)) else synchrotron.models.DEFAULT_COMPONENTS
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    def design(self, *, timeout: float | None = None) -> core.multi_sequence.MultiSequence[core.models.MultiblockComponent] | None:
        side_length = self.side_length + 4
        model = cp_model.CpModel()
        seq = core.multi_sequence.MultiSequence([model.NewIntVar(0, len(self.components) - 1, str(uuid.uuid4())) for i in range(side_length * side_length * 5)], (side_length, side_length, 5))
        synchrotron.constraints.CasingConstraint().to_model(model, seq, self.components)
        synchrotron.constraints.BeamConstraint().to_model(model, seq, self.components)
        synchrotron.constraints.AirConstraint().to_model(model, seq, self.components)
        synchrotron.constraints.CavityConstraint().to_model(model, seq, self.components)
        constraints.OneCavityConstraint().to_model(model, seq, self.components)
        synchrotron.constraints.MagnetConstraint().to_model(model, seq, self.components)
        core.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        if self.heat_neutral:
            sa = (seq.shape[0] * seq.shape[2]) * 4 + ((seq.shape[0] - 10) * seq.shape[2]) * 4 + (seq.shape[0] * seq.shape[1] * 2) - ((seq.shape[0] - 10) * (seq.shape[1] - 10) * 2)
            synchrotron.constraints.HeatNeutralConstraint(round(self.kappa * sa * self.env_temperature)).to_model(model, seq, self.components)
        if self.internal_symmetry:
            synchrotron.constraints.InnerSymmetryConstraint().to_model(model, seq, self.components)
        constraints.EnergyConstraint(self.minimum_energy, self.maximum_energy, self.charge, (seq.shape[0] - 4) / 2, self.mass).to_model(model, seq, self.components)
        synchrotron.constraints.BeamFocusConstraint(self.target_focus, self.charge, self.beam_strength, self.scaling_factor, self.initial_focus).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            core.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Minimize(synchrotron.calculations.PowerRequirement().to_model(model, seq, self.components))

        solver = cp_model.CpSolver()
        if isinstance(timeout, float):
            solver.parameters.max_time_in_seconds = timeout
        status = solver.Solve(model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return core.multi_sequence.MultiSequence([self.components[solver.Value(comp)] for comp in seq], (side_length, side_length, 5))
        elif status == cp_model.INFEASIBLE:
            return None
        raise RuntimeError(f"Solver status: {status}")
