"""Scaled multiplication and division functions for Reiuji."""

import uuid

from ortools.sat.python import cp_model


SCALE_FACTOR = 1000


def multiply(
        model: cp_model.CpModel,
        target: cp_model.IntVar,
        a: cp_model.IntVar | int,
        b: cp_model.IntVar | int,
        *,
        scale_factor: int = SCALE_FACTOR,
        min_value: int = cp_model.INT32_MIN,
        max_value: int = cp_model.INT32_MAX
) -> None:
    """Multiplies two integers or integer variables and returns the scaled product.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the scaled product.
        a (cp_model.IntVar | int): The first integer or integer variable.
        b (cp_model.IntVar | int): The second integer or integer variable.
    """
    op_id = uuid.uuid4()
    raw_prod = model.NewIntVar(min_value, max_value, f"{op_id}_raw_prod")
    model.AddMultiplicationEquality(raw_prod, [a, b])
    model.AddDivisionEquality(target, raw_prod, scale_factor)


def divide(
        model: cp_model.CpModel,
        target: cp_model.IntVar,
        a: cp_model.IntVar | int,
        b: cp_model.IntVar | int,
        *,
        scale_factor: int = SCALE_FACTOR,
        min_value: int = cp_model.INT32_MIN,
        max_value: int = cp_model.INT32_MAX
) -> None:
    """Divides the scaled numerator by the given divisor and returns the quotient.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the quotient.
        a (cp_model.IntVar | int): The numerator variable or constant.
        b (cp_model.IntVar | int): The divisor variable or constant.
    """
    op_id = uuid.uuid4()
    scaled_numerator = model.NewIntVar(min_value, max_value, f"{op_id}_scaled_numerator")
    model.AddMultiplicationEquality(scaled_numerator, [a, scale_factor])
    is_positive = model.NewBoolVar(f"{op_id}_is_positive")
    model.Add(b > 0).OnlyEnforceIf(is_positive)
    model.Add(b < 0).OnlyEnforceIf(is_positive.Not())
    b_pos = model.NewIntVar(1, max_value, f"{op_id}_b_pos")
    model.Add(b_pos == b).OnlyEnforceIf(is_positive)
    b_neg = model.NewIntVar(min_value, -1, f"{op_id}_b_neg")
    model.Add(b_neg == b).OnlyEnforceIf(is_positive.Not())
    target_pos = model.NewIntVar(min_value, max_value, f"{op_id}_target_pos")
    target_neg = model.NewIntVar(min_value, max_value, f"{op_id}_target_neg")
    model.AddDivisionEquality(target_pos, scaled_numerator, b_pos)
    model.AddDivisionEquality(target_neg, scaled_numerator, b_neg)
    model.Add(target == target_pos).OnlyEnforceIf(is_positive)
    model.Add(target == target_neg).OnlyEnforceIf(is_positive.Not())


def sqrt(
        model: cp_model.CpModel,
        target: cp_model.IntVar,
        a: cp_model.IntVar,
        *,
        scale_factor: int = SCALE_FACTOR,
        min_value: int = cp_model.INT32_MIN,
        max_value: int = cp_model.INT32_MAX,
        iter: int = 10
) -> None:
    """Calculates the square root of a given integer using Heron's method.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the square root result.
        a (cp_model.IntVar): The input integer to calculate the square root of.
        iter (int, optional): The number of iterations to perform. Defaults to 5.
    """
    op_id = uuid.uuid4()
    guess = a
    for i in range(iter):
        q = model.NewIntVar(min_value, max_value, f"{op_id}_q_{i}")
        divide(model, q, a, guess, scale_factor=scale_factor, min_value=min_value, max_value=max_value)
        s = model.NewIntVar(min_value, max_value, f"{op_id}_s_{i}")
        model.Add(s == guess + q)

        new_guess = model.NewIntVar(min_value, max_value, f"{op_id}_guess_{i + 1}")
        model.AddDivisionEquality(new_guess, s, 2)
        guess = new_guess
    
    model.AddAbsEquality(target, guess)
