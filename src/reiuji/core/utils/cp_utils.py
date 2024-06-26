"""Utilities related to OR-Tools CP-SAT."""

import typing
import uuid
from abc import ABC, abstractmethod

from ortools.sat.python import cp_model

# Domain utilities


def large_domain() -> cp_model.Domain:
    """Returns a domain for 48-bit integers."""
    return cp_model.Domain(-(2**47), 2**47 - 1)


def std_domain() -> cp_model.Domain:
    """Returns a domain for 32-bit integers."""
    return cp_model.Domain(cp_model.INT32_MIN, cp_model.INT32_MAX)


def nonnegative_domain() -> cp_model.Domain:
    """Returns a domain for nonnegative integers."""
    return cp_model.Domain(0, cp_model.INT_MAX)


def nonzero_domain() -> cp_model.Domain:
    """Returns a domain for nonzero integers."""
    return cp_model.Domain.from_values([0]).complement()


# Scaled calculations

SCALE_FACTOR = 1000


def s_multiply(
    model: cp_model.CpModel,
    target: cp_model.IntVar,
    a: cp_model.IntVar | int,
    b: cp_model.IntVar | int,
    *,
    scale_factor: int = SCALE_FACTOR,
    domain: cp_model.Domain | None = None,
) -> None:
    """Multiplies two scaled integers or integer variables and returns the scaled product.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the scaled product.
        a (cp_model.IntVar | int): The first integer or integer variable.
        b (cp_model.IntVar | int): The second integer or integer variable.
        scale_factor (int): The scaling factor. Defaults to SCALE_FACTOR.
        domain (cp_model.Domain | None): The domain of the raw product. Defaults to std_domain().
    """
    op_id = uuid.uuid4()
    domain = domain if isinstance(domain, cp_model.Domain) else std_domain()
    raw_prod = model.new_int_var_from_domain(domain, f"{op_id}_raw_prod")
    model.add_multiplication_equality(raw_prod, [a, b])
    model.add_division_equality(target, raw_prod, scale_factor)


def s_divide(
    model: cp_model.CpModel,
    target: cp_model.IntVar,
    a: cp_model.IntVar | int,
    b: cp_model.IntVar | int,
    *,
    scale_factor: int = SCALE_FACTOR,
    domain: cp_model.Domain | None = None,
) -> None:
    """Divides the scaled numerator by the given scaled divisor and returns the scaled quotient.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the quotient.
        a (cp_model.IntVar | int): The numerator variable or constant.
        b (cp_model.IntVar | int): The divisor variable or constant. Its domain must not contain 0.
        scale_factor (int): The scaling factor. Defaults to SCALE_FACTOR.
        domain (cp_model.Domain | None): The domain of the scaled numerator. Defaults to std_domain().
    """
    op_id = uuid.uuid4()
    domain = domain if isinstance(domain, cp_model.Domain) else std_domain()
    scaled_numerator = model.new_int_var_from_domain(
        domain, f"{op_id}_scaled_numerator"
    )
    model.add_multiplication_equality(scaled_numerator, [a, scale_factor])
    model.add_division_equality(target, scaled_numerator, b)


def s_sqrt(
    model: cp_model.CpModel,
    target: cp_model.IntVar,
    a: cp_model.IntVar,
    *,
    scale_factor: int = SCALE_FACTOR,
    domain: cp_model.Domain | None = None,
    iter: int = 10,
) -> None:
    """Calculates the square root of a given integer using Heron's method.

    Args:
        model (cp_model.CpModel): The constraint programming model.
        target (cp_model.IntVar): The variable to store the square root result.
        a (cp_model.IntVar): The input integer to calculate the square root of.
        scale_factor (int, optional): The scaling factor. Defaults to SCALE_FACTOR.
        domain (cp_model.Domain | None): The domain of the intermediate guesses. Defaults to std_domain().
        iter (int, optional): The number of iterations to perform. Defaults to 10.
    """
    op_id = uuid.uuid4()
    domain = domain if isinstance(domain, cp_model.Domain) else std_domain()
    guess_domain = domain.intersection_with(nonzero_domain())
    guess = model.new_int_var_from_domain(guess_domain, f"{op_id}_guess_0")
    model.add(guess == a)
    for i in range(iter):
        q = model.new_int_var_from_domain(domain, f"{op_id}_q_{i}")
        s = model.new_int_var_from_domain(domain, f"{op_id}_s_{i}")
        s_divide(model, q, a, guess, scale_factor=scale_factor, domain=domain)
        model.add(s == guess + q)

        new_guess = model.new_int_var_from_domain(
            guess_domain, f"{op_id}_guess_{i + 1}"
        )
        model.add_division_equality(new_guess, s, 2)
        guess = new_guess
    model.add_abs_equality(target, guess)


# Other


class BaseCPClass[BT, CT](ABC):
    @classmethod
    @abstractmethod
    def init(cls, model: cp_model.CpModel, config: CT) -> typing.Self: ...

    @abstractmethod
    def value(self, solver: cp_model.CpSolver, config: CT) -> BT: ...
