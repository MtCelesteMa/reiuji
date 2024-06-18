"""Tests for the `reiuji.core.utils.registered_model` module."""

import pydantic
import pytest
import registered_model_testutils as rt


@pytest.fixture
def parts_dict() -> list[dict]:
    return [
        {"reg_key": "test.part_a", "name": "a", "conductivity": 1.0},
        {"reg_key": "test.part_b", "name": "b", "cooling": 10},
        {"reg_key": "test.part_c", "name": "c", "cooling": 20, "flag": True},
    ]


@pytest.fixture
def parts() -> list[rt.BasePart]:
    return [
        rt.PartA(name="a", conductivity=1.0),
        rt.PartB(name="b", cooling=10),
        rt.PartC(name="c", cooling=20, flag=True),
    ]


@pytest.fixture
def rules_dict() -> list[dict]:
    return [
        {"reg_key": "test.rule_a", "amount": 1, "flag_a": True},
        {"reg_key": "test.rule_b", "amount": 2, "flag_b": True},
    ]


@pytest.fixture
def rules() -> list[rt.BaseRule]:
    return [
        rt.RuleA(amount=1, flag_a=True),
        rt.RuleB(amount=2, flag_b=True),
    ]


def test_registry() -> None:
    assert set(rt.BasePart.registry) == {"test.part_a", "test.part_b", "test.part_c"}
    assert set(rt.BaseRule.registry) == {"test.rule_a", "test.rule_b"}


def test_keys() -> None:
    assert not hasattr(rt.BasePart, "reg_key")
    assert rt.PartA.reg_key == "test.part_a"
    assert rt.PartB.reg_key == "test.part_b"
    assert rt.PartC.reg_key == "test.part_c"
    assert not hasattr(rt.BaseRule, "reg_key")
    assert not hasattr(rt.Rule0, "reg_key")
    assert rt.RuleA.reg_key == "test.rule_a"
    assert rt.RuleB.reg_key == "test.rule_b"


def test_validate(
    parts_dict: list[dict],
    rules_dict: list[dict],
    parts: list[rt.BasePart],
    rules: list[rt.BaseRule],
) -> None:
    assert pydantic.TypeAdapter(list[rt.Part]).validate_python(parts_dict) == parts
    assert pydantic.TypeAdapter(list[rt.Rule]).validate_python(rules_dict) == rules


def test_serialize(
    parts_dict: list[dict],
    rules_dict: list[dict],
    parts: list[rt.BasePart],
    rules: list[rt.BaseRule],
) -> None:
    assert pydantic.TypeAdapter(list[rt.Part]).dump_python(parts) == parts_dict
    assert pydantic.TypeAdapter(list[rt.Rule]).dump_python(rules) == rules_dict


def test_cycle_a(parts_dict: list[dict], rules_dict: list[dict]) -> None:
    parts = pydantic.TypeAdapter(list[rt.Part]).validate_python(parts_dict)
    rules = pydantic.TypeAdapter(list[rt.Rule]).validate_python(rules_dict)
    assert pydantic.TypeAdapter(list[rt.Part]).dump_python(parts) == parts_dict
    assert pydantic.TypeAdapter(list[rt.Rule]).dump_python(rules) == rules_dict


def test_cycle_b(parts: list[rt.BasePart], rules: list[rt.BaseRule]) -> None:
    parts_dict = pydantic.TypeAdapter(list[rt.Part]).dump_python(parts)
    rules_dict = pydantic.TypeAdapter(list[rt.Rule]).dump_python(rules)
    assert pydantic.TypeAdapter(list[rt.Part]).validate_python(parts_dict) == parts
    assert pydantic.TypeAdapter(list[rt.Rule]).validate_python(rules_dict) == rules
