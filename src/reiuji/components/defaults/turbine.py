"""Default component set for NuclearCraft: Overhauled turbines."""

from .. import base, types


OVERHAULED_TURBINE_DYNAMO_COMPONENTS: list[types.Component] = [
    types.Air(block=base.MCBlock(name="nuclearcraft:turbine_casing")),
    types.Casing(
        block=base.BlockInfoTransparency(
            opaque=base.MCBlock(name="nuclearcraft:turbine_casing"),
            transparent=base.MCBlock(name="nuclearcraft:turbine_casing")
        )
    ),
    types.DynamoBearing(),
    types.DynamoCoil(
        name="magnesium",
        conductivity=0.88,
        placement_rule="one bearing",
        display=base.DisplayInfo(
            short_name="Mg",
            full_name="Magnesium Dynamo Coil"
        ),
        block=base.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=0)
    ),
    types.DynamoCoil(
        name="beryllium",
        conductivity=0.9,
        placement_rule="one magnesium coil",
        display=base.DisplayInfo(
            short_name="Be",
            full_name="Beryllium Dynamo Coil"
        ),
        block=base.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=1)
    ),
    types.DynamoCoil(
        name="aluminum",
        conductivity=1.0,
        placement_rule="two magnesium coils",
        display=base.DisplayInfo(
            short_name="Al",
            full_name="Aluminum Dynamo Coil"
        ),
        block=base.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=2)
    ),
    types.DynamoCoil(
        name="gold",
        conductivity=1.04,
        placement_rule="one aluminum coil",
        display=base.DisplayInfo(
            short_name="Au",
            full_name="Gold Dynamo Coil"
        ),
        block=base.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=3)
    ),
    types.DynamoCoil(
        name="copper",
        conductivity=1.06,
        placement_rule="one beryllium coil",
        display=base.DisplayInfo(
            short_name="Cu",
            full_name="Copper Dynamo Coil"
        ),
        block=base.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=4)
    ),
    types.DynamoCoil(
        name="silver",
        conductivity=1.12,
        placement_rule="one gold coil && one copper coil",
        display=base.DisplayInfo(
            short_name="Ag",
            full_name="Silver Dynamo Coil"
        ),
        block=base.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=5)
    )
]


OVERHAULED_TURBINE_ROTOR_COMPONENTS_QMD: list[types.Component] = [
    types.RotorBlade(
        name="steel",
        efficiency=1.0,
        expansion=1.4,
        display=base.DisplayInfo(
            short_name="St",
            full_name="Steel Rotor Blade"
        ),
        block=base.BlockInfoOrientation(
            x=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=1),
            y=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=2),
            z=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_steel", data=3)
        )
    ),
    types.RotorBlade(
        name="extreme",
        efficiency=1.1,
        expansion=1.6,
        display=base.DisplayInfo(
            short_name="Ex",
            full_name="Extreme Rotor Blade"
        ),
        block=base.BlockInfoOrientation(
            x=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=1),
            y=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=2),
            z=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_extreme", data=3)
        )
    ),
    types.RotorBlade(
        name="sic_sic_cmc",
        efficiency=1.2,
        expansion=1.8,
        display=base.DisplayInfo(
            short_name="Si",
            full_name="SiC-SiC CMC Rotor Blade"
        ),
        block=base.BlockInfoOrientation(
            x=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=1),
            y=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=2),
            z=base.MCBlock(name="nuclearcraft:turbine_rotor_blade_sic_sic_cmc", data=3)
        )
    ),
    types.RotorBlade(
        name="super",
        efficiency=1.25,
        expansion=1.9,
        display=base.DisplayInfo(
            short_name="Su",
            full_name="Super Alloy Rotor Blade"
        ),
        block=base.BlockInfoOrientation(
            x=base.MCBlock(name="qmd:turbine_blade_super_alloy", data=1),
            y=base.MCBlock(name="qmd:turbine_blade_super_alloy", data=2),
            z=base.MCBlock(name="qmd:turbine_blade_super_alloy", data=3)
        )
    ),
    types.RotorStator(
        name="",
        expansion=0.75,
        display=base.DisplayInfo(
            short_name="X ",
            full_name="Stator"
        ),
        block=base.BlockInfoOrientation(
            x=base.MCBlock(name="nuclearcraft:turbine_rotor_stator", data=1),
            y=base.MCBlock(name="nuclearcraft:turbine_rotor_stator", data=2),
            z=base.MCBlock(name="nuclearcraft:turbine_rotor_stator", data=3)
        )
    ),
]


OVERHAULED_TURBINE_ROTOR_COMPONENTS = OVERHAULED_TURBINE_ROTOR_COMPONENTS_QMD.copy()
OVERHAULED_TURBINE_ROTOR_COMPONENTS.pop(3)
