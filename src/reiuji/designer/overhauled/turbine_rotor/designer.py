"""Designer for NuclearCraft: Overhauled turbine rotors."""

from .... import core
from ....components.types import *
from ....components.defaults import OVERHAULED_TURBINE_ROTOR_COMPONENTS
from ... import base
from . import calculations

from ortools.sat.python import cp_model


class TurbineRotorDesigner(base.designer.Designer):
    def __init__(
            self,
            length: int,
            optimal_expansion: float,
            *,
            components: list[Component] | None = None,
            component_limits: dict[str, tuple[int | None, int | None]] | None = None
    ) -> None:
        super().__init__(components=components if not isinstance(components, type(None)) else OVERHAULED_TURBINE_ROTOR_COMPONENTS)
        self.length = length
        self.optimal_expansion = optimal_expansion
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    @property
    def seq_shape(self) -> tuple[int, ...]:
        return (self.length,)
    
    def build_model(self, model: cp_model.CpModel, seq: core.multi_sequence.MultiSequence[cp_model.IntVar]) -> None:
        for component, (min_, max_) in self.component_limits.items():
            base.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Maximize(calculations.TurbineRotorEfficiency(self.optimal_expansion).to_model(model, seq, self.components))
