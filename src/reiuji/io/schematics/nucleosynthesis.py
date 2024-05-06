"""Schematic writer for QMD nucleosynthesis chambers."""

from ... import core
from . import base

import typing


class NucleosynthesisSchematicWriter(base.SchematicWriter):
    def __init__(
            self,
            seq: core.multi_sequence.MultiSequence[core.components.Component],
            *,
            facing: typing.Literal["x", "z"],
            transparent: bool = True
    ) -> None:
        self.seq = seq
        self.facing = facing
        self.transparent = transparent
    
    def to_structure(self) -> core.multi_sequence.MultiSequence[core.components.MCBlock]:
        x = self.seq.shape[0]
        z = self.seq.shape[1]
        y = self.seq.shape[2]
        
        structure = [core.components.MCBlock(name="minecraft:air", is_tile_entity=False)] * (y * z * x)
        for y_ in range(y):
            for z_ in range(z):
                for x_ in range(x):
                    idx = (y_ * z + z_) * x + x_
                    if self.seq[x_, z_, y_].type == "casing":
                        if (x_ == 0 or x_ == x - 1) + (z_ == 0 or z_ == z - 1) + (y_ == 0 or y_ == y - 1) >= 2:
                            structure[idx] = self.seq[x_, z_, y_].block[""]
                        else:
                            structure[idx] = self.seq[x_, z_, y_].block["glass"] if self.transparent and y_ != 0 else self.seq[x_, z_, y_].block[""]
                    elif self.seq[x_, z_, y_].type == "nozzle":
                        structure[idx] = self.seq[x_, z_, y_].block["x" if self.facing == "x" else "z"]
                    else:
                        structure[idx] = self.seq[x_, z_, y_].block[""]
        return core.multi_sequence.MultiSequence(structure, (y, z, x))
