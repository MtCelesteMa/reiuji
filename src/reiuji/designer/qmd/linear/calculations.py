"""Calculations specific to QMD's linear accelerator designer."""

from .... import core
from ....components.types import *
from ... import base

import uuid

from ortools.sat.python import cp_model


class TotalHeatingRate(base.calculations.Calculation):
    """Calculates the total heating rate of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        total_heating_rate = 0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], (RFCavity, AcceleratorMagnet)):
                total_heating_rate += seq[x, 1, 2].heat
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

        heat_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            model.AddElement(seq[x, 1, 2], heating_rates, heat_contrib[x])
        
        total_heating_rate = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_heating_rate == sum(heat_contrib))
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


class TotalVoltage(base.calculations.Calculation):
    """Calculates the total voltage of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        total_voltage = 0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], RFCavity):
                total_voltage += seq[x, 1, 2].voltage
        return total_voltage
    
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

        voltage_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            model.AddElement(seq[x, 1, 2], voltages, voltage_contrib[x])
        
        total_voltage = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_voltage == sum(voltage_contrib))
        return total_voltage


class BeamFocus(base.calculations.Calculation):
    def __init__(self, charge: float, beam_strength: int, scaling_factor: int = 10000, initial_focus: float = 0.0) -> None:
        self.charge = charge
        self.beam_strength = beam_strength
        self.scaling_factor = scaling_factor
        self.initial_focus = initial_focus
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        focus_loss = 0.0
        focus_gain = 0.0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], AcceleratorMagnet):
                focus_gain += seq[x, 1, 2].strength * abs(self.charge)
            if isinstance(seq[x, 2, 2], BeamPipe):
                focus_loss += seq[x, 2, 2].attenuation * (1 + abs(self.charge) * (self.beam_strength / self.scaling_factor) ** (1 / 2))
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
        strengths = [round(component.strength * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, AcceleratorMagnet) else 0 for component in components]
        attenuations = [round(component.attenuation * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, BeamPipe) else 0 for component in components]
        charge = round(abs(self.charge) * base.scaled_calculations.SCALE_FACTOR)
        loss_factor = round((1 + abs(self.charge) * (self.beam_strength / self.scaling_factor) ** (1 / 2)) * base.scaled_calculations.SCALE_FACTOR)

        focus_gain_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        focus_loss_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            strength_i = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[x, 1, 2], strengths, strength_i)
            base.scaled_calculations.multiply(model, focus_gain_contrib[x], charge, strength_i)

            attenuation_i = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[x, 2, 2], attenuations, attenuation_i)
            base.scaled_calculations.multiply(model, focus_loss_contrib[x], attenuation_i, loss_factor)
        
        focus_gain = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        focus_loss = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(focus_gain == sum(focus_gain_contrib))
        model.Add(focus_loss == sum(focus_loss_contrib))

        initial_focus = round(self.initial_focus * base.scaled_calculations.SCALE_FACTOR)   
        final_focus = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(final_focus == initial_focus + focus_gain - focus_loss)
        return final_focus


class PowerRequirement(base.calculations.Calculation):
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        efficiency = 0.0
        parts = 0
        raw_power = 0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], (RFCavity, AcceleratorMagnet)):
                raw_power += seq[x, 1, 2].power
                efficiency += seq[x, 1, 2].efficiency
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

        raw_power_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        efficiency_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        is_part_ = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            model.AddElement(seq[x, 1, 2], powers, raw_power_contrib[x])
            model.AddElement(seq[x, 1, 2], efficiencies, efficiency_contrib[x])
            model.AddElement(seq[x, 1, 2], is_part, is_part_[x])
        
        raw_power = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        efficiency = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        parts = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(raw_power == sum(raw_power_contrib))
        model.Add(efficiency == sum(efficiency_contrib))
        model.Add(parts == sum(is_part_))

        reduced_efficiency = model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(reduced_efficiency, efficiency, parts)

        raw_power_ = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddMultiplicationEquality(raw_power_, raw_power, base.scaled_calculations.SCALE_FACTOR)

        power_requirement = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(power_requirement, raw_power_, reduced_efficiency)

        return power_requirement
