"""Designer for QMD synchrotrons."""

from .... import core
from ....components.types import *
from ....components.defaults import QMD_ACCELERATOR_COMPONENTS
from ... import base
from . import constraints, calculations

from ortools.sat.python import cp_model


class SynchrotronDesigner(base.designer.Designer):
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
            components: list[Component] | None = None,
            component_limits: dict[str, tuple[int | None, int | None]] | None = None
    ) -> None:
        super().__init__(components=components if not isinstance(components, type(None)) else QMD_ACCELERATOR_COMPONENTS)
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
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()

    @property
    def seq_shape(self) -> tuple[int, ...]:
        return (self.side_length + 4, self.side_length + 4, 5)
    
    def build_model(self, model: cp_model.CpModel, seq: core.multi_sequence.MultiSequence[cp_model.IntVar]) -> None:
        constraints.CasingConstraint().to_model(model, seq, self.components)
        constraints.BeamConstraint().to_model(model, seq, self.components)
        constraints.AirConstraint().to_model(model, seq, self.components)
        constraints.CavityConstraint().to_model(model, seq, self.components)
        constraints.MagnetConstraint().to_model(model, seq, self.components)
        base.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        if self.heat_neutral:
            sa = (seq.shape[0] * seq.shape[2]) * 4 + ((seq.shape[0] - 10) * seq.shape[2]) * 4 + (seq.shape[0] * seq.shape[1] * 2) - ((seq.shape[0] - 10) * (seq.shape[1] - 10) * 2)
            constraints.HeatNeutralConstraint(round(self.kappa * sa * self.env_temperature)).to_model(model, seq, self.components)
        if self.internal_symmetry:
            constraints.InnerSymmetryConstraint().to_model(model, seq, self.components)
        constraints.EnergyConstraint(self.minimum_energy, self.maximum_energy, self.charge, (seq.shape[0] - 4) / 2, self.mass).to_model(model, seq, self.components)
        constraints.BeamFocusConstraint(self.target_focus, self.charge, self.beam_strength, self.scaling_factor, self.initial_focus).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            base.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Minimize(calculations.PowerRequirement().to_model(model, seq, self.components))
