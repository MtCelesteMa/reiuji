"""Data models for the NuclearCraft: Overhauled turbine rotors designer."""

from ... import core


class RotorBlade(core.models.MultiblockComponent):
    type: str = "blade"
    efficiency: float
    expansion: float


class RotorStator(core.models.MultiblockComponent):
    type: str = "stator"
    expansion: float


DEFAULT_COMPONENTS: list[core.models.MultiblockComponent] = [
    RotorBlade(name="steel", efficiency=1.0, expansion=1.4, short_name="St"),
    RotorBlade(name="extreme", efficiency=1.1, expansion=1.6, short_name="Ex"),
    RotorBlade(name="sic_sic_cmc", efficiency=1.2, expansion=1.8, short_name="Si"),
    RotorStator(name="", expansion=0.75, short_name="X ")
]