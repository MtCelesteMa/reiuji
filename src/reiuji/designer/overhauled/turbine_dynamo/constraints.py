"""Constraints specific to NuclearCraft: Overhauled's turbine dynamo designer."""

from .... import core
from ....components.types import *
from ... import base

from ortools.sat.python import cp_model


class CenteredBearingConstraint(base.constraints.Constraint):
    """Ensures that the bearings are centered in the dynamo."""
    def __init__(self, shaft_width: int) -> None:
        self.shaft_width = shaft_width
    
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        if len(seq.shape) != 2:
            raise ValueError("The sequence must be two-dimensional.")
        for i, component in enumerate(seq):
            y, x = seq.index_int_to_tuple(i)
            if seq.shape[0] % 2:
                mid = (seq.shape[0] - 1) // 2
                r = (self.shaft_width - 1) // 2
                if mid - r <= x <= mid + r and mid - r <= y <= mid + r:
                    if component.type != "bearing":
                        return False
                else:
                    if component.type == "bearing":
                        return False
            else:
                mid = seq.shape[0] // 2
                r_left = self.shaft_width // 2 - 1
                r_right = self.shaft_width // 2
                if mid - r_left <= x <= mid + r_right and mid - r_left <= y <= mid + r_right:
                    if component.type != "bearing":
                        return False
                else:
                    if component.type == "bearing":
                        return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        bearing_ids = type_to_id["bearing"]
        if len(seq.shape) != 2:
            raise ValueError("The sequence must be two-dimensional.")
        for i, component in enumerate(seq):
            y, x = seq.index_int_to_tuple(i)
            if seq.shape[0] % 2:
                mid = (seq.shape[0] - 1) // 2
                r = (self.shaft_width - 1) // 2
                if mid - r <= x <= mid + r and mid - r <= y <= mid + r:
                    model.AddAllowedAssignments([component], [(bearing_id,) for bearing_id in bearing_ids])
                else:
                    model.AddForbiddenAssignments([component], [(bearing_id,) for bearing_id in bearing_ids])
            else:
                mid = seq.shape[0] // 2
                r_left = self.shaft_width // 2 - 1
                r_right = self.shaft_width // 2
                if mid - r_left <= x <= mid + r_right and mid - r_left <= y <= mid + r_right:
                    model.AddAllowedAssignments([component], [(bearing_id,) for bearing_id in bearing_ids])
                else:
                    model.AddForbiddenAssignments([component], [(bearing_id,) for bearing_id in bearing_ids])
