"""Floating point numbers in OR-Tools."""

import uuid
import typing

from ortools.sat.python import cp_model


PERCISION = 3


class FloatVar:
    def __init__(self, man: cp_model.IntVar, exp: cp_model.IntVar) -> None:
        self.man = man
        self.exp = exp
    
    @classmethod
    def new(cls, model: cp_model.CpModel, name: str) -> typing.Self:
        return cls(model.NewIntVar(0, 10 ** (PERCISION * 2), f"{name}_man"), model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, f"{name}_exp"))
    
    def correct_overflow(self, model: cp_model.CpModel) -> typing.Self:
        op_id = uuid.uuid4()
        man = self.man
        exp = self.exp
        for i in range(PERCISION):
            overflow = model.NewBoolVar(f"{op_id}_overflow_{i}")
            a = model.NewIntVar(0, 10 ** PERCISION, f"{op_id}_a_{i}")
            model.AddDivisionEquality(a, man, 10 ** PERCISION)
            model.Add(a > 0).OnlyEnforceIf(overflow)
            model.Add(a == 0).OnlyEnforceIf(overflow.Not())

            b = model.NewIntVar(0, 10 ** PERCISION, f"{op_id}_b_{i}")
            model.AddDivisionEquality(b, man, 10)
            new_man = model.NewIntVar(0, 10 ** (PERCISION * 2), f"{op_id}_new_man{i}")
            model.Add(new_man == b).OnlyEnforceIf(overflow)
            model.Add(new_man == man).OnlyEnforceIf(overflow.Not())
            new_exp = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, f"{op_id}_new_exp_{i}")
            model.Add(exp + 1 == new_exp).OnlyEnforceIf(overflow)
            model.Add(exp == new_exp).OnlyEnforceIf(overflow.Not())

            man = new_man
            exp = new_exp
        return type(self)(new_man, new_exp)


def add(model: cp_model.CpModel, target: FloatVar, a: FloatVar, b: FloatVar) -> None:
    op_id = uuid.uuid4()
    sum_ = FloatVar.new(model, f"{op_id}_sum")
    model.Add(sum_.man == a.man + b.man)
    model.Add(sum_.exp == a.exp)
    sum_corrected = sum_.correct_overflow(model)
    model.Add(target.man == sum_corrected.man)
    model.Add(target.exp == sum_corrected.exp)
