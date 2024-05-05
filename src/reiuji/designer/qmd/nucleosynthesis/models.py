"""Data models for QMD nucleosynthesis chamber designer."""

from .... import core


class Beam(core.components.Component):
    type: str = "beam"
    power: int
    heat: int


class Glass(core.components.Component):
    type: str = "glass"
    power: int
    heat: int


class Nozzle(core.components.Component):
    type: str = "nozzle"
    power: int
    heat: int


class Heater(core.components.Component):
    type: str = "heater"
    cooling: int


DEFAULT_COMPONENTS: list[core.components.Component] = [
    core.components.Component(name="", type="air"),
    core.components.Component(name="", type="casing", short_name="X "),
    Beam(name="", power=500, heat=100, short_name="=="),
    Glass(name="", power=500, heat=100, short_name="[]"),
    Nozzle(name="", power=1000, heat=500, short_name="<>"),
    Heater(name="iron", cooling=5, short_name="Fe", placement_rule="one casing"),
    Heater(name="redstone", cooling=10, short_name="Rs", placement_rule="one beam"),
    Heater(name="quartz", cooling=20, short_name="Q ", placement_rule="two glass"),
    Heater(name="obsidian", cooling=40, short_name="Ob", placement_rule="exactly one quartz heater && exactly one redstone heater"),
    Heater(name="glowstone", cooling=80, short_name="Gs", placement_rule="two axial obsidian heaters"),
    Heater(name="lapis", cooling=160, short_name="Lp", placement_rule="exactly one redstone heater && two iron heaters"),
    Heater(name="gold", cooling=320, short_name="Au", placement_rule="one obsidian heater && one quartz heater"),
    Heater(name="diamond", cooling=640, short_name="Dm", placement_rule="one nozzle"),
]
