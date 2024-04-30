"""Base class for Reiuji JSON writers."""

import json

import pydantic


class MCBlock(pydantic.BaseModel):
    name: str
    data: int = 0
    properties: dict[str, str] = pydantic.Field(default_factory=dict)


class JSONWriter:
    def to_dict(self) -> dict[tuple[int, int, int], MCBlock]:
        raise NotImplementedError

    def write(self, output: str) -> None:
        d = {f"{k[0]},{k[1]},{k[2]}": v.model_dump() for k, v in self.to_dict().items()}
        with open(output, "w") as f:
            json.dump(d, f)
