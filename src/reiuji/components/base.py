"""Base classes for components."""

import typing

import pydantic


class DisplayInfo(pydantic.BaseModel):
    short_name: str = pydantic.Field(default="  ", min_length=2, max_length=2)
    full_name: str = ""
    
    bold: bool = False
    italic: bool = False
    color: tuple[int, int, int] | None = None
    bg_color: tuple[int, int, int] | None = None
    

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
