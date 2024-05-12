"""Base schematic writer class."""

from ... import core
from ... import components

import itertools
import pathlib

from nbt import nbt


class SchematicWriter:
    def to_structure(self) -> core.multi_sequence.MultiSequence[components.base.MCBlock]:
        raise NotImplementedError

    def to_nbt(self, structure: core.multi_sequence.MultiSequence[components.base.MCBlock]) -> nbt.NBTFile:
        y, z, x = structure.shape
        nbtfile = nbt.NBTFile()
        nbtfile.name = "Schematic"
        nbtfile.tags.append(nbt.TAG_Short(name="Width", value=x))
        nbtfile.tags.append(nbt.TAG_Short(name="Height", value=y))
        nbtfile.tags.append(nbt.TAG_Short(name="Length", value=z))
        nbtfile.tags.append(nbt.TAG_String(name="Materials", value="Alpha"))

        block_names = list(set([v.name for v in structure.seq]))
        name_to_id = {v: i for i, v in enumerate(block_names)}
        block_array = [0] * (y * z * x)
        data_array = [0] * (y * z * x)
        for y_ in range(y):
            for z_ in range(z):
                for x_ in range(x):
                    block_array[(y_ * z + z_) * x + x_] = name_to_id[structure[y_, z_, x_].name]
                    data_array[(y_ * z + z_) * x + x_] = structure[y_, z_, x_].data

        blocks = nbt.TAG_Byte_Array(name="Blocks")
        blocks.value = bytearray([v % 256 for v in block_array])
        nbtfile.tags.append(blocks)

        add_blocks = nbt.TAG_Byte_Array(name="AddBlocks")
        add_blocks.value = bytearray([((v[0] // 256) % 16) + ((((v[1] // 256) % 16) * 16) if len(v) == 2 else 0) for v in itertools.batched(block_array, 2)])
        nbtfile.tags.append(add_blocks)

        data = nbt.TAG_Byte_Array(name="Data")
        data.value = bytearray(data_array)
        nbtfile.tags.append(data)

        mapping = nbt.TAG_Compound(name="SchematicaMapping")
        for i, v in enumerate(block_names):
            mapping.tags.append(nbt.TAG_Short(name=v, value=i))
        nbtfile.tags.append(mapping)

        nbtfile.tags.append(nbt.TAG_List(name="Entities", type=nbt.TAG_Compound))

        tile_entities = nbt.TAG_List(name="TileEntities", type=nbt.TAG_Compound)
        for y_ in range(y):
            for z_ in range(z):
                for x_ in range(x):
                    if structure[y_, z_, x_].is_tile_entity:
                        tile_entity = nbt.TAG_Compound()
                        tile_entity.tags.append(nbt.TAG_String(name="id", value=structure[y_, z_, x_].name))
                        tile_entity.tags.append(nbt.TAG_Int(name="x", value=x_))
                        tile_entity.tags.append(nbt.TAG_Int(name="y", value=y_))
                        tile_entity.tags.append(nbt.TAG_Int(name="z", value=z_))
                        for p in structure[y_, z_, x_].properties:
                            tile_entity.tags.append(nbt.TAG_String(name=p, value=structure[y_, z_, x_].properties[p]))
                        tile_entities.tags.append(tile_entity)
        nbtfile.tags.append(tile_entities)

        return nbtfile
    
    def write(self, output: pathlib.Path | str) -> None:
        structure = self.to_structure()
        nbtfile = self.to_nbt(structure)
        nbtfile.write_file(output)
