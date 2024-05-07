"""Default component set for QMD accelerators."""

from .. import base, types


QMD_ACCELERATOR_COMPONENTS: list[types.Component] = [
    types.Air(),
    types.Casing(
        block=base.BlockInfoTransparency(
            opaque=base.MCBlock(name="qmd:accelerator_casing"),
            transparent=base.MCBlock(name="qmd:accelerator_glass")
        )
    ),
    types.AcceleratorYoke(),
    types.BeamPipe(),
    types.RFCavity(
        name="copper",
        voltage=200,
        efficiency=0.5,
        heat=300,
        power=500,
        display=base.DisplayInfo(
            short_name="Cu",
            full_name="Copper RF Cavity",
            bold=True
        ),
        block=base.MCBlock(name="qmd:accelerator_cavity", data=0)
    ),
    types.RFCavity(
        name="magnesium_diboride",
        voltage=500,
        efficiency=0.8,
        heat=580,
        power=1000,
        display=base.DisplayInfo(
            short_name="Mg",
            full_name="Magnesium Diboride RF Cavity",
            bold=True
        ),
        block=base.MCBlock(name="qmd:accelerator_cavity", data=1)
    ),
    types.RFCavity(
        name="niobium_tin",
        voltage=1000,
        efficiency=0.9,
        heat=1140,
        power=2000,
        display=base.DisplayInfo(
            short_name="NS",
            full_name="Niobium-Tin RF Cavity",
            bold=True
        ),
        block=base.MCBlock(name="qmd:accelerator_cavity", data=2)
    ),
    types.RFCavity(
        name="niobium_titanium",
        voltage=2000,
        efficiency=0.95,
        heat=2260,
        power=4000,
        display=base.DisplayInfo(
            short_name="NT",
            full_name="Niobium-Titanium RF Cavity",
            bold=True
        ),
        block=base.MCBlock(name="qmd:accelerator_cavity", data=3)
    ),
    types.RFCavity(
        name="bscco",
        voltage=4000,
        efficiency=0.99,
        heat=4500,
        power=8000,
        display=base.DisplayInfo(
            short_name="BS",
            full_name="BSCCO RF Cavity",
            bold=True
        ),
        block=base.MCBlock(name="qmd:accelerator_cavity", data=4)
    ),
    types.AcceleratorMagnet(
        name="copper",
        strength=0.2,
        efficiency=0.5,
        heat=300,
        power=1000,
        display=base.DisplayInfo(
            short_name="Cu",
            full_name="Copper Electromagnet",
            italic=True
        ),
        block=base.MCBlock(name="qmd:accelerator_magnet", data=0)
    ),
    types.AcceleratorMagnet(
        name="magnesium_diboride",
        strength=0.5,
        efficiency=0.8,
        heat=580,
        power=2000,
        display=base.DisplayInfo(
            short_name="Mg",
            full_name="Magnesium Diboride Electromagnet",
            italic=True
        ),
        block=base.MCBlock(name="qmd:accelerator_magnet", data=1)
    ),
    types.AcceleratorMagnet(
        name="niobium_tin",
        strength=1.0,
        efficiency=0.9,
        heat=1140,
        power=4000,
        display=base.DisplayInfo(
            short_name="NS",
            full_name="Niobium-Tin Electromagnet",
            italic=True
        ),
        block=base.MCBlock(name="qmd:accelerator_magnet", data=2)
    ),
    types.AcceleratorMagnet(
        name="niobium_titanium",
        strength=2.0,
        efficiency=0.95,
        heat=2260,
        power=8000,
        display=base.DisplayInfo(
            short_name="NT",
            full_name="Niobium-Titanium Electromagnet",
            italic=True
        ),
        block=base.MCBlock(name="qmd:accelerator_magnet", data=3)
    ),
    types.AcceleratorMagnet(
        name="bscco",
        strength=4.0,
        efficiency=0.99,
        heat=4500,
        power=16000,
        display=base.DisplayInfo(
            short_name="BS",
            full_name="BSCCO Electromagnet",
            italic=True
        ),
        block=base.MCBlock(name="qmd:accelerator_magnet", data=4)
    ),
    types.AcceleratorCooler(
        name="water",
        cooling=60,
        placement_rule="one cavity",
        display=base.DisplayInfo(
            short_name="W ",
            full_name="Water Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=0)
    ),
    types.AcceleratorCooler(
        name="water",
        cooling=60,
        placement_rule="one cavity",
        display=base.DisplayInfo(
            short_name="W ",
            full_name="Water Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=0)
    ),
    types.AcceleratorCooler(
        name="iron",
        cooling=55,
        placement_rule="one magnet",
        display=base.DisplayInfo(
            short_name="Fe",
            full_name="Iron Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=1)
    ),
    types.AcceleratorCooler(
        name="redstone",
        cooling=115,
        placement_rule="one cavity && one magnet",
        display=base.DisplayInfo(
            short_name="Rs",
            full_name="Redstone Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=2)
    ),
    types.AcceleratorCooler(
        name="quartz",
        cooling=75,
        placement_rule="one redstone cooler",
        display=base.DisplayInfo(
            short_name="Q ",
            full_name="Quartz Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=3)
    ),
    types.AcceleratorCooler(
        name="obsidian",
        cooling=70,
        placement_rule="two glowstone coolers",
        display=base.DisplayInfo(
            short_name="Ob",
            full_name="Obsidian Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=4)
    ),
    types.AcceleratorCooler(
        name="nether_brick",
        cooling=90,
        placement_rule="one obsidian cooler",
        display=base.DisplayInfo(
            short_name="NB",
            full_name="Nether Brick Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=5)
    ),
    types.AcceleratorCooler(
        name="glowstone",
        cooling=110,
        placement_rule="two different magnets",
        display=base.DisplayInfo(
            short_name="Gs",
            full_name="Glowstone Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=6)
    ),
    types.AcceleratorCooler(
        name="lapis",
        cooling=130,
        placement_rule="one yoke && one magnet",
        display=base.DisplayInfo(
            short_name="Lp",
            full_name="Lapis Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=7)
    ),
    types.AcceleratorCooler(
        name="gold",
        cooling=95,
        placement_rule="two iron coolers",
        display=base.DisplayInfo(
            short_name="Au",
            full_name="Gold Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=8)
    ),
    types.AcceleratorCooler(
        name="prismarine",
        cooling=85,
        placement_rule="two water coolers",
        display=base.DisplayInfo(
            short_name="Pm",
            full_name="Prismarine Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=9)
    ),
    types.AcceleratorCooler(
        name="slime",
        cooling=165,
        placement_rule="two lead coolers && one water cooler",
        display=base.DisplayInfo(
            short_name="Sl",
            full_name="Slime Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=10)
    ),
    types.AcceleratorCooler(
        name="end_stone",
        cooling=50,
        placement_rule="one yoke",
        display=base.DisplayInfo(
            short_name="Es",
            full_name="End Stone Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=11)
    ),
    types.AcceleratorCooler(
        name="purpur",
        cooling=100,
        placement_rule="two end_stone coolers",
        display=base.DisplayInfo(
            short_name="Pp",
            full_name="Purpur Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=12)
    ),
    types.AcceleratorCooler(
        name="diamond",
        cooling=185,
        placement_rule="one prismarine cooler && one gold cooler",
        display=base.DisplayInfo(
            short_name="Dm",
            full_name="Diamond Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=13)
    ),
    types.AcceleratorCooler(
        name="emerald",
        cooling=135,
        placement_rule="one cavity && one prismarine cooler",
        display=base.DisplayInfo(
            short_name="Em",
            full_name="Emerald Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=14)
    ),
    types.AcceleratorCooler(
        name="copper",
        cooling=80,
        placement_rule="one water cooler",
        display=base.DisplayInfo(
            short_name="Cu",
            full_name="Copper Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler1", data=15)
    ),
    types.AcceleratorCooler(
        name="tin",
        cooling=120,
        placement_rule="two lapis coolers",
        display=base.DisplayInfo(
            short_name="Sn",
            full_name="Tin Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=0)
    ),
    types.AcceleratorCooler(
        name="lead",
        cooling=65,
        placement_rule="one iron cooler",
        display=base.DisplayInfo(
            short_name="Pb",
            full_name="Lead Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=1)
    ),
    types.AcceleratorCooler(
        name="boron",
        cooling=105,
        placement_rule="one yoke && one cavity",
        display=base.DisplayInfo(
            short_name="B ",
            full_name="Boron Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=2)
    ),
    types.AcceleratorCooler(
        name="lithium",
        cooling=125,
        placement_rule="one boron cooler",
        display=base.DisplayInfo(
            short_name="Li",
            full_name="Lithium Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=3)
    ),
    types.AcceleratorCooler(
        name="magnesium",
        cooling=150,
        placement_rule="one end_stone cooler && one prismarine cooler",
        display=base.DisplayInfo(
            short_name="Mg",
            full_name="Magnesium Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=4)
    ),
    types.AcceleratorCooler(
        name="manganese",
        cooling=180,
        placement_rule="one gold cooler && one quartz cooler",
        display=base.DisplayInfo(
            short_name="Mn",
            full_name="Manganese Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=5)
    ),
    types.AcceleratorCooler(
        name="aluminum",
        cooling=175,
        placement_rule="one tin cooler && one quartz cooler",
        display=base.DisplayInfo(
            short_name="Al",
            full_name="Aluminum Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=6)
    ),
    types.AcceleratorCooler(
        name="silver",
        cooling=160,
        placement_rule="two arsenic coolers",
        display=base.DisplayInfo(
            short_name="Ag",
            full_name="Silver Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=7)
    ),
    types.AcceleratorCooler(
        name="fluorite",
        cooling=155,
        placement_rule="three gold coolers",
        display=base.DisplayInfo(
            short_name="F ",
            full_name="Fluorite Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=8)
    ),
    types.AcceleratorCooler(
        name="villaumite",
        cooling=170,
        placement_rule="one purpur cooler && one prismarine cooler",
        display=base.DisplayInfo(
            short_name="Vi",
            full_name="Villaumeite Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=9)
    ),
    types.AcceleratorCooler(
        name="carobbiite",
        cooling=140,
        placement_rule="one end_stone cooler && one gold cooler",
        display=base.DisplayInfo(
            short_name="Cb",
            full_name="Carobbiite Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=10)
    ),
    types.AcceleratorCooler(
        name="arsenic",
        cooling=145,
        placement_rule="two different cavity",
        display=base.DisplayInfo(
            short_name="As",
            full_name="Arsenic Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=11)
    ),
    types.AcceleratorCooler(
        name="nitrogen",
        cooling=195,
        placement_rule="one lapis cooler && one gold cooler",
        display=base.DisplayInfo(
            short_name="N ",
            full_name="Nitrogen Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=12)
    ),
    types.AcceleratorCooler(
        name="helium",
        cooling=200,
        placement_rule="one boron cooler && one lapis cooler",
        display=base.DisplayInfo(
            short_name="He",
            full_name="Helium Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=13)
    ),
    types.AcceleratorCooler(
        name="enderium",
        cooling=190,
        placement_rule="three purpur coolers",
        display=base.DisplayInfo(
            short_name="Ed",
            full_name="Enderium Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=14)
    ),
    types.AcceleratorCooler(
        name="cryotheum",
        cooling=205,
        placement_rule="three tin coolers",
        display=base.DisplayInfo(
            short_name="Cr",
            full_name="Cryotheum Accelerator Cooler"
        ),
        block=base.MCBlock(name="qmd:accelerator_cooler2", data=15)
    )
]


QMD_LINEAR_ACCELERATOR_COMPONENTS: list[types.Component] = []
for component in QMD_ACCELERATOR_COMPONENTS:
    if component.full_name not in [
        "yoke:",
        "cooler:lapis",
        "cooler:end_stone",
        "cooler:purpur",
        "cooler:tin",
        "cooler:boron",
        "cooler:lithium",
        "cooler:magnesium",
        "cooler:aluminum",
        "cooler:villaumite",
        "cooler:carobbiite",
        "cooler:nitrogen",
        "cooler:helium",
        "cooler:enderium",
        "cooler:cryotheum"
    ]:
        QMD_LINEAR_ACCELERATOR_COMPONENTS.append(component.model_copy())
