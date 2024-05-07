"""Schematic writer for QMD accelerators."""

from ... import core
from ... import components
from . import base


class AcceleratorSchematicWriter(base.SchematicWriter):
    def __init__(
            self,
            seq: core.multi_sequence.MultiSequence[components.types.Component],
            *,
            transparent: bool = True
    ) -> None:
        self.seq = seq
        self.transparent = transparent
    
    def to_structure(self) -> core.multi_sequence.MultiSequence[components.base.MCBlock]:
        z = self.seq.shape[0]
        x = self.seq.shape[1]
        y = self.seq.shape[2]
        
        structure = [components.base.MCBlock(name="minecraft:air", is_tile_entity=False)] * (y * z * x)
        for y_ in range(y):
            for z_ in range(z):
                for x_ in range(x):
                    idx = (y_ * z + z_) * x + x_
                    comp = self.seq[z_, x_, y_]
                    if isinstance(comp, components.types.Casing):
                        structure[idx] = comp.block.transparent if self.transparent and y_ != 0 else comp.block.opaque
                    else:
                        structure[idx] = comp.block
        return core.multi_sequence.MultiSequence(structure, (y, z, x))
