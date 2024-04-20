"""Tests for the `core.placement_rules` package."""

from reiuji.core.models import MultiblockComponent
from reiuji.core.placement_rules import parse_rule_string

from ortools.sat.python import cp_model


RULE_STRINGS = [
    "one cell",
    "two cells",
    "one cell && one moderator",
    "two axial glowstone sinks",
    "one reflector && one iron heater",
    "exactly two different sinks",
    "two different heaters",
    "one yoke && one cavity",
    "one iron heater || exactly two reflectors"
]

COMPONENTS = [
    MultiblockComponent(name="", type="cell"),
    MultiblockComponent(name="", type="reflector"),
    MultiblockComponent(name="", type="moderator"),
    MultiblockComponent(name="", type="yoke"),
    MultiblockComponent(name="", type="cavity"),
    MultiblockComponent(name="glowstone", type="sink"),
    MultiblockComponent(name="redstone", type="sink"),
    MultiblockComponent(name="iron", type="sink"),
    MultiblockComponent(name="glowstone", type="heater"),
    MultiblockComponent(name="redstone", type="heater"),
    MultiblockComponent(name="iron", type="heater"),
]


def test_to_model() -> None:
    for rule_str in RULE_STRINGS:
        rule = parse_rule_string(rule_str)
        print(rule_str)
        print(rule.to_dict())
        model = cp_model.CpModel()
        neighbors = [model.NewIntVar(0, len(COMPONENTS) - 1, f"neighbor_{i}") for i in range(6)]
        satisfied = rule.to_model(model, neighbors, COMPONENTS)
        model.Add(satisfied == 1)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE
        neighbors_sol = [COMPONENTS[solver.Value(neighbor)] for neighbor in neighbors]
        print(neighbors_sol)
        assert rule.is_satisfied(neighbors_sol)
