"""Registered models for Reiuji."""

import typing
from collections import abc
import importlib

import pydantic


class ClsInfo(pydantic.BaseModel):
    package: str
    module: str
    name: str

    def import_(self) -> typing.Any:
        return getattr(importlib.import_module(self.module, self.package), self.name)


class RegisteredModel(pydantic.BaseModel):
    reg_base: typing.ClassVar[type["RegisteredModel"]]
    registry: typing.ClassVar[dict[str, ClsInfo]]
    reg_key: typing.ClassVar[str]

    def __init_subclass__(cls, reg_key: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "registry"):
            cls.registry = {}
        if not hasattr(cls, "reg_base"):
            cls.reg_base = cls
        if isinstance(reg_key, str):
            cls.reg_key = reg_key
            if cls.reg_key in cls.reg_base.registry:
                raise ValueError(f"Registered model '{cls.reg_key}' already exists.")
            if "." in cls.__module__:
                package, module = cls.__module__.split(".", 1)
            else:
                package = cls.__module__
                module = ""
            cls.reg_base.registry[cls.reg_key] = ClsInfo(
                package=package, module=f".{module}", name=cls.__name__
            )


def model_validate[T: RegisteredModel](
    base_model: type[T],
) -> abc.Callable[[typing.Any], T]:
    def validator(obj: typing.Any) -> T:
        reg_key = getattr(obj, "reg_key") if hasattr(obj, "reg_key") else obj["reg_key"]
        if reg_key not in base_model.registry:
            raise ValueError(f"Registered model '{reg_key}' does not exist.")
        return base_model.registry[reg_key].import_().model_validate(obj)

    return validator


def model_dump[T: RegisteredModel](base_model: type[T]) -> abc.Callable[[T], dict]:
    def dump(obj: T) -> dict:
        if obj.reg_key not in base_model.registry:
            raise ValueError(f"Registered model '{obj.reg_key}' does not exist.")
        d = base_model.registry[obj.reg_key].import_().model_dump(obj)
        d["reg_key"] = obj.reg_key
        return d

    return dump
