"""Data models representing multiblock components."""

import pydantic


class MCBlock(pydantic.BaseModel):
    name: str
    data: int = 0
    is_tile_entity: bool = True
    properties: dict[str, str] = pydantic.Field(default_factory=dict)


class Component(pydantic.BaseModel):
    name: str
    type: str
    placement_rule: str = pydantic.Field(default="")

    short_name: str = pydantic.Field(default="  ")
    @property
    def full_name(self) -> str:
        return f"{self.name}__{self.type}"
    
    block: dict[str, MCBlock] = pydantic.Field(default_factory=dict)
