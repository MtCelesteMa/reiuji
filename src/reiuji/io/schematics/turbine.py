"""Schematic writer for NuclearCraft: Overhauled turbines."""

from ... import core
from ... import components
from . import base

import typing


class TurbineSchematicWriter(base.SchematicWriter):
    def __init__(
            self,
            dynamo_seq: core.multi_sequence.MultiSequence[components.types.Component],
            rotor_seq: core.multi_sequence.MultiSequence[components.types.Component],
            shaft_width: int,
            *,
            facing: typing.Literal["x", "z"],
            transparent: bool = True,
            casing: components.base.MCBlock | None = None,
            glass: components.base.MCBlock | None = None,
            air: components.base.MCBlock | None = None,
            shaft_x: components.base.MCBlock | None = None,
            shaft_z: components.base.MCBlock | None = None,
    ) -> None:
        self.dynamo_seq = dynamo_seq
        self.rotor_seq = rotor_seq
        self.shaft_width = shaft_width
        self.facing = facing
        self.transparent = transparent

        self.casing = casing if not isinstance(casing, type(None)) else components.base.MCBlock(name="nuclearcraft:turbine_casing")
        self.glass = glass if not isinstance(glass, type(None)) else components.base.MCBlock(name="nuclearcraft:turbine_glass")
        self.air = air if not isinstance(air, type(None)) else components.base.MCBlock(name="minecraft:air", is_tile_entity=False)
        self.shaft_x = shaft_x if not isinstance(shaft_x, type(None)) else components.base.MCBlock(name="nuclearcraft:turbine_rotor_shaft", data=1)
        self.shaft_z = shaft_z if not isinstance(shaft_z, type(None)) else components.base.MCBlock(name="nuclearcraft:turbine_rotor_shaft", data=3)
    
    def to_structure(self) -> core.multi_sequence.MultiSequence[components.base.MCBlock]:
        z = self.rotor_seq.shape[0] + 2
        x = y = self.dynamo_seq.shape[0]
        if self.dynamo_seq.shape[0] % 2:
            mid = (self.dynamo_seq.shape[0] - 1) // 2
            r_left = (self.shaft_width - 1) // 2
            r_right = (self.shaft_width - 1) // 2
        else:
            mid = self.dynamo_seq.shape[0] // 2
            r_left = self.shaft_width // 2 - 1
            r_right = self.shaft_width // 2
        
        structure = [self.air] * (y * z * x)
        for y_ in range(y):
            for z_ in range(z):
                for x_ in range(x):
                    idx = (y_ * z + z_) * x + x_
                    if z_ == 0 or z_ == z - 1:
                        comp = self.dynamo_seq[y_, x_]
                        if isinstance(comp, components.types.Casing):
                            structure[idx] = comp.block.opaque
                        else:
                            structure[idx] = comp.block
                    else:
                        if (x_ == 0 or x_ == x - 1) and (y_ == 0 or y_ == y - 1):
                            structure[idx] = self.casing
                        elif (x_ == 0 or x_ == x - 1) or (y_ == 0 or y_ == y - 1):
                            structure[idx] = self.glass if (self.transparent and y_ != 0) else self.casing
                        elif mid - r_left <= y_ <= mid + r_right and mid - r_left <= x_ <= mid + r_right:
                            structure[idx] = self.shaft_x if self.facing == "x" else self.shaft_z
                        elif mid - r_left <= y_ <= mid + r_right:
                            structure[idx] = self.rotor_seq[z_ - 1].block.x if self.facing == "z" else self.rotor_seq[z_ - 1].block.z
                        elif mid - r_left <= x_ <= mid + r_right:
                            structure[idx] = self.rotor_seq[z_ - 1].block.y
        return core.multi_sequence.MultiSequence(structure, (y, z, x))
