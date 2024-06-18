"""Optimizer tests for the `reiuji.core.core.placement_rules` module."""

import uuid

import pytest
from ortools.sat.python import cp_model

from reiuji.core.core import placement_rules


@pytest.fixture
def mapping() -> list[tuple[str, str]]:
    return [
        ("air", ""),
        ("cell", "a"),
        ("cell", "b"),
        ("sink", "glowstone"),
        ("sink", "redstone"),
        ("sink", "end_stone"),
    ]


@pytest.fixture
def rules() -> list[placement_rules.PlacementRule]:
    return [
        placement_rules.AdjacencyPlacementRule(req_name="cell", amount=2),
        placement_rules.AdjacencyPlacementRule(
            req_name="cell", amount=2, count_type=placement_rules.CountType.EXACTLY
        ),
        placement_rules.AdjacencyPlacementRule(
            req_name="cell", amount=2, count_type=placement_rules.CountType.AT_MOST
        ),
        placement_rules.AdjacencyPlacementRule(
            req_name="sink", req_type="glowstone", amount=2
        ),
        placement_rules.AdjacencyPlacementRule(
            req_name="cell",
            amount=2,
            adjacency_type=placement_rules.AdjacencyType.AXIAL,
        ),
        placement_rules.AdjacencyPlacementRule(
            req_name="cell",
            amount=3,
            adjacency_type=placement_rules.AdjacencyType.VERTEX,
        ),
        placement_rules.AdjacencyPlacementRule(
            req_name="cell", amount=2, adjacency_type=placement_rules.AdjacencyType.EDGE
        ),
        placement_rules.CompoundPlacementRule(
            subrules=[
                placement_rules.AdjacencyPlacementRule(req_name="cell", amount=2),
                placement_rules.AdjacencyPlacementRule(
                    req_name="sink", req_type="glowstone", amount=2
                ),
            ],
            logic_type=placement_rules.LogicType.AND,
        ),
        placement_rules.CompoundPlacementRule(
            subrules=[
                placement_rules.AdjacencyPlacementRule(req_name="cell", amount=4),
                placement_rules.AdjacencyPlacementRule(
                    req_name="sink", req_type="glowstone", amount=4
                ),
            ],
            logic_type=placement_rules.LogicType.OR,
        ),
    ]


def test_cp_opt(
    rules: list[placement_rules.PlacementRule], mapping: list[tuple[str, str]]
) -> None:
    for rule in rules:
        model = cp_model.CpModel()
        neighbors = [
            placement_rules.CPNeighbor(
                id=model.new_int_var(0, len(mapping) - 1, str(uuid.uuid4())),
                active=model.new_bool_var(str(uuid.uuid4())),
            )
            for _ in range(6)
        ]
        target = model.new_bool_var(str(uuid.uuid4()))
        rule.to_cp_model(model, neighbors, mapping, target)
        model.add(target == 1)
        solver = cp_model.CpSolver()
        status = solver.solve(model)
        assert status == cp_model.OPTIMAL
        assert rule.is_satisfied(
            [
                placement_rules.Neighbor(
                    name=mapping[solver.value(neighbors[i].id)][0],
                    type=mapping[solver.value(neighbors[i].id)][1],
                    active=bool(solver.value(neighbors[i].active)),
                )
                for i in range(6)
            ]
        )
