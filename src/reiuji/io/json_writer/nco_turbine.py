"""JSON writer for NuclearCraft: Overhauled turbines."""

from ... import designer
from .base import MCBlock, JSONWriter

import typing


CASING = MCBlock(name="nuclearcraft:turbine_casing")
GLASS = MCBlock(name="nuclearcraft:turbine_glass")
DYNAMOS = {
    "__bearing": MCBlock(name="nuclearcraft:turbine_rotor_bearing"),
    "magnesium__coil": MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=0),
    "beryllium__coil": MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=1),
    "aluminum__coil": MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=2),
    "gold__coil": MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=3),
    "copper__coil": MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=4),
    "silver__coil": MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=5)
}
SHAFT_X = MCBlock(name="nuclearcraft:turbine_rotor_shaft", data=1)
SHAFT_Z = MCBlock(name="nuclearcraft:turbine_rotor_shaft", data=2)
ROTORS_X = {
    "steel__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=1),
    "extreme__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=1),
    "sic_sic_cmc__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=1),
    "super__blade": MCBlock(name="qmd:turbine_blade_super_alloy", data=1),
    "__stator": MCBlock(name="nuclearcraft:turbine_rotor_stator", data=1)
}
ROTORS_Z = {
    "steel__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=3),
    "extreme__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=3),
    "sic_sic_cmc__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=3),
    "super__blade": MCBlock(name="qmd:turbine_blade_super_alloy", data=3),
    "__stator": MCBlock(name="nuclearcraft:turbine_rotor_stator", data=3)
}
ROTORS_Y = {
    "steel__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=2),
    "extreme__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=2),
    "sic_sic_cmc__blade": MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=2),
    "super__blade": MCBlock(name="qmd:turbine_blade_super_alloy", data=2),
    "__stator": MCBlock(name="nuclearcraft:turbine_rotor_stator", data=2)
}


class NCOTurbineJSONWriter(JSONWriter):
    def __init__(
            self,
            dynamo_seq: designer.core.multi_sequence.MultiSequence[designer.core.models.MultiblockComponent],
            rotor_seq: designer.core.multi_sequence.MultiSequence[designer.core.models.MultiblockComponent],
            shaft_width: int = 1,
            *,
            facing: typing.Literal["+x", "-x", "+z", "-z"],
            transparent: bool = True
    ) -> None:
        self.dynamo_seq = dynamo_seq
        self.rotor_seq = rotor_seq
        self.shaft_width = shaft_width
        self.facing = facing
        self.transparent = transparent
    
    def to_dict(self) -> dict[tuple[int, int, int], MCBlock]:
        d = {}
        if self.dynamo_seq.shape[0] % 2:
            mid = (self.dynamo_seq.shape[0] - 1) // 2
            r_left = (self.shaft_width - 1) // 2
            r_right = (self.shaft_width - 1) // 2
        else:
            mid = self.dynamo_seq.shape[0] // 2
            r_left = self.shaft_width // 2 - 1
            r_right = self.shaft_width // 2
        if self.facing in {"+x", "-x"}:
            x, y, z = self.rotor_seq.shape[0] + 2, self.dynamo_seq.shape[0], self.dynamo_seq.shape[1]
            for x_ in range(x):
                for z_ in range(z):
                    for y_ in range(y):
                        if x_ == 0 or x_ == x - 1:
                            if self.dynamo_seq[z_, y_].full_name in {"__casing", "__air"}:
                                d[x_, y_, z_] = CASING
                            else:
                                d[x_, y_, z_] = DYNAMOS[self.dynamo_seq[z_, y_].full_name]
                        else:
                            if (z_ == 0 or z_ == z - 1) and (y_ == 0 or y_ == y - 1):
                                d[x_, y_, z_] = CASING
                            elif (z_ == 0 or z_ == z - 1) or (y_ == 0 or y_ == y - 1):
                                d[x_, y_, z_] = GLASS if (self.transparent and y_ != 0) else CASING
                            elif mid - r_left <= y_ <= mid + r_right and mid - r_left <= z_ <= mid + r_right:
                                d[x_, y_, z_] = SHAFT_X
                            elif mid - r_left <= y_ <= mid + r_right:
                                d[x_, y_, z_] = ROTORS_Z[self.rotor_seq[(x_ - 1) if self.facing == "+x" else (x - x_ - 2)].full_name]
                            elif mid - r_left <= z_ <= mid + r_right:
                                d[x_, y_, z_] = ROTORS_Y[self.rotor_seq[(x_ - 1) if self.facing == "+x" else (x - x_ - 2)].full_name]
        else:
            x, y, z = self.dynamo_seq.shape[1], self.dynamo_seq.shape[0], self.rotor_seq.shape[0] + 2
            for z_ in range(z):
                for x_ in range(x):
                    for y_ in range(y):
                        if z_ == 0 or z_ == z - 1:
                            if self.dynamo_seq[y_, x_].full_name in {"__casing", "__air"}:
                                d[x_, y_, z_] = CASING
                            else:
                                d[x_, y_, z_] = DYNAMOS[self.dynamo_seq[y_, x_].full_name]
                        else:
                            if (y_ == 0 or y_ == y - 1) and (x_ == 0 or x_ == x - 1):
                                d[x_, y_, z_] = CASING
                            elif (y_ == 0 or y_ == y - 1) or (x_ == 0 or x_ == x - 1):
                                d[x_, y_, z_] = GLASS if (self.transparent and y_ != 0) else CASING
                            elif mid - r_left <= x_ <= mid + r_right and mid - r_left <= y_ <= mid + r_right:
                                d[x_, y_, z_] = SHAFT_Z
                            elif mid - r_left <= x_ <= mid + r_right:
                                d[x_, y_, z_] = ROTORS_Y[self.rotor_seq[(z_ - 1) if self.facing == "+z" else (z - z_ - 2)].full_name]
                            elif mid - r_left <= y_ <= mid + r_right:
                                d[x_, y_, z_] = ROTORS_X[self.rotor_seq[(z_ - 1) if self.facing == "+z" else (z - z_ - 2)].full_name]
        return d
