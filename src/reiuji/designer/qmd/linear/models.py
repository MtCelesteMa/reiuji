"""Data models for the QMD linear accelerator designer."""

from .... import core


class ParticleBeam(core.components.Component):
    type: str = "beam"
    attenuation: float


class RFCavity(core.components.Component):
    type: str = "cavity"
    voltage: int
    efficiency: float
    heat: int
    power: int


class AcceleratorMagnet(core.components.Component):
    type: str = "magnet"
    strength: float
    efficiency: float
    heat: int
    power: int


class AcceleratorCooler(core.components.Component):
    type: str = "cooler"
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
            "": core.components.MCBlock(name="qmd:accelerator_casing"),
            "glass": core.components.MCBlock(name="minecraft:glass"),
        }
    ),
    ParticleBeam(
        name="",
        attenuation=0.02,
        short_name="0 ",
        block={"": core.components.MCBlock(name="qmd:accelerator_beam")},
    ),
    RFCavity(
        name="copper",
        voltage=200,
        efficiency=0.5,
        heat=300,
        power=500,
        short_name="\033[1mCu\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_cavity", data=0)}
    ),
    RFCavity(
        name="magnesium_diboride",
        voltage=500, 
        efficiency=0.8,
        heat=580,
        power=1000,
        short_name="\033[1mMg\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_cavity", data=1)}
    ),
    RFCavity(
        name="niobium_tin",
        voltage=1000,
        efficiency=0.9,
        heat=1140,
        power=2000,
        short_name="\033[1mNS\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_cavity", data=2)}
    ),
    RFCavity(
        name="niobium_titanium",
        voltage=2000,
        efficiency=0.95,
        heat=2260,
        power=4000,
        short_name="\033[1mNT\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_cavity", data=3)}
    ),
    RFCavity(
        name="bscco",
        voltage=4000,
        efficiency=0.99,
        heat=4500,
        power=8000,
        short_name="\033[1mBS\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_cavity", data=4)}
    ),
    AcceleratorMagnet(
        name="copper",
        strength=0.2,
        efficiency=0.5,
        heat=300,
        power=1000,
        short_name="\033[3mCu\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_magnet", data=0)}
    ),
    AcceleratorMagnet(
        name="magnesium_diboride",
        strength=0.5,
        efficiency=0.8,
        heat=580,
        power=2000,
        short_name="\033[3mMg\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_magnet", data=1)}
    ),
    AcceleratorMagnet(
        name="niobium_tin",
        strength=1.0,
        efficiency=0.9,
        heat=1140,
        power=4000,
        short_name="\033[3mNS\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_magnet", data=2)}
    ),
    AcceleratorMagnet(
        name="niobium_titanium",
        strength=2.0,
        efficiency=0.95,
        heat=2260,
        power=8000,
        short_name="\033[3mNT\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_magnet", data=3)}
    ),
    AcceleratorMagnet(
        name="bscco",
        strength=4.0,
        efficiency=0.99,
        heat=4500,
        power=16000,
        short_name="\033[3mBS\033[0m",
        block={"": core.components.MCBlock(name="qmd:accelerator_magnet", data=4)}
    ),
    AcceleratorCooler(
        name="water",
        cooling=60,
        placement_rule="one cavity",
        short_name="W ",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=0)}
    ),
    AcceleratorCooler(
        name="iron",
        cooling=55,
        placement_rule="one magnet",
        short_name="Fe",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=1)}
    ),
    AcceleratorCooler(
        name="redstone",
        cooling=115,
        placement_rule="one cavity && one magnet",
        short_name="Rs",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=2)}
    ),
    AcceleratorCooler(
        name="quartz",
        cooling=75,
        placement_rule="one redstone cooler",
        short_name="Q ",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=3)}
    ),
    AcceleratorCooler(
        name="obsidian",
        cooling=70,
        placement_rule="two glowstone coolers",
        short_name="Ob",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=4)}
    ),
    AcceleratorCooler(
        name="nether_brick",
        cooling=90,
        placement_rule="one obsidian cooler",
        short_name="NB",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=5)}
    ),
    AcceleratorCooler(
        name="glowstone",
        cooling=110,
        placement_rule="two different magnets",
        short_name="Gs",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=6)}
    ),
    AcceleratorCooler(
        name="gold",
        cooling=95,
        placement_rule="two iron coolers",
        short_name="Au",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=8)}
    ),
    AcceleratorCooler(
        name="prismarine",
        cooling=85,
        placement_rule="two water coolers",
        short_name="Pm",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=9)}
    ),
    AcceleratorCooler(
        name="slime",
        cooling=165,
        placement_rule="two lead coolers && one water cooler",
        short_name="Sl",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=10)}
    ),
    AcceleratorCooler(
        name="diamond",
        cooling=185,
        placement_rule="one prismarine cooler && one gold cooler",
        short_name="Dm",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=13)}
    ),
    AcceleratorCooler(
        name="emerald",
        cooling=135,
        placement_rule="one cavity && one prismarine cooler",
        short_name="Em",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=14)}
    ),
    AcceleratorCooler(
        name="copper",
        cooling=80,
        placement_rule="one water cooler",
        short_name="Cu",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler1", data=15)}
    ),
    AcceleratorCooler(
        name="lead",
        cooling=65,
        placement_rule="one iron cooler",
        short_name="Pb",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler2", data=1)}
    ),
    AcceleratorCooler(
        name="manganese",
        cooling=180,
        placement_rule="one gold cooler && one quartz cooler",
        short_name="Mn",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler2", data=5)}
    ),
    AcceleratorCooler(
        name="silver",
        cooling=160,
        placement_rule="two arsenic coolers",
        short_name="Ag",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler2", data=7)}
    ),
    AcceleratorCooler(
        name="fluorite",
        cooling=155,
        placement_rule="three gold coolers",
        short_name="F ",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler2", data=8)}
    ),
    AcceleratorCooler(
        name="arsenic",
        cooling=145,
        placement_rule="two different cavity",
        short_name="As",
        block={"": core.components.MCBlock(name="qmd:accelerator_cooler2", data=11)}
    )
]
