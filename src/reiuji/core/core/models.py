"""Core data models."""

import pydantic


class MCBlock(pydantic.BaseModel):
    name: str
    data: int = pydantic.Field(default=0)
    properties: dict[str, str] | None = pydantic.Field(default=None)
