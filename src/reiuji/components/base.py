"""Base classes for components."""

import typing

import pydantic


class DisplayInfo(pydantic.BaseModel):
    short_name: str = pydantic.Field(default="  ", min_length=2, max_length=2)
    full_name: str = ""
    rich_formatting: str | None = None

    @property
    def rich_short_name(self) -> str:
        if isinstance(self.rich_formatting, str):
            return f"[{self.rich_formatting}]{self.short_name}[/{self.rich_formatting}]"
        return self.short_name

    @property
    def rich_full_name(self) -> str:
        if isinstance(self.rich_formatting, str):
            return f"[{self.rich_formatting}]{self.full_name}[/{self.rich_formatting}]"
        return self.full_name
    

class MCBlock(pydantic.BaseModel):
    name: str
    data: int = 0
    is_tile_entity: bool = True
    properties: dict[str, str] = pydantic.Field(default_factory=dict)


class BlockInfoTransparency(pydantic.BaseModel):
    opaque: MCBlock
    transparent: MCBlock


class BlockInfoOrientation(pydantic.BaseModel):
    x: MCBlock
    y: MCBlock
    z: MCBlock


class BaseComponent(pydantic.BaseModel):
    name: str
    type: str

    @property
    def full_name(self) -> str:
        return f"{self.type}:{self.name}"

    placement_rule: str = ""
    display: DisplayInfo = pydantic.Field(default_factory=DisplayInfo)
