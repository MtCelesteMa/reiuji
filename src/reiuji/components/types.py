"""Component types."""

from . import base

import typing

import pydantic


class Air(base.BaseComponent):
    discriminator: typing.Literal["Air"] = "Air"

    name: str = ""
    type: str = "air"

    block: base.MCBlock = pydantic.Field(default_factory=lambda: base.MCBlock(name="minecraft:air", is_tile_entity=False))


class Casing(base.BaseComponent):
    discriminator: typing.Literal["Casing"] = "Casing"

    name: str = ""
    type: str = "casing"

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="X ",
        full_name="Casing"
    ))
    block: base.BlockInfoTransparency


class DynamoBearing(base.BaseComponent):
    discriminator: typing.Literal["DynamoBearing"] = "DynamoBearing"

    name: str = ""
    type: str = "bearing"

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="0 ",
        full_name="Bearing",
        color=(128, 128, 128)
    ))
    block: base.MCBlock = pydantic.Field(default_factory=lambda: base.MCBlock(name="nuclearcraft:turbine_rotor_bearing"))


class DynamoCoil(base.BaseComponent):
    discriminator: typing.Literal["DynamoCoil"] = "DynamoCoil"

    type: str = "coil"

    conductivity: float

    block: base.MCBlock


class RotorBlade(base.BaseComponent):
    discriminator: typing.Literal["RotorBlade"] = "RotorBlade"

    type: str = "blade"

    efficiency: float
    expansion: float

    block: base.BlockInfoOrientation


class RotorStator(base.BaseComponent):
    discriminator: typing.Literal["RotorStator"] = "RotorStator"

    type: str = "stator"

    expansion: float

    block: base.BlockInfoOrientation


class BeamPipe(base.BaseComponent):
    discriminator: typing.Literal["BeamPipe"] = "BeamPipe"

    name: str = ""
    type: str = "beam"

    attenuation: float = 0.02

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="0 ",
        full_name="Beam Pipe",
        color=(128, 128, 128)
    ))
    block: base.MCBlock = pydantic.Field(default_factory=lambda: base.MCBlock(name="qmd:accelerator_beam"))


class AcceleratorYoke(base.BaseComponent):
    discriminator: typing.Literal["AcceleratorYoke"] = "AcceleratorYoke"

    name: str = ""
    type: str = "yoke"

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="Y ",
        full_name="Yoke",
        color=(128, 128, 128)
    ))
    block: base.MCBlock = pydantic.Field(default_factory=lambda: base.MCBlock(name="qmd:accelerator_yoke"))


class RFCavity(base.BaseComponent):
    discriminator: typing.Literal["RFCavity"] = "RFCavity"

    type: str = "cavity"

    voltage: int
    efficiency: float
    heat: int
    power: int

    block: base.MCBlock


class AcceleratorMagnet(base.BaseComponent):
    discriminator: typing.Literal["AcceleratorMagnet"] = "AcceleratorMagnet"

    type: str = "magnet"

    strength: float
    efficiency: float
    heat: int
    power: int

    block: base.MCBlock


class AcceleratorCooler(base.BaseComponent):
    discriminator: typing.Literal["AcceleratorCooler"] = "AcceleratorCooler"

    type: str = "cooler"

    cooling: int

    block: base.MCBlock


class NucleosynthesisBeam(base.BaseComponent):
    discriminator: typing.Literal["NucleosynthesisBeam"] = "NucleosynthesisBeam"

    name: str = ""
    type: str = "beam"

    power: int = 500
    heat: int = 100

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="==",
        full_name="Nucleosynthesis Beam",
        color=(128, 128, 128)
    ))
    block: base.MCBlock = pydantic.Field(default_factory=lambda: base.MCBlock(name="qmd:vacuum_chamber_beam"))


class PlasmaGlass(base.BaseComponent):
    discriminator: typing.Literal["PlasmaGlass"] = "PlasmaGlass"

    name: str = ""
    type: str = "glass"

    power: int = 500
    heat: int = 100

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="[]",
        full_name="Plasma Glass",
        color=(128, 128, 128)
    ))
    block: base.MCBlock = pydantic.Field(default_factory=lambda: base.MCBlock(name="qmd:vacuum_chamber_plasma_glass"))


class PlasmaNozzle(base.BaseComponent):
    discriminator: typing.Literal["PlasmaNozzle"] = "PlasmaNozzle"

    name: str = ""
    type: str = "nozzle"

    power: int = 1000
    heat: int = 500

    display: base.DisplayInfo = pydantic.Field(default_factory=lambda: base.DisplayInfo(
        short_name="<>",
        full_name="Plasma Nozzle",
        color=(128, 128, 128)
    ))
    block: base.BlockInfoOrientation = pydantic.Field(default_factory=lambda: base.BlockInfoOrientation(
        x=base.MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=0),
        y=base.MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=1),
        z=base.MCBlock(name="qmd:vacuum_chamber_plasma_nozzle", data=2)
    ))


class NucleosynthesisHeater(base.BaseComponent):
    discriminator: typing.Literal["NucleosynthesisHeater"] = "NucleosynthesisHeater"

    type: str = "heater"

    cooling: int

    block: base.MCBlock


Component = typing.Annotated[
    Air
    | Casing
    | DynamoBearing
    | DynamoCoil
    | RotorBlade
    | RotorStator
    | BeamPipe
    | AcceleratorYoke
    | RFCavity
    | AcceleratorMagnet
    | AcceleratorCooler
    | NucleosynthesisBeam
    | PlasmaGlass
    | PlasmaNozzle
    | NucleosynthesisHeater,
    pydantic.Field(discriminator="discriminator")
]
