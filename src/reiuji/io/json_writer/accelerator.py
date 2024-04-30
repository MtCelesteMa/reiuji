"""JSON writer for QMD accelerators."""

from ... import designer
from .base import MCBlock, JSONWriter

import typing


CASING = MCBlock(name="qmd:accelerator_casing")
GLASS = MCBlock(name="qmd:accelerator_glass")
COMPONENTS = {
    "__beam": MCBlock(name="qmd:accelerator_beam"),
    "__yoke": MCBlock(name="qmd:accelerator_yoke"),
    "copper__cavity": MCBlock(name="qmd:accelerator_cavity", data=0),
    "magnesium_diboride__cavity": MCBlock(name="qmd:accelerator_cavity", data=1),
    "niobium_tin__cavity": MCBlock(name="qmd:accelerator_cavity", data=2),
    "niobium_titanium__cavity": MCBlock(name="qmd:accelerator_cavity", data=3),
    "bscco__cavity": MCBlock(name="qmd:accelerator_cavity", data=4),
    "copper__magnet": MCBlock(name="qmd:accelerator_magnet", data=0),
    "magnesium_diboride__magnet": MCBlock(name="qmd:accelerator_magnet", data=1),
    "niobium_tin__magnet": MCBlock(name="qmd:accelerator_magnet", data=2),
    "niobium_titanium__magnet": MCBlock(name="qmd:accelerator_magnet", data=3),
    "bscco__magnet": MCBlock(name="qmd:accelerator_magnet", data=4),
    "water__cooler": MCBlock(name="qmd:accelerator_cooler1", data=0),
    "iron__cooler": MCBlock(name="qmd:accelerator_cooler1", data=1),
    "redstone__cooler": MCBlock(name="qmd:accelerator_cooler1", data=2),
    "quartz__cooler": MCBlock(name="qmd:accelerator_cooler1", data=3),
    "obsidian__cooler": MCBlock(name="qmd:accelerator_cooler1", data=4),
    "nether_brick__cooler": MCBlock(name="qmd:accelerator_cooler1", data=5),
    "glowstone__cooler": MCBlock(name="qmd:accelerator_cooler1", data=6),
    "lapis__cooler": MCBlock(name="qmd:accelerator_cooler1", data=7),
    "gold__cooler": MCBlock(name="qmd:accelerator_cooler1", data=8),
    "prismarine__cooler": MCBlock(name="qmd:accelerator_cooler1", data=9),
    "slime__cooler": MCBlock(name="qmd:accelerator_cooler1", data=10),
    "end_stone__cooler": MCBlock(name="qmd:accelerator_cooler1", data=11),
    "purpur__cooler": MCBlock(name="qmd:accelerator_cooler1", data=12),
    "diamond__cooler": MCBlock(name="qmd:accelerator_cooler1", data=13),
    "emerald__cooler": MCBlock(name="qmd:accelerator_cooler1", data=14),
    "copper__cooler": MCBlock(name="qmd:accelerator_cooler1", data=15),
    "tin__cooler": MCBlock(name="qmd:accelerator_cooler2", data=0),
    "lead__cooler": MCBlock(name="qmd:accelerator_cooler2", data=1),
    "boron__cooler": MCBlock(name="qmd:accelerator_cooler2", data=2),
    "lithium__cooler": MCBlock(name="qmd:accelerator_cooler2", data=3),
    "magnesium__cooler": MCBlock(name="qmd:accelerator_cooler2", data=4),
    "manganese__cooler": MCBlock(name="qmd:accelerator_cooler2", data=5),
    "aluminum__cooler": MCBlock(name="qmd:accelerator_cooler2", data=6),
    "silver__cooler": MCBlock(name="qmd:accelerator_cooler2", data=7),
    "fluorite__cooler": MCBlock(name="qmd:accelerator_cooler2", data=8),
    "villiaumite__cooler": MCBlock(name="qmd:accelerator_cooler2", data=9),
    "carobbiite__cooler": MCBlock(name="qmd:accelerator_cooler2", data=10),
    "arsenic__cooler": MCBlock(name="qmd:accelerator_cooler2", data=11),
    "nitrogen__cooler": MCBlock(name="qmd:accelerator_cooler2", data=12),
    "helium__cooler": MCBlock(name="qmd:accelerator_cooler2", data=13),
    "enderium__cooler": MCBlock(name="qmd:accelerator_cooler2", data=14),
    "cryotheum__cooler": MCBlock(name="qmd:accelerator_cooler2", data=15)
}


class AcceleratorJSONWriter(JSONWriter):
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
                            d[(x_, y_, z_)] = GLASS if self.transparent and y_ != 0 else CASING
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
                            d[(x_, y_, z_)] = GLASS if self.transparent and y_ != 0 else CASING
                        else:
                            d[(x_, y_, z_)] = COMPONENTS[self.seq[w, x_, y_].full_name]
        return d
