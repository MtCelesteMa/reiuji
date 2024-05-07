"""Constraints specific to the QMD nucleosynthesis chamber designer."""

from .... import core
from ....components.types import *
from ... import base

import uuid
import itertools

from ortools.sat.python import cp_model


class StructureConstraint(base.constraints.Constraint):
    """Ensures that the internal structure of the chamber is correct."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("StructureConstraint.is_satisfied is not implemented.")

    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        if seq.shape != (5, 11, 7):
            raise ValueError("StructureConstraint requires a 5x11x7 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        beam_ids = type_to_id["beam"]
        glass_ids = type_to_id["glass"]
        nozzle_ids = type_to_id["nozzle"]
        air_ids = type_to_id["air"]

        beam_pos = [
            (2, 1, 2),
            (2, 9, 2),
            (2, 1, 3),
            (2, 9, 3),
            (2, 1, 4),
            (2, 9, 4),
            (2, 1, 5),
            (2, 2, 5),
            (2, 3, 5),
            (2, 4, 5),
            (2, 5, 5),
            (2, 6, 5),
            (2, 7, 5),
            (2, 8, 5),
            (2, 9, 5)
        ]
        glass_pos = [
            (2, 3, 1),
            (2, 4, 1),
            (2, 5, 1),
            (2, 6, 1),
            (2, 7, 1),
            (1, 3, 2),
            (1, 4, 2),
            (1, 5, 2),
            (1, 6, 2),
            (1, 7, 2),
            (3, 3, 2),
            (3, 4, 2),
            (3, 5, 2),
            (3, 6, 2),
            (3, 7, 2),
            (2, 3, 3),
            (2, 4, 3),
            (2, 5, 3),
            (2, 6, 3),
            (2, 7, 3),
        ]
        nozzle_pos = [
            (2, 2, 2),
            (2, 8, 2),
        ]
        air_pos = [
            (2, 3, 2),
            (2, 4, 2),
            (2, 5, 2),
            (2, 6, 2),
            (2, 7, 2)
        ]
        for i, component in enumerate(seq):
            idx = seq.index_int_to_tuple(i)
            if idx in beam_pos:
                model.AddAllowedAssignments([component], [(beam_id,) for beam_id in beam_ids])
            else:
                model.AddForbiddenAssignments([component], [(beam_id,) for beam_id in beam_ids])
            if idx in glass_pos:
                model.AddAllowedAssignments([component], [(glass_id,) for glass_id in glass_ids])
            else:
                model.AddForbiddenAssignments([component], [(glass_id,) for glass_id in glass_ids])
            if idx in nozzle_pos:
                model.AddAllowedAssignments([component], [(nozzle_id,) for nozzle_id in nozzle_ids])
            else:
                model.AddForbiddenAssignments([component], [(nozzle_id,) for nozzle_id in nozzle_ids])
            if idx in air_pos:
                model.AddAllowedAssignments([component], [(air_id,) for air_id in air_ids])
