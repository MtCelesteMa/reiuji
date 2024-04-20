"""Placement rules for multiblock components."""

from . import models

import uuid
import typing
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

    def is_satisfied(self, neighbors: list[models.MultiblockComponent]) -> bool:
        """Checks if the placement rule is satisfied by the given list of neighbors.

        Args:
            neighbors (list[models.MultiblockComponent]): A list of neighboring components.

        Returns:
            bool: True if the placement rule is satisfied, False otherwise.
        """
        raise NotImplementedError
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[models.MultiblockComponent]
    ) -> cp_model.IntVar:
        """Adds the placement rule to the CP model and returns whether it is satisfied as a variable.

        Args:
            model (cp_model.CpModel): The CP model to which the placement rule will be added.
            neighbors (list[cp_model.IntVar]): The list of neighbor variables.
            components (list[models.MultiblockComponent]): The list of multiblock components.

        Returns:
            cp_model.IntVar: A variable representing whether the placement rule is satisfied.
        """
        raise NotImplementedError


class EmptyPlacementRule(PlacementRule):
    """A placement rule that is always satisfied."""
    def to_dict(self) -> dict:
        return {}
    
    def is_satisfied(self, neighbors: list[models.MultiblockComponent]) -> bool:
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[cp_model.IntVar],
        components: list[models.MultiblockComponent]
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


def parse_rule_string(s: str) -> PlacementRule:
    """Parses a rule string and returns a PlacementRule object.

    Args:
        s (str): The rule string to parse.

    Returns:
        PlacementRule: The parsed PlacementRule object.

    Raises:
        ValueError: If the rule string is invalid.
    """
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
            groups["type"].strip().rstrip("s" if groups["quantity"] != "one" else ""),
            QUANTITIES[groups["quantity"]],
            exact=not isinstance(groups["exact"], type(None)),
            axial=not isinstance(groups["axial"], type(None))
        )
    return TypePlacementRule(
        groups["type"].strip().rstrip("s" if groups["quantity"] != "one" else ""),
        QUANTITIES[groups["quantity"]],
        exact=not isinstance(groups["exact"], type(None)),
        axial=not isinstance(groups["axial"], type(None)),
        different=not isinstance(groups["different"], type(None))
    )
