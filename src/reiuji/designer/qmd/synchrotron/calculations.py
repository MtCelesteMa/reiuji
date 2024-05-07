"""Calculations specific to designing QMD synchrotrons."""

from .... import core
from ....components.types import *
from ... import base

import uuid

from ortools.sat.python import cp_model


class TotalHeatingRate(base.calculations.Calculation):
    """Calculates the total heating rate of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        total_heating_rate = 0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], (RFCavity, AcceleratorMagnet)):
                total_heating_rate += seq[2, z, 3].heat
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], (RFCavity, AcceleratorMagnet)):
                total_heating_rate += seq[seq.shape[0] - 3, z, 3].heat
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], (RFCavity, AcceleratorMagnet)):
                total_heating_rate += seq[x, 2, 3].heat
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], (RFCavity, AcceleratorMagnet)):
                total_heating_rate += seq[x, seq.shape[1] - 3, 3].heat
        return total_heating_rate
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        heating_rates = [component.heat if isinstance(component, (RFCavity, AcceleratorMagnet)) else 0 for component in components]

        # North side
        heat_contrib_N = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddElement(seq[2, z, 3], heating_rates, heat_contrib_N[z - 2])
        
        # South side
        heat_contrib_S = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddElement(seq[seq.shape[0] - 3, z, 3], heating_rates, heat_contrib_S[z - 2])
        
        # West side
        heat_contrib_W = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddElement(seq[x, 2, 3], heating_rates, heat_contrib_W[x - 4])
        
        # East side
        heat_contrib_E = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddElement(seq[x, seq.shape[1] - 3, 3], heating_rates, heat_contrib_E[x - 4])
        
        total_heating_rate_N = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(heat_contrib_N) == total_heating_rate_N)
        total_heating_rate_S = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(heat_contrib_S) == total_heating_rate_S)
        total_heating_rate_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(heat_contrib_W) == total_heating_rate_W)
        total_heating_rate_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(heat_contrib_E) == total_heating_rate_E)

        total_heating_rate = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum([total_heating_rate_N, total_heating_rate_S, total_heating_rate_W, total_heating_rate_E]) == total_heating_rate)

        return total_heating_rate


class TotalCoolingRate(base.calculations.Calculation):
    """Calculates the total cooling rate of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        total_cooling_rate = 0
        for i, component in enumerate(seq):
            if isinstance(component, AcceleratorCooler):
                total_cooling_rate += component.cooling
        return total_cooling_rate

    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        cooling_rates = [component.cooling if isinstance(component, AcceleratorCooler) else 0 for component in components]

        cool_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in seq]
        for i, component in enumerate(seq):
            model.AddElement(seq[i], cooling_rates, cool_contrib[i])

        total_cooling_rate = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_cooling_rate == sum(cool_contrib))

        return total_cooling_rate


