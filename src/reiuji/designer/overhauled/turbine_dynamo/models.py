"""Data models for the NuclearCraft: Overhauled turbine dynamo designer."""

from ... import core


class DynamoCoil(core.models.MultiblockComponent):
    type: str = "coil"
    conductivity: float


DEFAULT_COMPONENTS: list[core.models.MultiblockComponent] = [
    core.models.MultiblockComponent(name="", type="air"),
    core.models.MultiblockComponent(name="", type="casing", short_name="X "),
    core.models.MultiblockComponent(name="", type="bearing", short_name="0 "),
    DynamoCoil(name="magnesium", conductivity=0.88, placement_rule="one bearing", short_name="Mg"),
    DynamoCoil(name="beryllium", conductivity=0.9, placement_rule="one magnesium coil", short_name="Be"),
    DynamoCoil(name="aluminum", conductivity=1.0, placement_rule="two magnesium coils", short_name="Al"),
    DynamoCoil(name="gold", conductivity=1.04, placement_rule="one aluminum coil", short_name="Au"),
    DynamoCoil(name="copper", conductivity=1.06, placement_rule="one beryllium coil", short_name="Cu"),
    DynamoCoil(name="silver", conductivity=1.12, placement_rule="one gold coil && one copper coil", short_name="Ag"),
]
