"""Placement rules for multiblock components."""

from ... import core
from ...components.types import *

import uuid
import typing
import itertools
import math
import re

from ortools.sat.python import cp_model


class PlacementRule:
    """Represents a placement rule that determines whether a given list of neighbors satisfies the rule."""
    def to_dict(self) -> dict:
        """Converts the PlacementRule object to a dictionary.

        Returns:
            dict: A dictionary representation of the PlacementRule object.
        """
        raise NotImplementedError

    def is_satisfied(self, neighbors: list[Component]) -> bool:
        """Checks if the placement rule is satisfied by the given list of neighbors.

        Args:
            neighbors (list[Component]): A list of neighboring components.

        Returns:
            bool: True if the placement rule is satisfied, False otherwise.
        """
        raise NotImplementedError
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[Component]
    ) -> cp_model.IntVar:
        """Adds the placement rule to the CP model and returns whether it is satisfied as a variable.

        Args:
            model (cp_model.CpModel): The CP model to which the placement rule will be added.
            neighbors (list[cp_model.IntVar]): The list of neighbor variables.
            components (list[Component]): The list of multiblock components.

        Returns:
            cp_model.IntVar: A variable representing whether the placement rule is satisfied.
        """
        raise NotImplementedError


class EmptyPlacementRule(PlacementRule):
    """A placement rule that is always satisfied."""
    def to_dict(self) -> dict:
        return {}
    
    def is_satisfied(self, neighbors: list[Component]) -> bool:
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[Component]
    ) -> cp_model.IntVar:
        return model.NewBoolVar(str(uuid.uuid4()))


