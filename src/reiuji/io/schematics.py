"""Schematic writer module of Reiuji."""

from . import json_writer

from nbt import nbt


def to_schematic(writer: json_writer.JSONWriter) -> nbt.NBTFile:
    d = writer.to_dict()
    x = max([k[0] for k in d.keys()]) + 1
    y = max([k[1] for k in d.keys()]) + 1
    z = max([k[2] for k in d.keys()]) + 1
    nbtfile = nbt.NBTFile()
    nbtfile.name = "Schematic"
    nbtfile.tags.append(nbt.TAG_Short(name="Width", value=x))
    nbtfile.tags.append(nbt.TAG_Short(name="Height", value=y))
    nbtfile.tags.append(nbt.TAG_Short(name="Length", value=z))
    nbtfile.tags.append(nbt.TAG_String(name="Materials", value="Alpha"))

    block_names = ["minecraft:air"] + list(set([v.name for v in d.values()]))
    name_to_id = {v: i for i, v in enumerate(block_names)}
    blocks = nbt.TAG_Byte_Array(name="Blocks")
    ba = [0] * (x * y * z)
    for k, v in d.items():
        ba[(k[1] * z + k[2]) * x + k[0]] = name_to_id[v.name]
    blocks.value = bytearray(ba)
    nbtfile.tags.append(blocks)

    data = nbt.TAG_Byte_Array(name="Data")
    da = [0] * (x * y * z)
    for k, v in d.items():
        da[(k[1] * z + k[2]) * x + k[0]] = v.data
    data.value = bytearray(da)
    nbtfile.tags.append(data)

    mapping = nbt.TAG_Compound(name="SchematicaMapping")
    for i, v in enumerate(block_names):
        mapping.tags.append(nbt.TAG_Short(name=v, value=i))
    nbtfile.tags.append(mapping)

    nbtfile.tags.append(nbt.TAG_List(name="Entities", type=nbt.TAG_Compound))

    tile_entities = nbt.TAG_List(name="TileEntities", type=nbt.TAG_Compound)
    nbtfile.tags.append(tile_entities)
    for k, v in d.items():
        tile_entity = nbt.TAG_Compound()
        tile_entity.tags.append(nbt.TAG_String(name="id", value=v.name))
        tile_entity.tags.append(nbt.TAG_Int(name="x", value=k[0]))
        tile_entity.tags.append(nbt.TAG_Int(name="y", value=k[1]))
        tile_entity.tags.append(nbt.TAG_Int(name="z", value=k[2]))
        for p in v.properties:
            tile_entity.tags.append(nbt.TAG_String(name=p, value=v.properties[p]))
        tile_entities.tags.append(tile_entity)
    return nbtfile
