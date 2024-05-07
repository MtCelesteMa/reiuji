"""Calculations specific to NuclearCraft: Overhauled's turbine rotor designer."""

from .... import core
from ....components.types import *
from ... import base

import uuid

from ortools.sat.python import cp_model


class TurbineRotorExpansion(base.calculations.SequenceCalculation):
    """Calculates the expansion of a turbine rotor configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> list[float]:
        total_expansion_level = 1.0
        expansion_levels = []
        for component in seq:
            if isinstance(component, (RotorBlade, RotorStator)):
                expansion_levels.append(total_expansion_level * component.expansion ** (1 / 2))
                total_expansion_level *= component.expansion
        return expansion_levels
    
    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> list[cp_model.IntVar]:
        expansions = [round(component.expansion * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, (RotorBlade, RotorStator)) else 1 * base.scaled_calculations.SCALE_FACTOR for component in components]
        expansions_sqrt = [round(component.expansion ** (1 / 2) * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, (RotorBlade, RotorStator)) else 1 * base.scaled_calculations.SCALE_FACTOR for component in components]

        expansion_levels = [model.NewIntVar(1, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in seq]
        total_expansion_level = 1 * base.scaled_calculations.SCALE_FACTOR
        for i, expansion_level in enumerate(expansion_levels):
            expansion = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[i], expansions, expansion)
            expansion_sqrt = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[i], expansions_sqrt, expansion_sqrt)

            base.scaled_calculations.multiply(model, expansion_level, total_expansion_level, expansion_sqrt)
            total_expansion_level_ = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            base.scaled_calculations.multiply(model, total_expansion_level_, total_expansion_level, expansion)
            total_expansion_level = total_expansion_level_
        return expansion_levels


class TurbineRotorEfficiency(base.calculations.Calculation):
    """Calculates the efficiency of a turbine rotor configuration."""
    def __init__(self, optimal_expansion: float) -> None:
        self.optimal_expansion = optimal_expansion
    
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        efficiency = 0.0
        n_blades = 0
        expansions = TurbineRotorExpansion()(seq)
        for i, component in enumerate(seq):
            ideal_expansion = self.optimal_expansion ** ((i + 0.5) / len(seq))
            if isinstance(component, RotorBlade):
                n_blades += 1
                efficiency += component.efficiency * min(ideal_expansion / expansions[i], expansions[i] / ideal_expansion)
        return efficiency / n_blades

    def to_model(
            self,
            model: cp_model.CpModel,
            seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
            components: list[Component]
    ) -> cp_model.IntVar:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] =  [i]
            else:
                type_to_id[component.type].append(i)
        efficiencies = [round(component.efficiency * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, RotorBlade) else 0 for component in components]
        expansions = TurbineRotorExpansion().to_model(model, seq, components)
        
        is_blade = [model.NewBoolVar(str(uuid.uuid4())) for _ in seq]
        for i, component in enumerate(seq):
            model.AddAllowedAssignments([seq[i]], [(blade_id,) for blade_id in type_to_id["blade"]]).OnlyEnforceIf(is_blade[i])
            model.AddForbiddenAssignments([seq[i]], [(blade_id,) for blade_id in type_to_id["blade"]]).OnlyEnforceIf(is_blade[i].Not())
        
        efficiency = 0
        for i, component in enumerate(seq):
            ideal_expansion = round(self.optimal_expansion ** ((i + 0.5) / len(seq)) * base.scaled_calculations.SCALE_FACTOR)
            raw_efficiency = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddElement(seq[i], efficiencies, raw_efficiency)

            multiplier_a = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            base.scaled_calculations.divide(model, multiplier_a, ideal_expansion, expansions[i])
            multiplier_b = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            base.scaled_calculations.divide(model, multiplier_b, expansions[i], ideal_expansion)
            multiplier = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.AddMinEquality(multiplier, [multiplier_a, multiplier_b])

            effective_efficiency = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            base.scaled_calculations.multiply(model, effective_efficiency, raw_efficiency, multiplier)

            efficiency_ = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
            model.Add(efficiency_ == efficiency + effective_efficiency).OnlyEnforceIf(is_blade[i])
            model.Add(efficiency_ == efficiency).OnlyEnforceIf(is_blade[i].Not())
            efficiency = efficiency_
        
        n_blades = model.NewIntVar(1, len(seq), str(uuid.uuid4()))
        model.Add(n_blades == sum(is_blade))

        final_efficiency = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(final_efficiency, efficiency, n_blades)
        return final_efficiency

