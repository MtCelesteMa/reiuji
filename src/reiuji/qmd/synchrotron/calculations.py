"""Calculations specific to designing QMD synchrotrons."""

from ... import core
from . import models

import uuid

from ortools.sat.python import cp_model


class TotalHeatingRate(core.calculations.Calculation):
    """Calculates the total heating rate of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        total_heating_rate = 0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], (models.Cavity, models.Magnet)):
                total_heating_rate += seq[2, z, 3].heat
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], (models.Cavity, models.Magnet)):
                total_heating_rate += seq[seq.shape[0] - 3, z, 3].heat
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], (models.Cavity, models.Magnet)):
                total_heating_rate += seq[x, 2, 3].heat
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], (models.Cavity, models.Magnet)):
                total_heating_rate += seq[x, seq.shape[1] - 3, 3].heat
        return total_heating_rate
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[core.models.MultiblockComponent]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        heating_rates = [component.heat if isinstance(component, (models.Cavity, models.Magnet)) else 0 for component in components]

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


class TotalCoolingRate(core.calculations.Calculation):
    """Calculates the total cooling rate of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        total_cooling_rate = 0
        for i, component in enumerate(seq):
            if isinstance(component, models.Cooler):
                total_cooling_rate += component.cooling
        return total_cooling_rate

    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[core.models.MultiblockComponent]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        cooling_rates = [component.cooling if isinstance(component, models.Cooler) else 0 for component in components]

        cool_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in seq]
        for i, component in enumerate(seq):
            model.AddElement(seq[i], cooling_rates, cool_contrib[i])

        total_cooling_rate = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_cooling_rate == sum(cool_contrib))

        return total_cooling_rate


class MaxDipoleEnergy(core.calculations.Calculation):
    def __init__(self, charge: float, radius: float, mass: float) -> None:
        self.charge = charge
        self.radius = radius
        self.mass = mass
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        dipole_strength = 0.0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], models.Magnet) and seq[1, z, 3].type == "yoke":
                dipole_strength += seq[2, z, 3].strength
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], models.Magnet) and seq[seq.shape[0] - 2, z, 3].type == "yoke":
                dipole_strength += seq[seq.shape[0] - 3, z, 3].strength
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], models.Magnet) and seq[x, 1, 3].type == "yoke":
                dipole_strength += seq[x, 2, 3].strength
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], models.Magnet) and seq[x, seq.shape[1] - 2, 3].type == "yoke":
                dipole_strength += seq[x, seq.shape[1] - 3, 3].strength
        return ((self.charge * self.radius * dipole_strength) ** 2) / (2 * self.mass) * 1000
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[core.models.MultiblockComponent]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        yoke_ids = type_to_id["yoke"]
        strengths = [round(component.strength * core.scaled_calculations.SCALE_FACTOR) if isinstance(component, models.Magnet) else 0 for component in components]

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
        core.scaled_calculations.multiply(model, total_strength_sq, total_strength, total_strength)

        mass = round(self.mass * 10)
        charge = round(self.charge ** 2 * 9)
        radius = round(self.radius ** 2 * 4)

        max_dipole_energy_ = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddMultiplicationEquality(max_dipole_energy_, [charge, radius, total_strength_sq, 10])
        max_dipole_energy__ = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddDivisionEquality(max_dipole_energy__, max_dipole_energy_, 2 * mass)

        max_dipole_energy = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddDivisionEquality(max_dipole_energy, max_dipole_energy__, 36)

        return max_dipole_energy


class MaxRadiationLoss(core.calculations.Calculation):
    def __init__(self, charge: float, radius: float, mass: float) -> None:
        self.charge = charge
        self.radius = radius
        self.mass = mass
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        total_voltage = 0
        # North side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[2, z, 3], models.Cavity):
                total_voltage += seq[2, z, 3].voltage
        # South side
        for z in range(2, seq.shape[1] - 2):
            if isinstance(seq[seq.shape[0] - 3, z, 3], models.Cavity):
                total_voltage += seq[seq.shape[0] - 3, z, 3].voltage
        # West side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, 2, 3], models.Cavity):
                total_voltage += seq[x, 2, 3].voltage
        # East side
        for x in range(4, seq.shape[0] - 4):
            if isinstance(seq[x, seq.shape[1] - 3, 3], models.Cavity):
                total_voltage += seq[x, seq.shape[1] - 3, 3].voltage
        
        return self.mass * (3 * total_voltage * self.radius / abs(self.charge)) ** (1 / 4) * 1000

    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[core.models.MultiblockComponent]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        voltages = [round(component.voltage * core.scaled_calculations.SCALE_FACTOR) if isinstance(component, models.Cavity) else 0 for component in components]

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
        core.scaled_calculations.sqrt(model, total_voltage_sqrt, total_voltage)

        total_voltage_4rt = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        core.scaled_calculations.sqrt(model, total_voltage_4rt, total_voltage_sqrt)

        mass = round(self.mass * 10)
        charge = round(abs(self.charge) ** (1 / 4) * 81)
        radius = round(self.radius ** (1 / 4) * 16)

        mvr_ = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddMultiplicationEquality(mvr_, [total_voltage_4rt, radius, 3, mass])
        mvr = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddDivisionEquality(mvr, mvr_, 160)

        mvr2 = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddMultiplicationEquality(mvr2, [mvr, 81])

        max_radiation_loss = model.NewIntVar(0, 2 ** 48 - 1, str(uuid.uuid4()))
        model.AddDivisionEquality(max_radiation_loss, mvr2, charge)

        return max_radiation_loss
