"""Constraints for designing multiblocks."""

from ... import core
from ...components.types import *

from . import placement_rules

import uuid

from ortools.sat.python import cp_model


class Constraint:
    """Represents a constraint that can be applied to a multiblock sequence."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        """Checks if the given sequence satisfies the constraint.

        Args:
            seq (core.multi_sequence.MultiSequence[core.components.Component]): The sequence to be checked.

        Returns:
            bool: True if the sequence satisfies the constraint, False otherwise.
        """
        raise NotImplementedError
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        """Adds the constraint to the given model.

        Args:
            model (cp_model.CpModel): The model to which the constraint will be added.
            seq (core.multi_sequence.MultiSequence[cp_model.IntVar]): The sequence to which the constraint will be applied.
            components (list[core.components.Component]): The list of multiblock components.

        Returns:
            None
        """
        raise NotImplementedError


class CasingConstraint(Constraint):
    """Ensures that casing blocks are placed at the exterior of the sequence."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            if any([idx_ == 0 for idx_, dim in zip(idx, seq.shape)]) or any([idx_ == dim - 1 for idx_, dim in zip(idx, seq.shape)]):
                if component.type != "casing":
                    return False
            else:
                if component.type == "casing":
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
        casing_ids = type_to_id["casing"]
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            if any([idx_ == 0 or idx_ == dim - 1 for idx_, dim in zip(idx, seq.shape)]):
                model.AddAllowedAssignments([component], [(casing_id,) for casing_id in casing_ids])
            else:
                model.AddForbiddenAssignments([component], [(casing_id,) for casing_id in casing_ids])

class PlacementRuleConstraint(Constraint):
    """Ensures that all placement rules are satisfied."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            neighbors = []
            for dim in range(len(seq.shape)):
                a, b = seq.neighbors(idx, dim)
                neighbors.append(a)
                neighbors.append(b)
            if None in neighbors:
                continue
            rule = placement_rules.parse_rule_string(component.placement_rule)
            if not rule.is_satisfied(neighbors):
                return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        rules = [placement_rules.parse_rule_string(component.placement_rule) for component in components]
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            neighbors = []
            for dim in range(len(seq.shape)):
                a, b = seq.neighbors(idx, dim)
                neighbors.append(a)
                neighbors.append(b)
            if None in neighbors:
                continue
            rule_satisfied = [rule.to_model(model, neighbors, components) for rule in rules]
            model.AddElement(component, rule_satisfied, 1)


class SymmetryConstraint(Constraint):
    """Ensures that the sequence is symmetric along the given axis."""
    def __init__(self, axis: int) -> None:
        self.axis = axis

    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            mirror_idx = (idx[:self.axis] + (seq.shape[self.axis] - 1 - idx[self.axis],) + idx[self.axis + 1:])
            if component != seq[mirror_idx]:
                return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            mirror_idx = (idx[:self.axis] + (seq.shape[self.axis] - 1 - idx[self.axis],) + idx[self.axis + 1:])
            model.Add(component == seq[mirror_idx])


class QuantityConstraint(Constraint):
    """Limits the number of a specific component type in the sequence."""
    def __init__(self, component_full_name: str, max_quantity: int | None = None, min_quantity: int | None = None) -> None:
        self.component_full_name = component_full_name
        self.max_quantity = max_quantity
        self.min_quantity = min_quantity if isinstance(min_quantity, int) else 0
    
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        count = sum([1 for component in seq if component.full_name == self.component_full_name])
        if count < self.min_quantity or (isinstance(self.max_quantity, int) and count > self.max_quantity):
            return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        component_id = [component.full_name for component in components].index(self.component_full_name)
        is_equal = [model.NewBoolVar(str(uuid.uuid4())) for _ in seq]
        for i, component in enumerate(seq):
            model.Add(component == component_id).OnlyEnforceIf(is_equal[i])
            model.Add(component != component_id).OnlyEnforceIf(is_equal[i].Not())
        model.Add(sum(is_equal) >= self.min_quantity)
        if isinstance(self.max_quantity, int):
            model.Add(sum(is_equal) <= self.max_quantity)
