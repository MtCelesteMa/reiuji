"""Calculations specific to QMD's linear accelerator designer."""

from ... import core
from . import models

import uuid

from ortools.sat.python import cp_model


class TotalHeatingRate(core.calculations.Calculation):
    """Calculates the total heating rate of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        total_heating_rate = 0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], (models.Cavity, models.Magnet)):
                total_heating_rate += seq[x, 1, 2].heat
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

        heat_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            model.AddElement(seq[x, 1, 2], heating_rates, heat_contrib[x])
        
        total_heating_rate = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_heating_rate == sum(heat_contrib))
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


class TotalVoltage(core.calculations.Calculation):
    """Calculates the total voltage of a linear accelerator configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        total_voltage = 0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], models.Cavity):
                total_voltage += seq[x, 1, 2].voltage
        return total_voltage
    
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
        voltages = [component.voltage if isinstance(component, models.Cavity) else 0 for component in components]

        voltage_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            model.AddElement(seq[x, 1, 2], voltages, voltage_contrib[x])
        
        total_voltage = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(total_voltage == sum(voltage_contrib))
        return total_voltage


class BeamFocus(core.calculations.Calculation):
    def __init__(self, charge: float, beam_strength: int, scaling_factor: int = 10000, initial_focus: float = 0.0) -> None:
        self.charge = charge
        self.beam_strength = beam_strength
        self.scaling_factor = scaling_factor
        self.initial_focus = initial_focus
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[core.models.MultiblockComponent]) -> float:
        focus_loss = 0.0
        focus_gain = 0.0
        for x in range(seq.shape[0]):
            if isinstance(seq[x, 1, 2], models.Magnet):
                focus_gain += seq[x, 1, 2].strength * abs(self.charge)
            if isinstance(seq[x, 2, 2], models.Beam):
                focus_loss += seq[x, 2, 2].attenuation * (1 + abs(self.charge) * (self.beam_strength / self.scaling_factor) ** (1 / 2))
        return self.initial_focus + focus_gain - focus_loss
    
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
        strengths = [round(component.strength * core.scaled_calculations.SCALE_FACTOR) if isinstance(component, models.Magnet) else 0 for component in components]
        attenuations = [round(component.attenuation * core.scaled_calculations.SCALE_FACTOR) if isinstance(component, models.Beam) else 0 for component in components]
        charge = round(abs(self.charge) * core.scaled_calculations.SCALE_FACTOR)
        loss_factor = round((1 + abs(self.charge) * (self.beam_strength / self.scaling_factor) ** (1 / 2)) * core.scaled_calculations.SCALE_FACTOR)

        focus_gain_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        focus_loss_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(seq.shape[0])]
        for x in range(seq.shape[0]):
            strength_i = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[x, 1, 2], strengths, strength_i)
            core.scaled_calculations.multiply(model, focus_gain_contrib[x], charge, strength_i)

            attenuation_i = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[x, 2, 2], attenuations, attenuation_i)
            core.scaled_calculations.multiply(model, focus_loss_contrib[x], attenuation_i, loss_factor)
        
        focus_gain = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        focus_loss = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(focus_gain == sum(focus_gain_contrib))
        model.Add(focus_loss == sum(focus_loss_contrib))

        initial_focus = round(self.initial_focus * core.scaled_calculations.SCALE_FACTOR)   
        final_focus = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(final_focus == initial_focus + focus_gain - focus_loss)
        return final_focus