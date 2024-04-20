"""Data models for Reiuji."""

import pydantic


class MultiblockComponent(pydantic.BaseModel):
    name: str
    type: str
    placement_rule: str = pydantic.Field(default="")
