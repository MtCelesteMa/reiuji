"""Data models for QMD nucleosynthesis chamber designer."""

from .... import core


class NucleosynthesisBeam(core.components.Component):
    type: str = "beam"
    power: int
    heat: int


class PlasmaGlass(core.components.Component):
    type: str = "glass"
    power: int
    heat: int


class PlasmaNozzle(core.components.Component):
    type: str = "nozzle"
    power: int
    heat: int


class NucleosynthesisHeater(core.components.Component):
    type: str = "heater"
    cooling: int


DEFAULT_COMPONENTS: list[core.components.Component] = [
    core.components.Component(
        name="",
        type="air",
        block={"": core.components.MCBlock(name="minecraft:air", is_tile_entity=False)},
    ),
    core.components.Component(
        name="",
        type="casing",
        short_name="X ",
        block={
            "": core.components.MCBlock(name="qmd:containment_casing"),
            "glass": core.components.MCBlock(name="qmd:containment_glass"),
        }
    ),
    NucleosynthesisBeam(
        name="",
        power=500,
        heat=100,
        short_name="==",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_beam")}
    ),
    PlasmaGlass(
        name="",
        power=500,
        heat=100,
        short_name="[]",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_plasma_glass")}
    ),
    PlasmaNozzle(
        name="",
        power=1000,
        heat=500,
        short_name="<>",
        block={
            "x": core.components.MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=0),
            "y": core.components.MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=1),
            "z": core.components.MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=2),
        }
    ),
    NucleosynthesisHeater(
        name="iron",
        cooling=5,
        short_name="Fe",
        placement_rule="one casing",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=0)}
    ),
    NucleosynthesisHeater(
        name="redstone",
        cooling=10,
        short_name="Rs",
        placement_rule="one beam",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=1)}
    ),
    NucleosynthesisHeater(
        name="quartz",
        cooling=20,
        short_name="Q ",
        placement_rule="two glass",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=2)}
    ),
    NucleosynthesisHeater(
        name="obsidian",
        cooling=40,
        short_name="Ob",
        placement_rule="exactly one quartz heater && exactly one redstone heater",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=3)}
    ),
    NucleosynthesisHeater(
        name="glowstone",
        cooling=80,
        short_name="Gs",
        placement_rule="two axial obsidian heaters",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=4)}
    ),
    NucleosynthesisHeater(
        name="lapis",
        cooling=160,
        short_name="Lp",
        placement_rule="exactly one redstone heater && two iron heaters",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=5)}
    ),
    NucleosynthesisHeater(
        name="gold",
        cooling=320,
        short_name="Au",
        placement_rule="one obsidian heater && one quartz heater",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=6)}
    ),
    NucleosynthesisHeater(
        name="diamond",
        cooling=640,
        short_name="Dm",
        placement_rule="one nozzle",
        block={"": core.components.MCBlock(name="qmd:vacuum_chamber_heater", data=7)}
    )
]
