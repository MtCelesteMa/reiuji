"""Constraints specific to the QMD synchrotron designer."""

from ... import core
from . import models

import uuid

from ortools.sat.python import cp_model


class BeamConstraint(core.constraints.Constraint):
    """Ensures that the beam is placed in a ring formation. Note that the synchrotron goes in the +x and +z direction."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> bool:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("BeamConstraint requires a NxNx5 sequence.")
        for x in range(seq.shape[0]):
            for z in range(seq.shape[1]):
                for y in range(seq.shape[2]):
                    if y != 2:
                        if seq[x, z, y].type == "beam":
                            return False
                    else:
                        if 3 <= x <= (seq.shape[0] - 4) and 3 <= z <= (seq.shape[1] - 4):
                            if seq[x, z, y].type == "beam":
                                return False
                        elif 2 <= x <= (seq.shape[0] - 3) and 2 <= z <= (seq.shape[1] - 3):
                            if seq[x, z, y].type != "beam":
                                return False
                        else:
                            if seq[x, z, y].type == "beam":
                                return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[core.models.MultiblockComponent]
    ) -> None:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("BeamConstraint requires a NxNx5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        beam_ids = type_to_id["beam"]
        for x in range(seq.shape[0]):
            for z in range(seq.shape[1]):
                for y in range(seq.shape[2]):
                    if y != 2:
                        model.AddForbiddenAssignments([seq[x, z, y]], [(beam_id,) for beam_id in beam_ids])
                    else:
                        if 3 <= x <= (seq.shape[0] - 4) and 3 <= z <= (seq.shape[1] - 4):
                            model.AddForbiddenAssignments([seq[x, z, y]], [(beam_id,) for beam_id in beam_ids])
                        elif 2 <= x <= (seq.shape[0] - 3) and 2 <= z <= (seq.shape[1] - 3):
                            model.AddAllowedAssignments([seq[x, z, y]], [(beam_id,) for beam_id in beam_ids])
                        else:
                            model.AddForbiddenAssignments([seq[x, z, y]], [(beam_id,) for beam_id in beam_ids])


class CasingConstraint(core.constraints.Constraint):
    """Ensures that the casing is placed properly around the beam. Note that the synchrotron goes in the +x and +z direction."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> bool:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("CasingConstraint requires a NxNx5 sequence.")
        for y in range(seq.shape[2]):
            for x in range(seq.shape[0]):
                for z in range(seq.shape[1]):
                    if y == 0 or y == 4:
                        if 5 <= x <= (seq.shape[0] - 6) and 5 <= z <= (seq.shape[1] - 6):
                            if seq[x, z, y].type == "casing":
                                return False
                        else:
                            if seq[x, z, y].type != "casing":
                                return False
                    else:
                        if 5 <= x <= (seq.shape[0] - 6) and 5 <= z <= (seq.shape[1] - 6):
                            if seq[x, z, y].type == "casing":
                                return False
                        elif 4 <= x <= (seq.shape[0] - 5) and 4 <= z <= (seq.shape[1] - 5):
                            if seq[x, z, y].type != "casing":
                                return False
                        elif 1 <= x <= (seq.shape[0] - 2) and 1 <= z <= (seq.shape[1] - 2):
                            if seq[x, z, y].type == "casing":
                                return False
                        else:
                            if seq[x, z, y].type != "casing":
                                return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[core.models.MultiblockComponent]
    ) -> None:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("CasingConstraint requires a NxNx5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        casing_ids = type_to_id["casing"]
        for y in range(seq.shape[2]):
            for x in range(seq.shape[0]):
                for z in range(seq.shape[1]):
                    if y == 0 or y == 4:
                        if 5 <= x <= (seq.shape[0] - 6) and 5 <= z <= (seq.shape[1] - 6):
                            model.AddForbiddenAssignments([seq[x, z, y]], [(casing_id,) for casing_id in casing_ids])
                        else:
                            model.AddAllowedAssignments([seq[x, z, y]], [(casing_id,) for casing_id in casing_ids])
                    else:
                        if 5 <= x <= (seq.shape[0] - 6) and 5 <= z <= (seq.shape[1] - 6):
                            model.AddForbiddenAssignments([seq[x, z, y]], [(casing_id,) for casing_id in casing_ids])
                        elif 4 <= x <= (seq.shape[0] - 5) and 4 <= z <= (seq.shape[1] - 5):
                            model.AddAllowedAssignments([seq[x, z, y]], [(casing_id,) for casing_id in casing_ids])
                        elif 1 <= x <= (seq.shape[0] - 2) and 1 <= z <= (seq.shape[1] - 2):
                            model.AddForbiddenAssignments([seq[x, z, y]], [(casing_id,) for casing_id in casing_ids])
                        else:
                            model.AddAllowedAssignments([seq[x, z, y]], [(casing_id,) for casing_id in casing_ids])


class AirConstraint(core.constraints.Constraint):
    """Ensures that the central portion of the synchrotron is made of air blocks. Note that the synchrotron goes in the +x and +z direction."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> bool:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("AirConstraint requires a NxNx5 sequence.")
        for y in range(seq.shape[2]):
            for x in range(seq.shape[0]):
                for z in range(seq.shape[1]):
                    if 5 <= x <= (seq.shape[0] - 6) and 5 <= z <= (seq.shape[1] - 6):
                        if seq[x, z, y].type == "air":
                            return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[core.models.MultiblockComponent]
    ) -> None:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("AirConstraint requires a NxNx5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        air_ids = type_to_id["air"]
        for y in range(seq.shape[2]):
            for x in range(seq.shape[0]):
                for z in range(seq.shape[1]):
                    if 5 <= x <= (seq.shape[0] - 6) and 5 <= z <= (seq.shape[1] - 6):
                        model.AddAllowedAssignments([seq[x, z, y]], [(air_id,) for air_id in air_ids])


class MagnetConstraint(core.constraints.Constraint):
    """Ensures that dipoles and quadrupoles are placed properly around the beam."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> bool:
        raise NotImplementedError("MagnetConstraint.is_satisfied is not implemented.")
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[core.models.MultiblockComponent]
    ) -> None:
        if seq.shape[0] != seq.shape[1] or seq.shape[2] != 5:
            raise ValueError("MagnetConstraint requires a NxNx5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        magnet_ids = type_to_id["magnet"]
        yoke_ids = type_to_id["yoke"]
        # North magnets
        has_dipole_N = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1])]
        has_quadrupole_N = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1])]
        model.Add(has_dipole_N[2] == 1)
        model.Add(has_dipole_N[3] == 0)
        model.Add(has_dipole_N[seq.shape[1] - 3] == 1)
        model.Add(has_dipole_N[seq.shape[1] - 4] == 0)
        for z in range(4, seq.shape[1] - 4):
            magnet_positions_center = [
                seq[2, z, 3],
                seq[2, z, 1]
            ]
            magnet_positions_side = [
                seq[1, z, 2],
                seq[3, z, 2]
            ]
            magnet_positions_corner = [
                seq[1, z, 1],
                seq[3, z, 1],
                seq[1, z, 3],
                seq[3, z, 3]
            ]
            has_magnet = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_N[z], has_quadrupole_N[z]]).OnlyEnforceIf(has_magnet)
            model.AddBoolAnd([has_dipole_N[z].Not(), has_quadrupole_N[z].Not()]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_center:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet)
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_side:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_N[z])
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_N[z].Not())
            for pos in magnet_positions_corner:
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids])
            
            model.Add(magnet_positions_center[0] == magnet_positions_center[1]).OnlyEnforceIf(has_magnet)
            model.Add(magnet_positions_side[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_N[z])
            model.Add(magnet_positions_center[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_N[z])
            
            model.AddImplication(has_dipole_N[z], has_dipole_N[z - 2].Not())
            model.AddImplication(has_dipole_N[z], has_dipole_N[z - 1].Not())
            model.AddImplication(has_dipole_N[z], has_quadrupole_N[z - 1].Not())
            model.AddImplication(has_dipole_N[z], has_quadrupole_N[z + 1].Not())
            model.AddImplication(has_dipole_N[z], has_dipole_N[z + 1].Not())
            model.AddImplication(has_dipole_N[z], has_dipole_N[z + 2].Not())
        
        # North Yokes
        for z in range(4, seq.shape[1] - 4):
            yoke_positions_center = [
                seq[1, z, 1],
                seq[1, z, 2],
                seq[1, z, 3],
                seq[3, z, 1],
                seq[3, z, 2],
                seq[3, z, 3]
            ]
            yoke_positions_side = [
                seq[1, z, 1],
                seq[1, z, 2],
                seq[1, z, 3],
                seq[2, z, 1],
                seq[2, z, 3],
                seq[3, z, 1],
                seq[3, z, 2],
                seq[3, z, 3]
            ]
            for pos in yoke_positions_center:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(has_dipole_N[z])
            dipole_on_sides = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_N[z - 1], has_dipole_N[z + 1]]).OnlyEnforceIf(dipole_on_sides)
            model.AddBoolAnd([has_dipole_N[z - 1].Not(), has_dipole_N[z + 1].Not()]).OnlyEnforceIf(dipole_on_sides.Not())
            for pos in yoke_positions_side:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_on_sides)
            dipole_in_range = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_N[z], dipole_on_sides]).OnlyEnforceIf(dipole_in_range)
            model.AddBoolAnd([has_dipole_N[z].Not(), dipole_on_sides.Not()]).OnlyEnforceIf(dipole_in_range.Not())
            for pos in yoke_positions_side:
                model.AddForbiddenAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_in_range.Not())

        # South magnets
        has_dipole_S = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1])]
        has_quadrupole_S = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1])]
        model.Add(has_dipole_S[2] == 1)
        model.Add(has_dipole_S[3] == 0)
        model.Add(has_dipole_S[seq.shape[1] - 3] == 1)
        model.Add(has_dipole_S[seq.shape[1] - 4] == 0)
        for z in range(4, seq.shape[1] - 4):
            magnet_positions_center = [
                seq[seq.shape[0] - 3, z, 3],
                seq[seq.shape[0] - 3, z, 1]
            ]
            magnet_positions_side = [
                seq[seq.shape[0] - 2, z, 2],
                seq[seq.shape[0] - 4, z, 2]
            ]
            magnet_positions_corner = [
                seq[seq.shape[0] - 2, z, 1],
                seq[seq.shape[0] - 4, z, 1],
                seq[seq.shape[0] - 2, z, 3],
                seq[seq.shape[0] - 4, z, 3]
            ]
            has_magnet = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_S[z], has_quadrupole_S[z]]).OnlyEnforceIf(has_magnet)
            model.AddBoolAnd([has_dipole_S[z].Not(), has_quadrupole_S[z].Not()]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_center:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet)
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_side:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_S[z])
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_S[z].Not())
            for pos in magnet_positions_corner:
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids])
            
            model.Add(magnet_positions_center[0] == magnet_positions_center[1]).OnlyEnforceIf(has_magnet)
            model.Add(magnet_positions_side[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_S[z])
            model.Add(magnet_positions_center[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_S[z])
            
            model.AddImplication(has_dipole_S[z], has_dipole_S[z - 2].Not())
            model.AddImplication(has_dipole_S[z], has_dipole_S[z - 1].Not())
            model.AddImplication(has_dipole_S[z], has_quadrupole_S[z - 1].Not())
            model.AddImplication(has_dipole_S[z], has_quadrupole_S[z + 1].Not())
            model.AddImplication(has_dipole_S[z], has_dipole_S[z + 1].Not())
            model.AddImplication(has_dipole_S[z], has_dipole_S[z + 2].Not())
        
        # South Yokes
        for z in range(4, seq.shape[1] - 4):
            yoke_positions_center = [
                seq[seq.shape[0] - 2, z, 1],
                seq[seq.shape[0] - 2, z, 2],
                seq[seq.shape[0] - 2, z, 3],
                seq[seq.shape[0] - 4, z, 1],
                seq[seq.shape[0] - 4, z, 2],
                seq[seq.shape[0] - 4, z, 3]
            ]
            yoke_positions_side = [
                seq[seq.shape[0] - 2, z, 1],
                seq[seq.shape[0] - 2, z, 2],
                seq[seq.shape[0] - 2, z, 3],
                seq[seq.shape[0] - 3, z, 1],
                seq[seq.shape[0] - 3, z, 3],
                seq[seq.shape[0] - 4, z, 1],
                seq[seq.shape[0] - 4, z, 2],
                seq[seq.shape[0] - 4, z, 3]
            ]
            for pos in yoke_positions_center:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(has_dipole_S[z])
            dipole_on_sides = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_S[z - 1], has_dipole_S[z + 1]]).OnlyEnforceIf(dipole_on_sides)
            model.AddBoolAnd([has_dipole_S[z - 1].Not(), has_dipole_S[z + 1].Not()]).OnlyEnforceIf(dipole_on_sides.Not())
            for pos in yoke_positions_side:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_on_sides)
            dipole_in_range = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_S[z], dipole_on_sides]).OnlyEnforceIf(dipole_in_range)
            model.AddBoolAnd([has_dipole_S[z].Not(), dipole_on_sides.Not()]).OnlyEnforceIf(dipole_in_range.Not())
            for pos in yoke_positions_side:
                model.AddForbiddenAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_in_range.Not())
        
        # West magnets
        has_dipole_W = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        has_quadrupole_W = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        model.Add(has_dipole_W[2] == 1)
        model.Add(has_dipole_W[3] == 0)
        model.Add(has_dipole_W[seq.shape[0] - 3] == 1)
        model.Add(has_dipole_W[seq.shape[0] - 4] == 0)
        for x in range(4, seq.shape[1] - 4):
            magnet_positions_center = [
                seq[x, 2, 3],
                seq[x, 2, 1]
            ]
            magnet_positions_side = [
                seq[x, 1, 2],
                seq[x, 3, 2]
            ]
            magnet_positions_corner = [
                seq[x, 1, 1],
                seq[x, 3, 1],
                seq[x, 1, 3],
                seq[x, 3, 3]
            ]
            has_magnet = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_W[x], has_quadrupole_W[x]]).OnlyEnforceIf(has_magnet)
            model.AddBoolAnd([has_dipole_W[x].Not(), has_quadrupole_W[x].Not()]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_center:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet)
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_side:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_W[x])
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_W[x].Not())
            for pos in magnet_positions_corner:
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids])
            
            model.Add(magnet_positions_center[0] == magnet_positions_center[1]).OnlyEnforceIf(has_magnet)
            model.Add(magnet_positions_side[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_W[x])
            model.Add(magnet_positions_center[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_W[x])
            
            model.AddImplication(has_dipole_W[x], has_dipole_W[x - 2].Not())
            model.AddImplication(has_dipole_W[x], has_dipole_W[x - 1].Not())
            model.AddImplication(has_dipole_W[x], has_quadrupole_W[x - 1].Not())
            model.AddImplication(has_dipole_W[x], has_quadrupole_W[x + 1].Not())
            model.AddImplication(has_dipole_W[x], has_dipole_W[x + 1].Not())
            model.AddImplication(has_dipole_W[x], has_dipole_W[x + 2].Not())
        
        # West Yokes
        for x in range(4, seq.shape[0] - 4):
            yoke_positions_center = [
                seq[x, 1, 1],
                seq[x, 1, 2],
                seq[x, 1, 3],
                seq[x, 3, 1],
                seq[x, 3, 2],
                seq[x, 3, 3]
            ]
            yoke_positions_side = [
                seq[x, 1, 1],
                seq[x, 1, 2],
                seq[x, 1, 3],
                seq[x, 2, 1],
                seq[x, 2, 3],
                seq[x, 3, 1],
                seq[x, 3, 2],
                seq[x, 3, 3]
            ]
            for pos in yoke_positions_center:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(has_dipole_W[x])
            dipole_on_sides = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_W[x - 1], has_dipole_W[x + 1]]).OnlyEnforceIf(dipole_on_sides)
            model.AddBoolAnd([has_dipole_W[x - 1].Not(), has_dipole_W[x + 1].Not()]).OnlyEnforceIf(dipole_on_sides.Not())
            for pos in yoke_positions_side:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_on_sides)
            dipole_in_range = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_W[x], dipole_on_sides]).OnlyEnforceIf(dipole_in_range)
            model.AddBoolAnd([has_dipole_W[x].Not(), dipole_on_sides.Not()]).OnlyEnforceIf(dipole_in_range.Not())
            for pos in yoke_positions_side:
                model.AddForbiddenAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_in_range.Not())
        
        # East magnets
        has_dipole_E = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        has_quadrupole_E = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        model.Add(has_dipole_E[2] == 1)
        model.Add(has_dipole_E[3] == 0)
        model.Add(has_dipole_E[seq.shape[0] - 3] == 1)
        model.Add(has_dipole_E[seq.shape[0] - 4] == 0)
        for x in range(4, seq.shape[1] - 4):
            magnet_positions_center = [
                seq[x, seq.shape[1] - 3, 3],
                seq[x, seq.shape[1] - 3, 1]
            ]
            magnet_positions_side = [
                seq[x, seq.shape[1] - 2, 2],
                seq[x, seq.shape[1] - 4, 2]
            ]
            magnet_positions_corner = [
                seq[x, seq.shape[1] - 2, 1],
                seq[x, seq.shape[1] - 4, 1],
                seq[x, seq.shape[1] - 2, 3],
                seq[x, seq.shape[1] - 4, 3]
            ]
            has_magnet = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_E[x], has_quadrupole_E[x]]).OnlyEnforceIf(has_magnet)
            model.AddBoolAnd([has_dipole_E[x].Not(), has_quadrupole_E[x].Not()]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_center:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet)
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet.Not())
            for pos in magnet_positions_side:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_E[x])
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_quadrupole_E[x].Not())
            for pos in magnet_positions_corner:
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids])

            model.Add(magnet_positions_center[0] == magnet_positions_center[1]).OnlyEnforceIf(has_magnet)
            model.Add(magnet_positions_side[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_E[x])
            model.Add(magnet_positions_center[0] == magnet_positions_side[1]).OnlyEnforceIf(has_quadrupole_E[x])
            
            model.AddImplication(has_dipole_E[x], has_dipole_E[x - 2].Not())
            model.AddImplication(has_dipole_E[x], has_dipole_E[x - 1].Not())
            model.AddImplication(has_dipole_E[x], has_quadrupole_E[x - 1].Not())
            model.AddImplication(has_dipole_E[x], has_quadrupole_E[x + 1].Not())
            model.AddImplication(has_dipole_E[x], has_dipole_E[x + 1].Not())
            model.AddImplication(has_dipole_E[x], has_dipole_E[x + 2].Not())
        
        # East Yokes
        for x in range(4, seq.shape[0] - 4):
            yoke_positions_center = [
                seq[x, seq.shape[1] - 2, 1],
                seq[x, seq.shape[1] - 2, 2],
                seq[x, seq.shape[1] - 2, 3],
                seq[x, seq.shape[1] - 4, 1],
                seq[x, seq.shape[1] - 4, 2],
                seq[x, seq.shape[1] - 4, 3]
            ]
            yoke_positions_side = [
                seq[x, seq.shape[1] - 2, 1],
                seq[x, seq.shape[1] - 2, 2],
                seq[x, seq.shape[1] - 2, 3],
                seq[x, seq.shape[1] - 3, 1],
                seq[x, seq.shape[1] - 3, 3],
                seq[x, seq.shape[1] - 4, 1],
                seq[x, seq.shape[1] - 4, 2],
                seq[x, seq.shape[1] - 4, 3]
            ]
            for pos in yoke_positions_center:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(has_dipole_E[x])
            dipole_on_sides = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_E[x - 1], has_dipole_E[x + 1]]).OnlyEnforceIf(dipole_on_sides)
            model.AddBoolAnd([has_dipole_E[x - 1].Not(), has_dipole_E[x + 1].Not()]).OnlyEnforceIf(dipole_on_sides.Not())
            for pos in yoke_positions_side:
                model.AddAllowedAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_on_sides)
            dipole_in_range = model.NewBoolVar(str(uuid.uuid4()))
            model.AddBoolOr([has_dipole_E[x], dipole_on_sides]).OnlyEnforceIf(dipole_in_range)
            model.AddBoolAnd([has_dipole_E[x].Not(), dipole_on_sides.Not()]).OnlyEnforceIf(dipole_in_range.Not())
            for pos in yoke_positions_side:
                model.AddForbiddenAssignments([pos], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(dipole_in_range.Not())

        # Corner magnets
        for x, z in [(2, 2), (2, seq.shape[1] - 3), (seq.shape[0] - 3, 2), (seq.shape[0] - 3, seq.shape[1] - 3)]:
            model.AddAllowedAssignments([seq[x, z, 1]], [(magnet_id,) for magnet_id in magnet_ids])
            model.AddAllowedAssignments([seq[x, z, 3]], [(magnet_id,) for magnet_id in magnet_ids])
            model.Add(seq[x, z, 1] == seq[x, z, 3])
        
        # Corner yokes

        # NW Corner Bottom and Top Layers
        for x, z in [(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)]:
            model.AddAllowedAssignments([seq[x, z, 1]], [(yoke_id,) for yoke_id in yoke_ids])
            model.AddAllowedAssignments([seq[x, z, 3]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # NE Corner Bottom and Top Layers
        for x, z in [(1, seq.shape[1] - 4), (1, seq.shape[1] - 3), (1, seq.shape[1] - 2), (2, seq.shape[1] - 4), (2, seq.shape[1] - 2), (3, seq.shape[1] - 4), (3, seq.shape[1] - 3), (3, seq.shape[1] - 2)]:
            model.AddAllowedAssignments([seq[x, z, 1]], [(yoke_id,) for yoke_id in yoke_ids])
            model.AddAllowedAssignments([seq[x, z, 3]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # SW Corner Bottom and Top Layers
        for x, z in [(seq.shape[0] - 4, 1), (seq.shape[0] - 3, 1), (seq.shape[0] - 2, 1), (seq.shape[0] - 4, 2), (seq.shape[0] - 2, 2), (seq.shape[0] - 4, 3), (seq.shape[0] - 3, 3), (seq.shape[0] - 2, 3)]:
            model.AddAllowedAssignments([seq[x, z, 1]], [(yoke_id,) for yoke_id in yoke_ids])
            model.AddAllowedAssignments([seq[x, z, 3]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # SE Corner Bottom and Top Layers
        for x, z in [(seq.shape[0] - 4, seq.shape[1] - 4), (seq.shape[0] - 3, seq.shape[1] - 4), (seq.shape[0] - 2, seq.shape[1] - 4), (seq.shape[0] - 4, seq.shape[1] - 3), (seq.shape[0] - 2, seq.shape[1] - 3), (seq.shape[0] - 4, seq.shape[1] - 2), (seq.shape[0] - 3, seq.shape[1] - 2), (seq.shape[0] - 2, seq.shape[1] - 2)]:
            model.AddAllowedAssignments([seq[x, z, 1]], [(yoke_id,) for yoke_id in yoke_ids])
            model.AddAllowedAssignments([seq[x, z, 3]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # NW Corner Middle Layer
        for x, z in [(1, 1), (1, 2), (1, 3), (2, 1), (3, 1), (3, 3)]:
            model.AddAllowedAssignments([seq[x, z, 2]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # NE Corner Middle Layer
        for x, z in [(1, seq.shape[1] - 4), (1, seq.shape[1] - 3), (1, seq.shape[1] - 2), (2, seq.shape[1] - 2), (3, seq.shape[1] - 4), (3, seq.shape[1] - 2)]:
            model.AddAllowedAssignments([seq[x, z, 2]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # SW Corner Middle Layer
        for x, z in [(seq.shape[0] - 4, 1), (seq.shape[0] - 3, 1), (seq.shape[0] - 2, 1), (seq.shape[0] - 2, 2), (seq.shape[0] - 4, 3), (seq.shape[0] - 2, 3)]:
            model.AddAllowedAssignments([seq[x, z, 2]], [(yoke_id,) for yoke_id in yoke_ids])
        
        # SE Corner Middle Layer
        for x, z in [(seq.shape[0] - 4, seq.shape[1] - 2), (seq.shape[0] - 3, seq.shape[1] - 2), (seq.shape[0] - 2, seq.shape[1] - 2), (seq.shape[0] - 2, seq.shape[1] - 3), (seq.shape[0] - 4, seq.shape[1] - 4), (seq.shape[0] - 2, seq.shape[1] - 4)]:
            model.AddAllowedAssignments([seq[x, z, 2]], [(yoke_id,) for yoke_id in yoke_ids])
