"""Core multiblock part classes."""

import typing

import pydantic
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import PlainValidator

from .. import utils
from . import placement_rules


class BasePart(utils.registered_model.RegisteredModel, reg_key="core.base"):
    name: str
    type: str
    placement_rule: placement_rules.PlacementRule | None = pydantic.Field(default=None)


Part = typing.Annotated[
    BasePart,
    PlainValidator(utils.registered_model.model_validate(BasePart)),
    PlainSerializer(utils.registered_model.model_dump(BasePart)),
]


class Air(BasePart, reg_key="core.air"):
    name: str = pydantic.Field(default="air")
    type: str = pydantic.Field(default="")


class Casing(BasePart, reg_key="core.casing"):
    name: str = pydantic.Field(default="casing")
    type: str = pydantic.Field(default="")
