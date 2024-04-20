"""Tests for the `core.constraints` package."""

from reiuji.core.models import MultiblockComponent
from reiuji.core.multi_sequence import MultiSequence
from reiuji.core.placement_rules import parse_rule_string
from reiuji.core.constraints import CasingConstraint, PlacementRuleConstraint, SymmetryConstraint

from ortools.sat.python import cp_model


COMPONENTS = [
    MultiblockComponent(name="", type="casing"),
    MultiblockComponent(name="", type="cell"),
    MultiblockComponent(name="", type="reflector"),
    MultiblockComponent(name="", type="moderator"),
    MultiblockComponent(name="", type="yoke"),
    MultiblockComponent(name="", type="cavity"),
    MultiblockComponent(name="glowstone", type="sink", placement_rule="one cell"),
    MultiblockComponent(name="redstone", type="sink", placement_rule="one glowstone sink"),
    MultiblockComponent(name="iron", type="sink", placement_rule="one cell && one moderator"),
    MultiblockComponent(name="glowstone", type="heater", placement_rule="one cell"),
    MultiblockComponent(name="redstone", type="heater", placement_rule="one glowstone heater"),
    MultiblockComponent(name="iron", type="heater", placement_rule="one cell && one moderator")
]


def test_casing_constraint() -> None:
    seq1 = MultiSequence([COMPONENTS[0], COMPONENTS[0], COMPONENTS[0], COMPONENTS[0], COMPONENTS[1], COMPONENTS[0], COMPONENTS[0], COMPONENTS[0], COMPONENTS[0]], (3, 3))
    seq2 = MultiSequence([COMPONENTS[0], COMPONENTS[1], COMPONENTS[0], COMPONENTS[0], COMPONENTS[1], COMPONENTS[0], COMPONENTS[0], COMPONENTS[0], COMPONENTS[0]], (3, 3))
    assert CasingConstraint(COMPONENTS[0]).is_satisfied(seq1)
    assert not CasingConstraint(COMPONENTS[0]).is_satisfied(seq2)


def test_symmetry_constraint() -> None:
    seq1 = MultiSequence([COMPONENTS[0], COMPONENTS[1], COMPONENTS[0], COMPONENTS[1], COMPONENTS[1], COMPONENTS[0], COMPONENTS[0], COMPONENTS[1], COMPONENTS[0]], (3, 3))
    assert SymmetryConstraint(0).is_satisfied(seq1)
    assert not SymmetryConstraint(1).is_satisfied(seq1)


CONSTRAINTS = [
    CasingConstraint(COMPONENTS[0]),
    PlacementRuleConstraint(),
    SymmetryConstraint(0),
    SymmetryConstraint(1),
    SymmetryConstraint(2)
]


def test_to_model() -> None:
    model = cp_model.CpModel()
    seq = MultiSequence([model.NewIntVar(0, len(COMPONENTS) - 1, f"component_{i}") for i in range(125)], (5, 5, 5))
    for constraint in CONSTRAINTS:
        constraint.to_model(model, seq, COMPONENTS)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    solution = MultiSequence([COMPONENTS[solver.Value(comp)] for comp in seq], (5, 5, 5))
    assert all(constraint.is_satisfied(solution) for constraint in CONSTRAINTS)
