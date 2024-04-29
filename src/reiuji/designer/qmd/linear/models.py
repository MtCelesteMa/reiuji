"""Data models for the QMD linear accelerator designer."""

from ... import core


class Beam(core.models.MultiblockComponent):
    type: str = "beam"
    attenuation: float


class Cavity(core.models.MultiblockComponent):
    type: str = "cavity"
    voltage: int
    efficiency: float
    heat: int
    power: int


class Magnet(core.models.MultiblockComponent):
    type: str = "magnet"
    strength: float
    efficiency: float
    heat: int
    power: int


class Cooler(core.models.MultiblockComponent):
    type: str = "cooler"
    cooling: int


DEFAULT_COMPONENTS: list[core.models.MultiblockComponent] = [
    core.models.MultiblockComponent(name="", type="air"),
    core.models.MultiblockComponent(name="", type="casing", short_name="X "),
    Beam(name="", attenuation=0.02, short_name="0 "),
    Cavity(name="copper", voltage=200, efficiency=0.5, heat=300, power=500, short_name="\033[1mCu\033[0m"),
    Cavity(name="magnesium_diboride", voltage=500, efficiency=0.8, heat=580, power=1000, short_name="\033[1mMg\033[0m"),
    Cavity(name="niobium_tin", voltage=1000, efficiency=0.9, heat=1140, power=2000, short_name="\033[1mNS\033[0m"),
    Cavity(name="niobium_titanium", voltage=2000, efficiency=0.95, heat=2260, power=4000, short_name="\033[1mNT\033[0m"),
    Cavity(name="bscco", voltage=4000, efficiency=0.99, heat=4500, power=8000, short_name="\033[1mBS\033[0m"),
    Magnet(name="copper", strength=0.2, efficiency=0.5, heat=300, power=1000, short_name="\033[3mCu\033[0m"),
    Magnet(name="magnesium_diboride", strength=0.5, efficiency=0.8, heat=580, power=2000, short_name="\033[3mMg\033[0m"),
    Magnet(name="niobium_tin", strength=1.0, efficiency=0.9, heat=1140, power=4000, short_name="\033[3mNS\033[0m"),
    Magnet(name="niobium_titanium", strength=2.0, efficiency=0.95, heat=2260, power=8000, short_name="\033[3mNT\033[0m"),
    Magnet(name="bscco", strength=4.0, efficiency=0.99, heat=4500, power=16000, short_name="\033[3mBS\033[0m"),
    Cooler(name="water", cooling=60, placement_rule="one cavity", short_name="W "),
    Cooler(name="iron", cooling=55, placement_rule="one magnet", short_name="Fe"),
    Cooler(name="redstone", cooling=115, placement_rule="one cavity && one magnet", short_name="Rs"),
    Cooler(name="quartz", cooling=75, placement_rule="one redstone cooler", short_name="Q "),
    Cooler(name="obsidian", cooling=70, placement_rule="two glowstone coolers", short_name="Ob"),
    Cooler(name="nether_brick", cooling=90, placement_rule="one obsidian cooler", short_name="NB"),
    Cooler(name="glowstone", cooling=110, placement_rule="two different magnets", short_name="Gs"),
    Cooler(name="gold", cooling=95, placement_rule="two iron coolers", short_name="Au"),
    Cooler(name="prismarine", cooling=85, placement_rule="two water coolers", short_name="Pm"),
    Cooler(name="slime", cooling=165, placement_rule="two lead coolers && one water cooler", short_name="Sl"),
    Cooler(name="diamond", cooling=185, placement_rule="one prismarine cooler && one gold cooler", short_name="Dm"),
    Cooler(name="emerald", cooling=135, placement_rule="one cavity && one prismarine cooler", short_name="Em"),
    Cooler(name="copper", cooling=80, placement_rule="one water cooler", short_name="Cu"),
    Cooler(name="lead", cooling=65, placement_rule="one iron cooler", short_name="Pb"),
    Cooler(name="manganese", cooling=180, placement_rule="one gold cooler && one quartz cooler", short_name="Mn"),
    Cooler(name="silver", cooling=160, placement_rule="two arsenic coolers", short_name="Ag"),
    Cooler(name="fluorite", cooling=155, placement_rule="three gold coolers", short_name="F "),
    Cooler(name="arsenic", cooling=145, placement_rule="two different cavity", short_name="As")
]
