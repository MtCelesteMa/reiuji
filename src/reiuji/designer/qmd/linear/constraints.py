"""Constraints specific to QMD's linear accelerator designer."""

from .... import core
from ....components.types import *
from ... import base
from . import calculations

import uuid
import itertools

from ortools.sat.python import cp_model


class BeamConstraint(base.constraints.Constraint):
    """Ensures that the beam is at the center of the sequence. Note that the accelerator goes in the +x direction."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        if seq.shape[1] != 5 or seq.shape[2] != 5:
            raise ValueError("BeamConstraint requires a Nx5x5 sequence.")
        for x in range(1, seq.shape[0] - 1):
            for y in range(seq.shape[1]):
                for z in range(seq.shape[2]):
                    if y == z == 2 and seq[x, y, z].type != "beam":
                        return False
                    elif (y != 2 or z != 2) and seq[x, y, z].type == "beam":
                        return False
        return True
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        if seq.shape[1] != 5 or seq.shape[2] != 5:
            raise ValueError("BeamConstraint requires a Nx5x5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        beam_ids = type_to_id["beam"]
        for x in range(1, seq.shape[0] - 1):
            for y in range(seq.shape[1]):
                for z in range(seq.shape[2]):
                    if y == z == 2:
                        model.AddAllowedAssignments([seq[x, y, z]], [(beam_id,) for beam_id in beam_ids])
                    else:
                        model.AddForbiddenAssignments([seq[x, y, z]], [(beam_id,) for beam_id in beam_ids])


class CavityConstraint(base.constraints.Constraint):
    """Ensures that cavities are correctly placed."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("CavityConstraint.is_satisfied is not implemented.")
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        if seq.shape[1] != 5 or seq.shape[2] != 5:
            raise ValueError("CavityConstraint requires a Nx5x5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        cavity_ids = type_to_id["cavity"]
        has_cavity = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(1, seq.shape[0] - 1):
            cavity_positions = [
                seq[x, 1, 1],
                seq[x, 1, 2],
                seq[x, 1, 3],
                seq[x, 2, 1],
                seq[x, 2, 3],
                seq[x, 3, 1],
                seq[x, 3, 2],
                seq[x, 3, 3]
            ]
            for pos in cavity_positions:
                model.AddAllowedAssignments([pos], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity[x])
                model.AddForbiddenAssignments([pos], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity[x].Not())
            for a, b in itertools.combinations(cavity_positions, 2):
                model.Add(a == b).OnlyEnforceIf(has_cavity[x])
            model.AddImplication(has_cavity[x], has_cavity[x - 1].Not())
            model.AddImplication(has_cavity[x], has_cavity[x + 1].Not())


class MagnetConstraint(base.constraints.Constraint):
    """Ensures that magnets are correctly placed."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("CavityConstraint.is_satisfied is not implemented.")
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        if seq.shape[1] != 5 or seq.shape[2] != 5:
            raise ValueError("MagnetConstraint requires a Nx5x5 sequence.")
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        magnet_ids = type_to_id["magnet"]
        has_magnet = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(1, seq.shape[0] - 1):
            magnet_positions = [
                seq[x, 1, 2],
                seq[x, 2, 1],
                seq[x, 2, 3],
                seq[x, 3, 2],
            ]
            for pos in magnet_positions:
                model.AddAllowedAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet[x])
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids]).OnlyEnforceIf(has_magnet[x].Not())
            for a, b in itertools.combinations(magnet_positions, 2):
                model.Add(a == b).OnlyEnforceIf(has_magnet[x])
            forbidden_magnet_positions = [
                seq[x, 1, 1],
                seq[x, 1, 3],
                seq[x, 3, 1],
                seq[x, 3, 3]
            ]
            for pos in forbidden_magnet_positions:
                model.AddForbiddenAssignments([pos], [(magnet_id,) for magnet_id in magnet_ids])


class HeatNeutralConstraint(base.constraints.Constraint):
    """Ensures that the cooling rate is equal to or greater than the heating rate."""
    def __init__(self, external_heating: int) -> None:
        self.external_heating = external_heating
    
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("HeatNeutralConstraint.is_satisfied is not implemented.")
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        heating_rate = calculations.TotalHeatingRate().to_model(model, seq, components)
        cooling_rate = calculations.TotalCoolingRate().to_model(model, seq, components)
        model.Add(heating_rate + self.external_heating <= cooling_rate)


class BeamFocusConstraint(base.constraints.Constraint):
    """Ensures that the beam exits with a focus greater than a desired value."""
    def __init__(self, target_focus: float, charge: float, beam_strength: int, scaling_factor: int = 10000, initial_focus: float = 0.0) -> None:
        self.target_focus = target_focus
        self.charge = charge
        self.beam_strength = beam_strength
        self.scaling_factor = scaling_factor
        self.initial_focus = initial_focus
    
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("BeamFocusConstraint.is_satisfied is not implemented.")
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        target_focus = round(self.target_focus * base.scaled_calculations.SCALE_FACTOR)
        focus = calculations.BeamFocus(self.charge, self.beam_strength, self.scaling_factor, self.initial_focus).to_model(model, seq, components)
        model.Add(focus >= target_focus)


class EnergyConstraint(base.constraints.Constraint):
    """Ensures that the beam exists with an energy greater than a desired value."""
    def __init__(self, minimum_energy: int, maximum_energy: int, charge: float) -> None:
        self.minimum_energy = minimum_energy
        self.maximum_energy = maximum_energy
        self.charge = charge
    
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("EnergyConstraint.is_satisfied is not implemented.")
    
    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        charge = round(self.charge * 3)
        voltage = calculations.TotalVoltage().to_model(model, seq, components)
        energy_ = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddMultiplicationEquality(energy_, [voltage, charge])
        energy = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(energy, energy_, 3)
        model.Add(energy >= self.minimum_energy)
        model.Add(energy <= self.maximum_energy)
