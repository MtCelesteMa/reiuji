"""Utilities for tests for the `reiuji.core.utils.registered_model` module."""

import typing

from pydantic.functional_validators import PlainValidator
from pydantic.functional_serializers import PlainSerializer

from reiuji.core.utils import registered_model


class BasePart(registered_model.RegisteredModel):
    name: str


class PartA(BasePart, reg_key="test.part_a"):
    name: str = "a"
    conductivity: float


class PartB(BasePart, reg_key="test.part_b"):
    name: str = "b"
    cooling: int


class PartC(PartB, reg_key="test.part_c"):
    name: str = "c"
    flag: bool


Part = typing.Annotated[
    BasePart,
    PlainValidator(registered_model.model_validate(BasePart)),
    PlainSerializer(registered_model.model_dump(BasePart)),
]

class BaseRule(registered_model.RegisteredModel):
    pass


class Rule0(BaseRule):
    amount: int


class RuleA(Rule0, reg_key="test.rule_a"):
    flag_a: bool


class RuleB(Rule0, reg_key="test.rule_b"):
    flag_b: bool


Rule = typing.Annotated[
    BaseRule,
    PlainValidator(registered_model.model_validate(BaseRule)),
    PlainSerializer(registered_model.model_dump(BaseRule)),
]
