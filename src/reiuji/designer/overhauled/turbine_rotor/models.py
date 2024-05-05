"""Data models for the NuclearCraft: Overhauled turbine rotors designer."""

from .... import core


class RotorBlade(core.components.Component):
    type: str = "blade"
    efficiency: float
    expansion: float


class RotorStator(core.components.Component):
    type: str = "stator"
    expansion: float


DEFAULT_COMPONENTS: list[core.components.Component] = [
    RotorBlade(
        name="steel",
        efficiency=1.0,
        expansion=1.4,
        short_name="St",
        block={
            "x": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=1),
            "y": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=2),
            "z": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=3)
        }
    ),
    RotorBlade(
        name="extreme",
        efficiency=1.1,
        expansion=1.6,
        short_name="Ex",
        block={
            "x": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=1),
            "y": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=2),
            "z": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=3)
        }
    ),
    RotorBlade(
        name="sic_sic_cmc",
        efficiency=1.2,
        expansion=1.8,
        short_name="Si",
        block={
            "x": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=1),
            "y": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=2),
            "z": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=3)
        }
    ),
    RotorBlade(
        name="super",
        efficiency=1.25,
        expansion=1.9,
        short_name="Su",
        block={
            "x": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_super", data=1),
            "y": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_super", data=2),
            "z": core.components.MCBlock(name="nuclearcraft:turbine_rotor_blade_super", data=3)
        }
    ),
    RotorStator(
        name="",
        expansion=0.75,
        short_name="X ",
        block={
            "x": core.components.MCBlock(name="nuclearcraft:turbine_rotor_stator", data=1),
            "y": core.components.MCBlock(name="nuclearcraft:turbine_rotor_stator", data=2),
            "z": core.components.MCBlock(name="nuclearcraft:turbine_rotor_stator", data=3)
        }
    )
]