"""Tests for the `core.scaled_calculations` module."""

from reiuji.core.scaled_calculations import multiply, divide, sqrt, SCALE_FACTOR

from ortools.sat.python import cp_model


def test_multiply() -> None:
    model = cp_model.CpModel()
    a = model.NewIntVar(0, cp_model.INT32_MAX, "a")
    b = model.NewIntVar(0, cp_model.INT32_MAX, "b")
    product = model.NewIntVar(0, cp_model.INT32_MAX, "product")
    model.Add(a == 2 * SCALE_FACTOR)
    model.Add(b == 5 * SCALE_FACTOR)
    multiply(model, product, a, b)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.Value(product) == 10 * SCALE_FACTOR


def test_divide() -> None:
    model = cp_model.CpModel()
    a = model.NewIntVar(0, cp_model.INT32_MAX, "a")
    b = model.NewIntVar(1, cp_model.INT32_MAX, "b")
    quotient = model.NewIntVar(0, cp_model.INT32_MAX, "quotient")
    model.Add(a == 10 * SCALE_FACTOR)
    model.Add(b == 2 * SCALE_FACTOR)
    divide(model, quotient, a, b)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.Value(quotient) == 5 * SCALE_FACTOR


def test_divide_neg() -> None:
    model = cp_model.CpModel()
    a = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, "a")
    b = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, "b")
    quotient = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, "quotient")
    model.Add(a == -10 * SCALE_FACTOR)
    model.Add(b == -2 * SCALE_FACTOR)
    divide(model, quotient, a, b)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.Value(quotient) == 5 * SCALE_FACTOR


def test_sqrt() -> None:
    model = cp_model.CpModel()
    a = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, "a")
    target = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, "target")
    sqrt(model, target, a)
    model.Add(a == 25 * SCALE_FACTOR)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.Value(target) == 5 * SCALE_FACTOR
