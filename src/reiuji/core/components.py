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

    short_name: str = pydantic.Field(default="  ", min_length=2, max_length=2)
    rich_formatting: str | None = None
    @property
    def rich_short_name(self) -> str:
        if isinstance(self.rich_formatting, str):
            return f"[{self.rich_formatting}]{self.short_name}[/{self.rich_formatting}]"
        return self.short_name

    @property
    def full_name(self) -> str:
        return f"{self.type}:{self.name}"
    
    block: dict[str, MCBlock] = pydantic.Field(default_factory=dict)