class MaxDipoleEnergy(base.calculations.Calculation):
    def __init__(self, charge: float, radius: float, mass: float) -> None:
        self.charge = charge
        self.radius = radius
        self.mass = mass
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        dipole_strength = 0.0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], AcceleratorMagnet) and seq[1, z, 3].type == "yoke":
                dipole_strength += seq[2, z, 3].strength
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], AcceleratorMagnet) and seq[seq.shape[0] - 2, z, 3].type == "yoke":
                dipole_strength += seq[seq.shape[0] - 3, z, 3].strength
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], AcceleratorMagnet) and seq[x, 1, 3].type == "yoke":
                dipole_strength += seq[x, 2, 3].strength
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], AcceleratorMagnet) and seq[x, seq.shape[1] - 2, 3].type == "yoke":
                dipole_strength += seq[x, seq.shape[1] - 3, 3].strength
        return ((self.charge * self.radius * dipole_strength) ** 2) / (2 * self.mass) * 1000
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        yoke_ids = type_to_id["yoke"]
        strengths = [round(component.strength * 10) if isinstance(component, AcceleratorMagnet) else 0 for component in components]

        # North side
        strength_contrib_N = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        is_dipole_N = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddAllowedAssignments([seq[1, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_N[z - 2])
            model.AddForbiddenAssignments([seq[1, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_N[z - 2].Not())
            model.AddElement(seq[2, z, 3], strengths, strength_contrib_N[z - 2])
        
        strength_contrib_N_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for i in range(seq.shape[1] - 4):
            model.AddMultiplicationEquality(strength_contrib_N_[i], is_dipole_N[i], strength_contrib_N[i])
        
        total_strength_N = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_N_) == total_strength_N)
        
        # South side
        strength_contrib_S = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        is_dipole_S = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddAllowedAssignments([seq[seq.shape[0] - 2, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_S[z - 2])
            model.AddForbiddenAssignments([seq[seq.shape[0] - 2, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_S[z - 2].Not())
            model.AddElement(seq[seq.shape[0] - 3, z, 3], strengths, strength_contrib_S[z - 2])
        
        strength_contrib_S_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for i in range(seq.shape[1] - 4):
            model.AddMultiplicationEquality(strength_contrib_S_[i], is_dipole_S[i], strength_contrib_S[i])
        
        total_strength_S = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_S_) == total_strength_S)
        
        # West side
        strength_contrib_W = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        is_dipole_W = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddAllowedAssignments([seq[x, 1, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_W[x - 4])
            model.AddForbiddenAssignments([seq[x, 1, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_W[x - 4].Not())
            model.AddElement(seq[x, 2, 3], strengths, strength_contrib_W[x - 4])
        
        strength_contrib_W_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for i in range(seq.shape[0] - 8):
            model.AddMultiplicationEquality(strength_contrib_W_[i], is_dipole_W[i], strength_contrib_W[i])
        
        total_strength_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_W_) == total_strength_W)
        
        # East side
        strength_contrib_E = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        is_dipole_E = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddAllowedAssignments([seq[x, seq.shape[1] - 2, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_E[x - 4])
            model.AddForbiddenAssignments([seq[x, seq.shape[1] - 2, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_E[x - 4].Not())
            model.AddElement(seq[x, seq.shape[1] - 3, 3], strengths, strength_contrib_E[x - 4])
        
        strength_contrib_E_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for i in range(seq.shape[0] - 8):
            model.AddMultiplicationEquality(strength_contrib_E_[i], is_dipole_E[i], strength_contrib_E[i])
        
        total_strength_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_E_) == total_strength_E)

        total_strength = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_strength == sum([total_strength_N, total_strength_S, total_strength_W, total_strength_E]))

        total_strength_sq = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        base.scaled_calculations.multiply(model, total_strength_sq, total_strength, total_strength, scale_factor=10)

        multiplier = (self.charge * self.radius) ** 2 / (2 * self.mass)
        multiplier = round(multiplier * base.scaled_calculations.SCALE_FACTOR)

        dipole_energy = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        base.scaled_calculations.multiply(model, dipole_energy, total_strength_sq, multiplier, max_value=2 ** 48 - 1, scale_factor=10)

        return dipole_energy


class MaxRadiationLoss(base.calculations.Calculation):
    def __init__(self, charge: float, radius: float, mass: float) -> None:
        self.charge = charge
        self.radius = radius
        self.mass = mass
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        total_voltage = 0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], RFCavity):
                total_voltage += seq[2, z, 3].voltage
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], RFCavity):
                total_voltage += seq[seq.shape[0] - 3, z, 3].voltage
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], RFCavity):
                total_voltage += seq[x, 2, 3].voltage
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], RFCavity):
                total_voltage += seq[x, seq.shape[1] - 3, 3].voltage
        
        return self.mass * (3 * total_voltage * self.radius / abs(self.charge)) ** (1 / 4) * 1000

    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        voltages = [component.voltage if isinstance(component, RFCavity) else 0 for component in components]

        # North side
        voltage_contrib_N = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddElement(seq[2, z, 3], voltages, voltage_contrib_N[z - 2])

        total_voltage_N = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(voltage_contrib_N) == total_voltage_N)
        
        # South side
        voltage_contrib_S = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddElement(seq[seq.shape[0] - 3, z, 3], voltages, voltage_contrib_S[z - 2])
        
        total_voltage_S = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(voltage_contrib_S) == total_voltage_S)
        
        # West side
        voltage_contrib_W = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddElement(seq[x, 2, 3], voltages, voltage_contrib_W[x - 4])
        
        total_voltage_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(voltage_contrib_W) == total_voltage_W)
        
        # East side
        voltage_contrib_E = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddElement(seq[x, seq.shape[1] - 3, 3], voltages, voltage_contrib_E[x - 4])
        
        total_voltage_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(voltage_contrib_E) == total_voltage_E)

        total_voltage = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum([total_voltage_N, total_voltage_S, total_voltage_W, total_voltage_E]) == total_voltage)

        total_voltage_sqrt = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        base.scaled_calculations.sqrt(model, total_voltage_sqrt, total_voltage, scale_factor=1)

        total_voltage_sqrt_ =  model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddMultiplicationEquality(total_voltage_sqrt_, total_voltage_sqrt, base.scaled_calculations.SCALE_FACTOR)

        total_voltage_4rt = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        base.scaled_calculations.sqrt(model, total_voltage_4rt, total_voltage_sqrt_)

        multiplier = self.mass * (3 * self.radius / abs(self.charge)) ** (1 / 4)
        multiplier = round(multiplier * base.scaled_calculations.SCALE_FACTOR)

        radiation_energy = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        base.scaled_calculations.multiply(model, radiation_energy, total_voltage_4rt, multiplier, max_value=2 ** 48 - 1)

        return radiation_energy


