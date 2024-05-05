"""Data models for the NuclearCraft: Overhauled turbine dynamo designer."""

from .... import core


class DynamoCoil(core.components.Component):
    type: str = "coil"
    conductivity: float


DEFAULT_COMPONENTS: list[core.components.Component] = [
    core.components.Component(
        name="",
        type="air",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_casing")}
    ),
    core.components.Component(
        name="",
        type="casing",
        short_name="X ",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_casing")}
    ),
    core.components.Component(
        name="",
        type="bearing",
        short_name="0 ",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_rotor_bearing")}
    ),
    DynamoCoil(
        name="magnesium",
        conductivity=0.88,
        placement_rule="one bearing",
        short_name="Mg",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=0)}
    ),
    DynamoCoil(
        name="beryllium",
        conductivity=0.9,
        placement_rule="one magnesium coil",
        short_name="Be",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=1)}
    ),
    DynamoCoil(
        name="aluminum",
        conductivity=1.0,
        placement_rule="two magnesium coils",
        short_name="Al",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=2)}
    ),
    DynamoCoil(
        name="gold",
        conductivity=1.04,
        placement_rule="one aluminum coil",
        short_name="Au",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=3)}
    ),
    DynamoCoil(
        name="copper",
        conductivity=1.06,
        placement_rule="one beryllium coil",
        short_name="Cu",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=4)}
    ),
    DynamoCoil(
        name="silver",
        conductivity=1.12,
        placement_rule="one gold coil && one copper coil",
        short_name="Ag",
        block={"": core.components.MCBlock(name="nuclearcraft:turbine_dynamo_coil", data=5)}
    ),
]
