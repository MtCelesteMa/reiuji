"""Constraints for designing multiblocks."""

from . import multi_sequence
from . import models
from . import placement_rules

import uuid

from ortools.sat.python import cp_model


class Constraint:
    """Represents a constraint that can be applied to a multiblock sequence."""
    def is_satisfied(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> bool:
        """Checks if the given sequence satisfies the constraint.

        Args:
            seq (multi_sequence.MultiSequence[models.MultiblockComponent]): The sequence to be checked.

        Returns:
            bool: True if the sequence satisfies the constraint, False otherwise.
        """
        raise NotImplementedError
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[models.MultiblockComponent]
    ) -> None:
        """Adds the constraint to the given model.

        Args:
            model (cp_model.CpModel): The model to which the constraint will be added.
            seq (multi_sequence.MultiSequence[cp_model.IntVar]): The sequence to which the constraint will be applied.
            components (list[models.MultiblockComponent]): The list of multiblock components.

        Returns:
            None
        """
        raise NotImplementedError


class CasingConstraint(Constraint):
    """Ensures that casing blocks are placed at the exterior of the sequence."""
    def __init__(self, casing: models.MultiblockComponent):
        self.casing = casing
    
    def is_satisfied(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> bool:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            if any([idx_ == 0 for idx_, dim in zip(idx, seq.shape)]) or any([idx_ == dim - 1 for idx_, dim in zip(idx, seq.shape)]):
                if component != self.casing:
                    return False
            else:
                if component == self.casing:
                    return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[models.MultiblockComponent]
    ) -> None:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            if any([idx_ == 0 for idx_, dim in zip(idx, seq.shape)]) or any([idx_ == dim - 1 for idx_, dim in zip(idx, seq.shape)]):
                model.Add(component == components.index(self.casing))
            else:
                model.Add(component != components.index(self.casing))


class PlacementRuleConstraint(Constraint):
    """Ensures that all placement rules are satisfied."""
    def is_satisfied(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> bool:
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
        seq: multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[models.MultiblockComponent]
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
    def __init__(self, axis: int) -> None:
        self.axis = axis

    def is_satisfied(self, seq: multi_sequence.MultiSequence[models.MultiblockComponent]) -> bool:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            mirror_idx = (idx[:self.axis] + (seq.shape[self.axis] - 1 - idx[self.axis],) + idx[self.axis + 1:])
            if component != seq[mirror_idx]:
                return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[models.MultiblockComponent]
    ) -> None:
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            mirror_idx = (idx[:self.axis] + (seq.shape[self.axis] - 1 - idx[self.axis],) + idx[self.axis + 1:])
            model.Add(component == seq[mirror_idx])
