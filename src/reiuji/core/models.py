"""Data models for Reiuji."""

import pydantic


class MultiblockComponent(pydantic.BaseModel):
    name: str
    type: str
    short_name: str = "  "
    placement_rule: str = pydantic.Field(default="")

    @property
    def full_name(self) -> str:
        return f"{self.type}__{self.name}"
