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
    core.components.Component(name="", type="air"),
    core.components.Component(name="", type="casing", short_name="X "),
    NucleosynthesisBeam(name="", power=500, heat=100, short_name="=="),
    PlasmaGlass(name="", power=500, heat=100, short_name="[]"),
    PlasmaNozzle(name="", power=1000, heat=500, short_name="<>"),
    NucleosynthesisHeater(name="iron", cooling=5, short_name="Fe", placement_rule="one casing"),
    NucleosynthesisHeater(name="redstone", cooling=10, short_name="Rs", placement_rule="one beam"),
    NucleosynthesisHeater(name="quartz", cooling=20, short_name="Q ", placement_rule="two glass"),
    NucleosynthesisHeater(name="obsidian", cooling=40, short_name="Ob", placement_rule="exactly one quartz heater && exactly one redstone heater"),
    NucleosynthesisHeater(name="glowstone", cooling=80, short_name="Gs", placement_rule="two axial obsidian heaters"),
    NucleosynthesisHeater(name="lapis", cooling=160, short_name="Lp", placement_rule="exactly one redstone heater && two iron heaters"),
    NucleosynthesisHeater(name="gold", cooling=320, short_name="Au", placement_rule="one obsidian heater && one quartz heater"),
    NucleosynthesisHeater(name="diamond", cooling=640, short_name="Dm", placement_rule="one nozzle"),
]
