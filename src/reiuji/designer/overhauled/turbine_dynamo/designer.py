"""Designer for NuclearCraft: Overhauled turbine dynamos."""

from .... import core
from ....components.types import *
from ....components.defaults import OVERHAULED_TURBINE_DYNAMO_COMPONENTS
from ... import base
from . import constraints, calculations

from ortools.sat.python import cp_model


class TurbineDynamoDesigner(base.designer.Designer):
    def __init__(
            self,
            side_length: int,
            *,
            shaft_width: int = 1,
            x_symmetry: bool = False,
            y_symmetry: bool = False,
            components: list[Component] | None = None,
            component_limits: dict[str, tuple[int | None, int | None]] | None = None
    ) -> None:
        super().__init__(components=components if not isinstance(components, type(None)) else OVERHAULED_TURBINE_DYNAMO_COMPONENTS)
        self.side_length = side_length
        self.shaft_width = shaft_width
        self.x_symmetry = x_symmetry
        self.y_symmetry = y_symmetry
        self.component_limits = component_limits if not isinstance(component_limits, type(None)) else dict()
    
    @property
    def seq_shape(self) -> tuple[int, ...]:
        return self.side_length + 2, self.side_length + 2
    
    def build_model(self, model: cp_model.CpModel, seq: core.multi_sequence.MultiSequence[cp_model.IntVar]) -> None:
        base.constraints.CasingConstraint().to_model(model, seq, self.components)
        base.constraints.PlacementRuleConstraint().to_model(model, seq, self.components)
        constraints.CenteredBearingConstraint(self.shaft_width).to_model(model, seq, self.components)
        if self.x_symmetry:
            base.constraints.SymmetryConstraint(1).to_model(model, seq, self.components)
        if self.y_symmetry:
            base.constraints.SymmetryConstraint(0).to_model(model, seq, self.components)
        for component, (min_, max_) in self.component_limits.items():
            base.constraints.QuantityConstraint(component, max_, min_).to_model(model, seq, self.components)
        model.Maximize(calculations.TurbineDynamoConductivity().to_model(model, seq, self.components))
