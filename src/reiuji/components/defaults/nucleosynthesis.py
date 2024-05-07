"""Default component set for QMD Nucleosynthesis Chambers."""

from .. import base, types


QMD_NUCLEOSYNTHESIS_COMPONENTS: list[types.Component] = [
    types.Air(),
    types.Casing(
        block=base.BlockInfoTransparency(
            opaque=base.MCBlock(name="qmd:containment_casing"),
            transparent=base.MCBlock(name="qmd:containment_glass")
        )
    ),
    types.NucleosynthesisBeam(),
    types.PlasmaGlass(),
    types.PlasmaNozzle(),
    types.NucleosynthesisHeater(
        name="iron",
        cooling=5,
        placement_rule="one casing",
        display=base.DisplayInfo(
            short_name="Fe",
            full_name="Iron Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=0)
    ),
    types.NucleosynthesisHeater(
        name="redstone",
        cooling=10,
        placement_rule="one beam",
        display=base.DisplayInfo(
            short_name="Rs",
            full_name="Redstone Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=1)
    ),
    types.NucleosynthesisHeater(
        name="quartz",
        cooling=20,
        placement_rule="two glass",
        display=base.DisplayInfo(
            short_name="Q ",
            full_name="Quartz Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=2)
    ),
    types.NucleosynthesisHeater(
        name="obsidian",
        cooling=40,
        placement_rule="exactly one quartz heater && exactly one redstone heater",
        display=base.DisplayInfo(
            short_name="Ob",
            full_name="Obsidian Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=3)
    ),
    types.NucleosynthesisHeater(
        name="glowstone",
        cooling=80,
        placement_rule="two axial obsidian heaters",
        display=base.DisplayInfo(
            short_name="Gs",
            full_name="Glowstone Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=4)
    ),
    types.NucleosynthesisHeater(
        name="lapis",
        cooling=160,
        placement_rule="exactly one redstone heater && two iron heaters",
        display=base.DisplayInfo(
            short_name="Lp",
            full_name="Lapis Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=5)
    ),
    types.NucleosynthesisHeater(
        name="gold",
        cooling=320,
        placement_rule="one obsidian heater && one quartz heater",
        display=base.DisplayInfo(
            short_name="Au",
            full_name="Gold Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=6)
    ),
    types.NucleosynthesisHeater(
        name="diamond",
        cooling=640,
        placement_rule="one nozzle",
        display=base.DisplayInfo(
            short_name="Dm",
            full_name="Diamond Heater"
        ),
        block=base.MCBlock(name="qmd:vacuum_chamber_heater", data=7)
    )
]
