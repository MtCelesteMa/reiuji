"""Scaled multiplication and division functions for Reiuji."""

import uuid

from ortools.sat.python import cp_model


SCALE_FACTOR = 1000


def multiply(model: cp_model.CpModel, a: cp_model.IntVar | int, b: cp_model.IntVar | int) -> cp_model.IntVar:
    """Multiplies two integers or integer variables and returns the scaled product.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        a (cp_model.IntVar | int): The first integer or integer variable.
        b (cp_model.IntVar | int): The second integer or integer variable.

    Returns:
        cp_model.IntVar: The scaled product of a and b.
    """
    op_id = uuid.uuid4()
    raw_prod = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, f"{op_id}_raw_prod")
    product = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, f"{op_id}_product")
    model.AddMultiplicationEquality(raw_prod, [a, b])
    model.AddDivisionEquality(product, raw_prod, SCALE_FACTOR)
    return product


def divide(model: cp_model.CpModel, a: cp_model.IntVar | int, b: cp_model.IntVar | int) -> cp_model.IntVar:
    """Divides the scaled numerator by the given divisor and returns the quotient.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        a (cp_model.IntVar | int): The numerator variable or constant.
        b (cp_model.IntVar | int): The divisor variable or constant.

    Returns:
        cp_model.IntVar: The quotient of the division.
    """
    op_id = uuid.uuid4()
    scaled_numerator = model.NewIntVar(1, cp_model.INT32_MAX, f"{op_id}_scaled_numerator")
    model.AddMultiplicationEquality(scaled_numerator, [a, SCALE_FACTOR])
    quotient = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, f"{op_id}_quotient")
    model.AddDivisionEquality(quotient, scaled_numerator, b)
    return quotient
