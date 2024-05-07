"""MultiSequence serialization and deserialization functions."""

from .. import core
from .. import components

import typing

import pydantic


class SerializableMultiSequence(pydantic.BaseModel):
    shape: tuple[int, ...]
    seq: list[components.types.Component]

    @classmethod
    def from_multi_sequence(cls, seq: core.multi_sequence.MultiSequence[components.types.Component]) -> typing.Self:
        return cls(shape=seq.shape, seq=list(seq.seq))
    
    def to_multi_sequence(self) -> core.multi_sequence.MultiSequence[components.types.Component]:
        return core.multi_sequence.MultiSequence(shape=self.shape, seq=self.seq)
