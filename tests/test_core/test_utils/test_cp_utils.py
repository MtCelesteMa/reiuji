"""Tests for the `reiuji.core.utils.cp_utils` module."""

from reiuji.core.utils import cp_utils

from ortools.sat.python import cp_model


def test_multiply() -> None:
    model = cp_model.CpModel()
    a = model.new_int_var_from_domain(cp_utils.std_domain(), "a")
    b = model.new_int_var_from_domain(cp_utils.std_domain(), "b")
    product = model.new_int_var_from_domain(cp_utils.std_domain(), "product")
    model.add(a == 2 * cp_utils.SCALE_FACTOR)
    model.add(b == 5 * cp_utils.SCALE_FACTOR)
    cp_utils.s_multiply(model, product, a, b)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.value(product) == 10 * cp_utils.SCALE_FACTOR


def test_divide_pos() -> None:
    model = cp_model.CpModel()
    a = model.new_int_var_from_domain(cp_utils.std_domain(), "a")
    b = model.new_int_var_from_domain(cp_utils.std_domain().intersection_with(cp_utils.nonzero_domain()), "b")
    quotient = model.new_int_var_from_domain(cp_utils.std_domain(), "quotient")
    model.add(a == 10 * cp_utils.SCALE_FACTOR)
    model.add(b == 5 * cp_utils.SCALE_FACTOR)
    cp_utils.s_divide(model, quotient, a, b)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.value(quotient) == 2 * cp_utils.SCALE_FACTOR


def test_divide_neg() -> None:
    model = cp_model.CpModel()
    a = model.new_int_var_from_domain(cp_utils.std_domain(), "a")
    b = model.new_int_var_from_domain(cp_utils.std_domain().intersection_with(cp_utils.nonzero_domain()), "b")
    quotient = model.new_int_var_from_domain(cp_utils.std_domain(), "quotient")
    model.add(a == 10 * cp_utils.SCALE_FACTOR)
    model.add(b == -5 * cp_utils.SCALE_FACTOR)
    cp_utils.s_divide(model, quotient, a, b)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.value(quotient) == -2 * cp_utils.SCALE_FACTOR


def test_sqrt() -> None:
    model = cp_model.CpModel()
    a = model.new_int_var_from_domain(cp_utils.std_domain(), "a")
    target = model.new_int_var_from_domain(cp_utils.std_domain(), "target")
    model.add(a == 25 * cp_utils.SCALE_FACTOR)
    cp_utils.s_sqrt(model, target, a)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    assert status == cp_model.OPTIMAL
    assert solver.value(target) == 5 * cp_utils.SCALE_FACTOR
