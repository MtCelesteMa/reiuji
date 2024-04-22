"""Scaled multiplication and division functions for Reiuji."""

import uuid

from ortools.sat.python import cp_model


SCALE_FACTOR = 1000


def multiply(model: cp_model.CpModel, target: cp_model.IntVar, a: cp_model.IntVar | int, b: cp_model.IntVar | int) -> None:
    """Multiplies two integers or integer variables and returns the scaled product.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the scaled product.
        a (cp_model.IntVar | int): The first integer or integer variable.
        b (cp_model.IntVar | int): The second integer or integer variable.
    """
    op_id = uuid.uuid4()
    raw_prod = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, f"{op_id}_raw_prod")
    model.AddMultiplicationEquality(raw_prod, [a, b])
    model.AddDivisionEquality(target, raw_prod, SCALE_FACTOR)


def divide(model: cp_model.CpModel, target: cp_model.IntVar, a: cp_model.IntVar | int, b: cp_model.IntVar | int) -> None:
    """Divides the scaled numerator by the given divisor and returns the quotient.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the quotient.
        a (cp_model.IntVar | int): The numerator variable or constant.
        b (cp_model.IntVar | int): The divisor variable or constant.
    """
    op_id = uuid.uuid4()
    scaled_numerator = model.NewIntVar(0, cp_model.INT32_MAX, f"{op_id}_scaled_numerator")
    model.AddMultiplicationEquality(scaled_numerator, [a, SCALE_FACTOR])
    model.AddDivisionEquality(target, scaled_numerator, b)


def sqrt(model: cp_model.CpModel, target: cp_model.IntVar, a: cp_model.IntVar | int) -> None:
    """Calculates the square root of the scaled integer and returns the result.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the square root.
        a (cp_model.IntVar | int): The integer or integer variable.
    """
    op_id = uuid.uuid4()
    sqrt = model.NewIntVar(0, cp_model.INT32_MAX, f"{op_id}_sqrt")
    square_ = model.NewIntVar(0, cp_model.INT32_MAX, f"{op_id}_square_")
    model.AddMultiplicationEquality(square_, [target, target])
    square = model.NewIntVar(0, cp_model.INT32_MAX, f"{op_id}_square")
    model.AddDivisionEquality(square, square_, SCALE_FACTOR)
    error = model.NewIntVar(0, cp_model.INT32_MAX, f"{op_id}_error")
    model.AddAbsEquality(error, a - square)
    model.Add(error <= 10)
