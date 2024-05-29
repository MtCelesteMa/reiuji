"""Namespace registry for data classes."""

import importlib
import typing

import pydantic


REGISTRY: "Registry" = {}

Registry = dict[str, "Namespace"]


class ObjInfo(pydantic.BaseModel):
    package: str
    module: str
    name: str

    def import_(self) -> typing.Any:
        return getattr(importlib.import_module(self.module, self.package), self.name)


class PlacementRuleSpace(pydantic.BaseModel):
    factory: ObjInfo | None = pydantic.Field(default=None)
    data_model: ObjInfo | None = pydantic.Field(default=None)

    @classmethod
    def create(cls, space_name: str, namespace: str, **kwargs) -> typing.Self:
        if namespace not in REGISTRY:
            raise NameError(f"Namespace '{namespace}' does not exist.")
        if space_name in REGISTRY[namespace].placement_rules:
            raise ValueError(f"Placement rule '{space_name}' already exists in namespace '{namespace}'.")
        rule = cls(**kwargs)
        REGISTRY[namespace].placement_rules[space_name] = rule
        return rule


class MultiblockSpace(pydantic.BaseModel):
    multiblock: ObjInfo | None = pydantic.Field(default=None)
    designer: ObjInfo | None = pydantic.Field(default=None)
    part_types: dict[str, ObjInfo] = pydantic.Field(default_factory=dict)

    @classmethod
    def create(cls, space_name: str, namespace: str, **kwargs) -> typing.Self:
        if namespace not in REGISTRY:
            raise NameError(f"Namespace '{namespace}' does not exist.")
        if space_name in REGISTRY[namespace].multiblocks:
            raise ValueError(f"Multiblock '{space_name}' already exists in namespace '{namespace}'.")
        multiblock = cls(**kwargs)
        REGISTRY[namespace].multiblocks[space_name] = multiblock
        return multiblock


class Namespace(pydantic.BaseModel):
    rule_parser: ObjInfo | None = pydantic.Field(default=None)
    placement_rules: dict[str, PlacementRuleSpace] = pydantic.Field(default_factory=dict)
    multiblocks: dict[str, MultiblockSpace] = pydantic.Field(default_factory=dict)

    @classmethod
    def create(cls, name: str, **kwargs) -> typing.Self:
        if name in REGISTRY:
            raise ValueError(f"Namespace '{name}' already exists.")
        namespace = cls(**kwargs)
        REGISTRY[name] = namespace
        return namespace
