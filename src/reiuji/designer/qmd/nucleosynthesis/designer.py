"""Designer for QMD nucleosynthesis chambers."""

from .... import core
from ....components.types import *
from ....components.defaults import QMD_NUCLEOSYNTHESIS_COMPONENTS
from ... import base
from . import constraints, calculations

from ortools.sat.python import cp_model


class NucleosynthesisDesigner(base.designer.Designer):
    def __init__(
            self,
            *,
            recipe_heat: int,
            x_symmetry: bool = False,
            z_symmetry: bool = False,
            components: list[Component] | None = None,
            component_limits: dict[str, tuple[int | None, int | None]] | None = None
    ) -> None:
        super().__init__(components=components if not isinstance(components, type(None)) else QMD_NUCLEOSYNTHESIS_COMPONENTS)
        self.recipe_heat = recipe_heat
        self.x_symmetry = x_symmetry
        self.z_symmetry = z_symmetry
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    @property
    def seq_shape(self) -> tuple[int, ...]:
        return (5, 11, 7)
    
    def build_model(self, model: cp_model.CpModel, seq: core.multi_sequence.MultiSequence[cp_model.IntVar]) -> None:
        base.constraints.CasingConstraint().to_model(model, seq, self.components)
        base.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        constraints.StructureConstraint().to_model(model, seq, self.components)
        heating = calculations.TotalHeatingRate().to_model(model, seq, self.components)
        cooling = calculations.TotalCoolingRate().to_model(model, seq, self.components)
        if self.x_symmetry:
            base.constraints.SymmetryConstraint(0).to_model(model, seq, self.components)
        if self.z_symmetry:
            base.constraints.SymmetryConstraint(1).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            base.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Add(self.recipe_heat <= cooling)
        model.Minimize(cooling - self.recipe_heat)