class NamePlacementRule(PlacementRule):
    def __init__(self, name: str, type: str, quantity: int, *, exact: bool = False, axial: bool = False) -> None:
        """Initialize a NamePlacementRule object.

        Args:
            name (str): The name of the required component.
            type (str): The type of the required component.
            quantity (int): The quantity of the required component required.
            exact (bool, optional): Whether the placement rule requires an exact match in quantity. Defaults to False.
            axial (bool, optional): Whether the placement rule is axial. Defaults to False.
        """
        self.name = name
        self.type = type
        self.quantity = quantity
        self.exact = exact
        self.axial = axial

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "quantity": self.quantity,
            "exact": self.exact,
            "axial": self.axial
        }
    
    def is_satisfied(self, neighbors: list[Component]) -> bool:
        count = 0
        for neighbor in neighbors:
            if neighbor.name == self.name and neighbor.type == self.type:
                count += 1
        axial = False
        for a, b in itertools.batched(neighbors, 2):
            if a.name == b.name == self.name and a.type == b.type == self.type:
                axial = True
                break
        if self.exact:
            return count == self.quantity and (not self.axial or axial)
        return count >= self.quantity and (not self.axial or axial)
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[Component]
    ) -> cp_model.IntVar:
        name_to_id = dict()
        for i, component in enumerate(components):
            if component.name not in name_to_id:
                name_to_id[component.name] = [i]
            else:
                name_to_id[component.name].append(i)
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)

        matches = [model.NewBoolVar(str(uuid.uuid4())) for _ in neighbors]
        for i, neighbor in enumerate(neighbors):
            name_matches = model.NewBoolVar(str(uuid.uuid4()))
            model.AddAllowedAssignments([neighbor], [(n,) for n in name_to_id[self.name]]).OnlyEnforceIf(name_matches)
            model.AddForbiddenAssignments([neighbor], [(n,) for n in name_to_id[self.name]]).OnlyEnforceIf(name_matches.Not())
            
            type_matches = model.NewBoolVar(str(uuid.uuid4()))
            model.AddAllowedAssignments([neighbor], [(n,) for n in type_to_id[self.type]]).OnlyEnforceIf(type_matches)
            model.AddForbiddenAssignments([neighbor], [(n,) for n in type_to_id[self.type]]).OnlyEnforceIf(type_matches.Not())

            model.AddBoolAnd([name_matches, type_matches]).OnlyEnforceIf(matches[i])
            model.AddBoolOr([name_matches.Not(), type_matches.Not()]).OnlyEnforceIf(matches[i].Not())
        over_threshold = model.NewBoolVar(str(uuid.uuid4()))
        if self.exact:
            model.Add(sum(matches) == self.quantity).OnlyEnforceIf(over_threshold)
            model.Add(sum(matches) != self.quantity).OnlyEnforceIf(over_threshold.Not())
        else:
            model.Add(sum(matches) >= self.quantity).OnlyEnforceIf(over_threshold)
            model.Add(sum(matches) < self.quantity).OnlyEnforceIf(over_threshold.Not())
        
        axials = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(len(neighbors) // 2)]
        for i in range(len(neighbors) // 2):
            model.AddBoolAnd([matches[i * 2], matches[i * 2 + 1]]).OnlyEnforceIf(axials[i])
            model.AddBoolOr([matches[i * 2].Not(), matches[i * 2 + 1].Not()]).OnlyEnforceIf(axials[i].Not())
        axial = model.NewBoolVar(str(uuid.uuid4()))
        model.AddBoolOr(axials).OnlyEnforceIf(axial)
        model.AddBoolAnd([axial_.Not() for axial_ in axials]).OnlyEnforceIf(axial.Not())

        satisfied = model.NewBoolVar(str(uuid.uuid4()))
        if self.axial:
            model.AddBoolAnd([axial, over_threshold]).OnlyEnforceIf(satisfied)
            model.AddBoolOr([axial.Not(), over_threshold.Not()]).OnlyEnforceIf(satisfied.Not())
        else:
            model.Add(over_threshold == satisfied)
        return satisfied


class TypePlacementRule(PlacementRule):
    def __init__(self, type: str, quantity: int, *, exact: bool = False, axial: bool = False, different: bool = False) -> None:
        """Initialize a TypePlacementRule object.

        Args:
            type (str): The type of the required component.
            quantity (int): The quantity of the required component required.
            exact (bool, optional): Whether the placement rule requires an exact match in quantity. Defaults to False.
            axial (bool, optional): Whether the placement rule is axial. Defaults to False.
            different (bool, optional): Whether the names of the components must be different. Defaults to False.
        """
        self.type = type
        self.quantity = quantity
        self.exact = exact
        self.axial = axial
        self.different = different
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "quantity": self.quantity,
            "exact": self.exact,
            "axial": self.axial,
            "different": self.different
        }
    
    def is_satisfied(self, neighbors: list[Component]) -> bool:
        count = 0
        for neighbor in neighbors:
            if neighbor.type == self.type:
                count += 1
        axial = False
        for a, b in itertools.batched(neighbors, 2):
            if a.type == b.type == self.type:
                axial = True
                break
        different_c = math.comb(len(neighbors), 2)
        for a, b in itertools.combinations(neighbors, 2):
            if a.name == b.name or a.type != self.type or b.type != self.type:
                different_c -= 1
        if self.exact:
            return count == self.quantity and (not self.axial or axial) and (not self.different or different_c >= math.comb(self.quantity, 2))
        return count >= self.quantity and (not self.axial or axial) and (not self.different or different_c >= math.comb(self.quantity, 2))
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)

        matches = [model.NewBoolVar(str(uuid.uuid4())) for _ in neighbors]
        for i, neighbor in enumerate(neighbors):
            model.AddAllowedAssignments([neighbor], [(n,) for n in type_to_id[self.type]]).OnlyEnforceIf(matches[i])
            model.AddForbiddenAssignments([neighbor], [(n,) for n in type_to_id[self.type]]).OnlyEnforceIf(matches[i].Not())
        over_threshold = model.NewBoolVar(str(uuid.uuid4()))
        if self.exact:
            model.Add(sum(matches) == self.quantity).OnlyEnforceIf(over_threshold)
            model.Add(sum(matches) != self.quantity).OnlyEnforceIf(over_threshold.Not())
        else:
            model.Add(sum(matches) >= self.quantity).OnlyEnforceIf(over_threshold)
            model.Add(sum(matches) < self.quantity).OnlyEnforceIf(over_threshold.Not())
        
        axials = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(len(neighbors) // 2)]
        for i in range(len(neighbors) // 2):
            model.AddBoolAnd([matches[i * 2], matches[i * 2 + 1]]).OnlyEnforceIf(axials[i])
            model.AddBoolOr([matches[i * 2].Not(), matches[i * 2 + 1].Not()]).OnlyEnforceIf(axials[i].Not())
        axial = model.NewBoolVar(str(uuid.uuid4()))
        model.AddBoolOr(axials).OnlyEnforceIf(axial)
        model.AddBoolAnd([axial_.Not() for axial_ in axials]).OnlyEnforceIf(axial.Not())

        differents = core.multi_sequence.MultiSequence([model.NewBoolVar(str(uuid.uuid4())) for _ in range(len(neighbors) ** 2)], shape=(len(neighbors), len(neighbors)))
        for i, j in itertools.product(range(len(neighbors)), repeat=2):
            if i == j:
                model.Add(differents[i, j] == 0)
            else:
                neighbors_different = model.NewBoolVar(str(uuid.uuid4()))
                model.Add(neighbors[i] != neighbors[j]).OnlyEnforceIf(neighbors_different)
                model.Add(neighbors[i] == neighbors[j]).OnlyEnforceIf(neighbors_different.Not())

                model.AddBoolAnd([neighbors_different, matches[i], matches[j]]).OnlyEnforceIf(differents[i, j])
                model.AddBoolOr([neighbors_different.Not(), matches[i].Not(), matches[j].Not()]).OnlyEnforceIf(differents[i, j].Not())
        diverse = model.NewBoolVar(str(uuid.uuid4()))
        model.Add(sum(differents) >= math.comb(self.quantity, 2)).OnlyEnforceIf(diverse)
        model.Add(sum(differents) < math.comb(self.quantity, 2)).OnlyEnforceIf(diverse.Not())

        satisfied = model.NewBoolVar(str(uuid.uuid4()))
        if self.different:
            if self.axial:
                model.AddBoolAnd([axial, over_threshold, diverse]).OnlyEnforceIf(satisfied)
                model.AddBoolOr([axial.Not(), over_threshold.Not(), diverse.Not()]).OnlyEnforceIf(satisfied.Not())
            else:
                model.AddBoolAnd([over_threshold, diverse]).OnlyEnforceIf(satisfied)
                model.AddBoolOr([over_threshold.Not(), diverse.Not()]).OnlyEnforceIf(satisfied.Not())
        else:
            if self.axial:
                model.AddBoolAnd([axial, over_threshold]).OnlyEnforceIf(satisfied)
                model.AddBoolOr([axial.Not(), over_threshold.Not()]).OnlyEnforceIf(satisfied.Not())
            else:
                model.Add(over_threshold == satisfied)
        return satisfied


class CompoundPlacementRule(PlacementRule):
    def __init__(self, rules: list[PlacementRule], *, mode: typing.Literal["AND", "OR"] = "AND") -> None:
        """Initialize a CompoundPlacementRule object.

        Args:
            rules (list[PlacementRule]): The list of placement rules to combine.
            mode (typing.Literal["AND", "OR"], optional): The mode of combination. Defaults to "AND".
        """
        self.rules = rules
        self.mode = mode
    
    def to_dict(self) -> dict:
        return {
            "rules": [rule.to_dict() for rule in self.rules],
            "mode": self.mode
        }
    
    def is_satisfied(self, neighbors: list[Component]) -> bool:
        satisfied = [rule.is_satisfied(neighbors) for rule in self.rules]
        if self.mode == "AND":
            return all(satisfied)
        return any(satisfied)
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[Component]
    ) -> cp_model.IntVar:
        satisfied = model.NewBoolVar(str(uuid.uuid4()))
        rule_satisfied = [rule.to_model(model, neighbors, components) for rule in self.rules]
        if self.mode == "AND":
            model.AddBoolAnd(rule_satisfied).OnlyEnforceIf(satisfied)
            model.AddBoolOr([rule_satisfied_.Not() for rule_satisfied_ in rule_satisfied]).OnlyEnforceIf(satisfied.Not())
        else:
            model.AddBoolOr(rule_satisfied).OnlyEnforceIf(satisfied)
            model.AddBoolAnd([rule_satisfied_.Not() for rule_satisfied_ in rule_satisfied]).OnlyEnforceIf(satisfied.Not())
        return satisfied


def parse_rule_string(s: str) -> PlacementRule:
    """Parses a rule string and returns a PlacementRule object.

    Args:
        s (str): The rule string to parse.

    Returns:
        PlacementRule: The parsed PlacementRule object.

    Raises:
        ValueError: If the rule string is invalid.
    """
    if len(s) == 0:
        return EmptyPlacementRule()
    if "&&" in s:
        return CompoundPlacementRule([parse_rule_string(sub) for sub in s.split(" && ", 1)], mode="AND")
    if "||" in s:
        return CompoundPlacementRule([parse_rule_string(sub) for sub in s.split(" || ", 1)], mode="OR")
    PATTERN = r"(?P<exact>exactly )?(?P<quantity>one|two|three|four|five|six) (?P<axial>axial )?(?P<different>different )?(?P<name>[\w_]+ )?(?P<type>[\w_]+)"
    QUANTITIES = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6
    }
    match = re.fullmatch(PATTERN, s)
    if isinstance(match, type(None)):
        raise ValueError(f"Invalid rule string: {s}")
    groups = match.groupdict()
    if not isinstance(groups["name"], type(None)):
        return NamePlacementRule(
            groups["name"].strip(),
            groups["type"].strip().rstrip("s" if (groups["quantity"] != "one" and groups["type"].strip() != "glass") else ""),
            QUANTITIES[groups["quantity"]],
            exact=not isinstance(groups["exact"], type(None)),
            axial=not isinstance(groups["axial"], type(None))
        )
    return TypePlacementRule(
        groups["type"].strip().rstrip("s" if (groups["quantity"] != "one" and groups["type"].strip() != "glass") else ""),
        QUANTITIES[groups["quantity"]],
        exact=not isinstance(groups["exact"], type(None)),
        axial=not isinstance(groups["axial"], type(None)),
        different=not isinstance(groups["different"], type(None))
    )
