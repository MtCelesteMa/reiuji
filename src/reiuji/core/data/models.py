"""Data models for Reiuji."""

import typing

import pydantic
from pydantic.functional_validators import PlainValidator

from . import registry


class BasePlacementRule(pydantic.BaseModel):
    name: str

    def __init_subclass__(cls, name: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if isinstance(name, str):
            cls.name = name
            namespace, name = name.split(".", 1)
            if namespace not in registry.REGISTRY:
                registry.Namespace.create(namespace)
            if name not in registry.REGISTRY[namespace].placement_rules:
                registry.PlacementRuleSpace.create(name, namespace)
            if "." in cls.__module__:
                package, module = cls.__module__.split(".", 1)
            else:
                package = cls.__module__
                module = ""
            if not isinstance(registry.REGISTRY[namespace].placement_rules[name].data_model, type(None)):
                raise ValueError(f"Placement rule '{name}' already exists in namespace '{namespace}'.")
            registry.REGISTRY[namespace].placement_rules[name].data_model = registry.ObjInfo(package=package, module=f".{module}", name=cls.__name__)


class BasePartType(pydantic.BaseModel):
    name: str

    def __init_subclass__(cls, name: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if isinstance(name, str):
            cls.name = name
            namespace, multiblock, name = name.split(".", 2)
            if namespace not in registry.REGISTRY:
                registry.Namespace.create(namespace)
            if multiblock not in registry.REGISTRY[namespace].multiblocks:
                registry.MultiblockSpace.create(multiblock, namespace)
            if name in registry.REGISTRY[namespace].multiblocks[multiblock].part_types:
                raise ValueError(f"Part type '{name}' already exists in multiblock '{multiblock}' in namespace '{namespace}'.")
            if "." in cls.__module__:
                package, module = cls.__module__.split(".", 1)
            else:
                package = cls.__module__
                module = ""
            registry.REGISTRY[namespace].multiblocks[multiblock].part_types[name] = registry.ObjInfo(package=package, module=f".{module}", name=cls.__name__)


def validate_placement_rule(obj: typing.Any) -> BasePlacementRule:
    v_obj = BasePlacementRule.model_validate(obj)
    namespace, name = v_obj.name.split(".", 1)
    return registry.REGISTRY[namespace].placement_rules[name].data_model.import_().model_validate(obj)


def validate_part_type(obj: typing.Any) -> BasePartType:
    v_obj = BasePartType.model_validate(obj)
    namespace, multiblock, name = v_obj.name.split(".", 2)
    return registry.REGISTRY[namespace].multiblocks[multiblock].part_types[name].import_().model_validate(obj)


PlacementRule = typing.Annotated[BasePlacementRule, PlainValidator(validate_placement_rule)]
PartType = typing.Annotated[BasePartType, PlainValidator(validate_part_type)]
