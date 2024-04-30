"""JSON Writer for QMD nucleosynthesis chambers."""

from ... import designer
from .base import MCBlock, JSONWriter

import typing


CASING = MCBlock(name="qmd:containment_casing")
GLASS = MCBlock(name="qmd:containment_glass")
NOZZLE_X = MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=0)
NOZZLE_Y = MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=1)
NOZZLE_Z = MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=2)
COMPONENTS = {
    "__beam": MCBlock(name="qmd:vacuum_chamber_beam"),
    "__glass": MCBlock(name="qmd:vacuum_chamber_plasma_glass"),
    "iron__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=0),
    "redstone__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=1),
    "quartz__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=2),
    "obsidian__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=3),
    "glowstone__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=4),
    "lapis__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=5),
    "gold__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=6),
    "diamond__heater": MCBlock(name="qmd:vacuum_chamber_heater", data=7)
}


class NucleosynthesisJSONWriter(JSONWriter):
    def __init__(
            self,
            seq: designer.core.multi_sequence.MultiSequence[designer.core.models.MultiblockComponent],
            *,
            facing: typing.Literal["+x", "-x", "+z", "-z"],
            transparent: bool = True
    ) -> None:
        self.seq = seq
        self.facing = facing
        self.transparent = transparent
    
    def to_dict(self) -> dict[tuple[int, int, int], MCBlock]:
        d = {}
        if self.facing in {"+x", "-x"}:
            x, y, z = self.seq.shape[0], self.seq.shape[2], self.seq.shape[1]
            for x_ in range(x):
                for z_ in range(z):
                    for y_ in range(y):
                        w = x_ if self.facing == "+x" else x - x_ - 1
                        if self.seq[w, z_, y_].type == "air":
                            continue
                        if self.seq[w, z_, y_].type == "casing":
                            if (x_ == 0 or x_ == x - 1) + (z_ == 0 or z_ == z - 1) + (y_ == 0 or y_ == y - 1) >= 2:
                                d[(x_, y_, z_)] = CASING
                            else:
                                d[(x_, y_, z_)] = GLASS if self.transparent and y_ != 0 else CASING
                        elif self.seq[w, z_, y_].type == "nozzle":
                            d[(x_, y_, z_)] = NOZZLE_X
                        else:
                            d[(x_, y_, z_)] = COMPONENTS[self.seq[w, z_, y_].full_name]
        else:
            x, y, z = self.seq.shape[1], self.seq.shape[2], self.seq.shape[0]
            for x_ in range(x):
                for z_ in range(z):
                    for y_ in range(y):
                        w = z_ if self.facing == "+z" else z - z_ - 1
                        if self.seq[w, x_, y_].type == "air":
                            continue
                        if self.seq[w, x_, y_].type == "casing":
                            if (x_ == 0 or x_ == x - 1) + (z_ == 0 or z_ == z - 1) + (y_ == 0 or y_ == y - 1) >= 2:
                                d[(x_, y_, z_)] = CASING
                            else:
                                d[(x_, y_, z_)] = GLASS if self.transparent and y_ != 0 else CASING
                        elif self.seq[w, x_, y_].type == "nozzle":
                            d[(x_, y_, z_)] = NOZZLE_Z
                        else:
                            d[(x_, y_, z_)] = COMPONENTS[self.seq[w, x_, y_].full_name]
        return d