class BeamFocus(base.calculations.Calculation):
    def __init__(self, charge: float, beam_strength: int, scaling_factor: int = 10000, initial_focus: float = 0.0) -> None:
        self.charge = charge
        self.beam_strength = beam_strength
        self.scaling_factor = scaling_factor
        self.initial_focus = initial_focus
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        quadrupole_strength = 0.0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], AcceleratorMagnet) and seq[1, z, 3].type != "yoke":
                quadrupole_strength += seq[2, z, 3].strength
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], AcceleratorMagnet) and seq[seq.shape[0] - 2, z, 3].type != "yoke":
                quadrupole_strength += seq[seq.shape[0] - 3, z, 3].strength
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], AcceleratorMagnet) and seq[x, 1, 3].type != "yoke":
                quadrupole_strength += seq[x, 2, 3].strength
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], AcceleratorMagnet) and seq[x, seq.shape[1] - 2, 3].type != "yoke":
                quadrupole_strength += seq[x, seq.shape[1] - 3, 3].strength
        beams = (seq.shape[0] - 4) * 4 - 4
        focus_loss = beams * 0.02 * (1 + abs(self.charge) * (self.beam_strength / self.scaling_factor) ** (1 / 2))
        focus_gain = abs(self.charge) * quadrupole_strength
        return self.initial_focus + focus_gain - focus_loss
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        yoke_ids = type_to_id["yoke"]
        strengths = [round(component.strength * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, AcceleratorMagnet) else 0 for component in components]

        # North side
        strength_contrib_N = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        is_dipole_N = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddAllowedAssignments([seq[1, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_N[z - 2])
            model.AddForbiddenAssignments([seq[1, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_N[z - 2].Not())
            model.AddElement(seq[2, z, 3], strengths, strength_contrib_N[z - 2])
        
        strength_contrib_N_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for i in range(seq.shape[1] - 4):
            model.AddMultiplicationEquality(strength_contrib_N_[i], is_dipole_N[i].Not(), strength_contrib_N[i])
        
        total_strength_N = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_N_) == total_strength_N)
        
        # South side
        strength_contrib_S = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        is_dipole_S = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddAllowedAssignments([seq[seq.shape[0] - 2, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_S[z - 2])
            model.AddForbiddenAssignments([seq[seq.shape[0] - 2, z, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_S[z - 2].Not())
            model.AddElement(seq[seq.shape[0] - 3, z, 3], strengths, strength_contrib_S[z - 2])
        
        strength_contrib_S_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for i in range(seq.shape[1] - 4):
            model.AddMultiplicationEquality(strength_contrib_S_[i], is_dipole_S[i].Not(), strength_contrib_S[i])
        
        total_strength_S = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_S_) == total_strength_S)
        
        # West side
        strength_contrib_W = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        is_dipole_W = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddAllowedAssignments([seq[x, 1, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_W[x - 4])
            model.AddForbiddenAssignments([seq[x, 1, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_W[x - 4].Not())
            model.AddElement(seq[x, 2, 3], strengths, strength_contrib_W[x - 4])
        
        strength_contrib_W_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for i in range(seq.shape[0] - 8):
            model.AddMultiplicationEquality(strength_contrib_W_[i], is_dipole_W[i].Not(), strength_contrib_W[i])
        
        total_strength_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_W_) == total_strength_W)
        
        # East side
        strength_contrib_E = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        is_dipole_E = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddAllowedAssignments([seq[x, seq.shape[1] - 2, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_E[x - 4])
            model.AddForbiddenAssignments([seq[x, seq.shape[1] - 2, 3]], [(yoke_id,) for yoke_id in yoke_ids]).OnlyEnforceIf(is_dipole_E[x - 4].Not())
            model.AddElement(seq[x, seq.shape[1] - 3, 3], strengths, strength_contrib_E[x - 4])
        
        strength_contrib_E_ = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for i in range(seq.shape[0] - 8):
            model.AddMultiplicationEquality(strength_contrib_E_[i], is_dipole_E[i].Not(), strength_contrib_E[i])
        
        total_strength_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(strength_contrib_E_) == total_strength_E)

        total_strength = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_strength == sum([total_strength_N, total_strength_S, total_strength_W, total_strength_E]))

        beams = (seq.shape[0] - 4) * 4 - 4
        focus_loss = round(0.02 * (1 + abs(self.charge) * (self.beam_strength / self.scaling_factor) ** (1 / 2)) * base.scaled_calculations.SCALE_FACTOR) * beams

        focus_gain = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        base.scaled_calculations.multiply(model, focus_gain, total_strength, round(abs(self.charge) * base.scaled_calculations.SCALE_FACTOR))

        focus_delta = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(focus_delta == focus_gain - focus_loss)

        focus = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(focus == focus_delta + round(self.initial_focus * base.scaled_calculations.SCALE_FACTOR))

        return focus
    

class PowerRequirement(base.calculations.Calculation):
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        efficiency = 0.0
        parts = 0
        raw_power = 0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], (RFCavity, AcceleratorMagnet)):
                raw_power += seq[2, z, 3].power
                efficiency += seq[2, z, 3].efficiency
                parts += 1
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], (RFCavity, AcceleratorMagnet)):
                raw_power += seq[seq.shape[0] - 3, z, 3].power
                efficiency += seq[seq.shape[0] - 3, z, 3].efficiency
                parts += 1
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], (RFCavity, AcceleratorMagnet)):
                raw_power += seq[x, 2, 3].power
                efficiency += seq[x, 2, 3].efficiency
                parts += 1
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], (RFCavity, AcceleratorMagnet)):
                raw_power += seq[x, seq.shape[1] - 3, 3].power
                efficiency += seq[x, seq.shape[1] - 3, 3].efficiency
                parts += 1
        return raw_power / (efficiency / parts)
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        powers = [component.power if isinstance(component, (RFCavity, AcceleratorMagnet)) else 0 for component in components]
        efficiencies = [round(component.efficiency * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, (RFCavity, AcceleratorMagnet)) else 0 for component in components]
        is_part = [1 if isinstance(component, (RFCavity, AcceleratorMagnet)) else 0 for component in components]

        # North side
        raw_power_contrib_N = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        efficiency_contrib_N = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        is_part_N = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddElement(seq[2, z, 3], powers, raw_power_contrib_N[z - 2])
            model.AddElement(seq[2, z, 3], efficiencies, efficiency_contrib_N[z - 2])
            model.AddElement(seq[2, z, 3], is_part, is_part_N[z - 2])
        
        raw_power_N = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        efficiency_N = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        parts_N = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(raw_power_N == sum(raw_power_contrib_N))
        model.Add(efficiency_N == sum(efficiency_contrib_N))
        model.Add(parts_N == sum(is_part_N))

        # South side
        raw_power_contrib_S = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        efficiency_contrib_S = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        is_part_S = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddElement(seq[seq.shape[0] - 3, z, 3], powers, raw_power_contrib_S[z - 2])
            model.AddElement(seq[seq.shape[0] - 3, z, 3], efficiencies, efficiency_contrib_S[z - 2])
            model.AddElement(seq[seq.shape[0] - 3, z, 3], is_part, is_part_S[z - 2])
        
        raw_power_S = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        efficiency_S = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        parts_S = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(raw_power_S == sum(raw_power_contrib_S))
        model.Add(efficiency_S == sum(efficiency_contrib_S))
        model.Add(parts_S == sum(is_part_S))

        # West side
        raw_power_contrib_W = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        efficiency_contrib_W = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        is_part_W = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddElement(seq[x, 2, 3], powers, raw_power_contrib_W[x - 4])
            model.AddElement(seq[x, 2, 3], efficiencies, efficiency_contrib_W[x - 4])
            model.AddElement(seq[x, 2, 3], is_part, is_part_W[x - 4])
        
        raw_power_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        efficiency_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        parts_W = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(raw_power_W == sum(raw_power_contrib_W))
        model.Add(efficiency_W == sum(efficiency_contrib_W))
        model.Add(parts_W == sum(is_part_W))

        # East side
        raw_power_contrib_E = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        efficiency_contrib_E = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        is_part_E = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddElement(seq[x, seq.shape[1] - 3, 3], powers, raw_power_contrib_E[x - 4])
            model.AddElement(seq[x, seq.shape[1] - 3, 3], efficiencies, efficiency_contrib_E[x - 4])
            model.AddElement(seq[x, seq.shape[1] - 3, 3], is_part, is_part_E[x - 4])
        
        raw_power_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        efficiency_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        parts_E = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(raw_power_E == sum(raw_power_contrib_E))
        model.Add(efficiency_E == sum(efficiency_contrib_E))
        model.Add(parts_E == sum(is_part_E))
        
        raw_power = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        efficiency = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        parts = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(raw_power == sum([raw_power_N, raw_power_S, raw_power_W, raw_power_E]))
        model.Add(efficiency == sum([efficiency_N, efficiency_S, efficiency_W, efficiency_E]))
        model.Add(parts == sum([parts_N, parts_S, parts_W, parts_E]))

        reduced_efficiency = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(reduced_efficiency, efficiency, parts)

        raw_power_ = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddMultiplicationEquality(raw_power_, raw_power, base.scaled_calculations.SCALE_FACTOR)

        power_requirement = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(power_requirement, raw_power_, reduced_efficiency)

        return power_requirement

