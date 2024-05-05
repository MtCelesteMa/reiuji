"""MultiSequence serialization and deserialization functions."""

from .. import core

import typing

import pydantic


class SerializableMultiSequence(pydantic.BaseModel):
    shape: tuple[int, ...]
    seq: list[dict[str, pydantic.JsonValue]]

    @classmethod
    def from_multi_sequence(cls, seq: core.multi_sequence.MultiSequence[core.components.Component]) -> typing.Self:
        seq_ = []
        for comp in seq:
            comp_ser = comp.model_dump()
            comp_ser.update({"__type__": comp.__class__.__name__})
            seq_.append(comp_ser)
        return cls(shape=seq.shape, seq=seq_)
    
    def to_multi_sequence(self) -> core.multi_sequence.MultiSequence[core.components.Component]:
        seq = []
        for comp_ser in self.seq:
            comp_cls_name = comp_ser.get("__type__", "Component")
            comp_cls = None
            for subclass in [core.components.Component] + core.components.Component.__subclasses__():
                if subclass.__name__.split(".")[-1] == comp_cls_name.split(".")[-1]:
                    comp_cls = subclass
                    break
            if isinstance(comp_cls, type(None)):
                raise ValueError(f"Component class {comp_cls_name} not found.")
            comp_ser.pop("__type__", "")
            comp = comp_cls.model_validate(comp_ser)
            seq.append(comp)
        return core.multi_sequence.MultiSequence(shape=self.shape, seq=seq)
