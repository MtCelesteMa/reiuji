"""Tests for the `scaled_calculations` module."""

from reiuji.core.scaled_calculations import multiply, divide

from ortools.sat.python import cp_model


def test_multiply() -> None:
    model = cp_model.CpModel()
    a = model.NewIntVar(0, 1000, "a")
    b = model.NewIntVar(0, 1000, "b")
    product = multiply(model, a, b)
    model.Add(a == 200)
    model.Add(b == 500)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.Value(product) == 1000


def test_divide() -> None:
    model = cp_model.CpModel()
    a = model.NewIntVar(0, 1000, "a")
    b = model.NewIntVar(1, 1000, "b")
    quotient = divide(model, a, b)
    model.Add(a == 1000)
    model.Add(b == 200)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.Value(quotient) == 500
