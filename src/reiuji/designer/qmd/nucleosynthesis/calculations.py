"""Calculations specific to the QMD nucleosynthesis chamber designer."""

from .... import core
from ....components.types import *
from ... import base

import uuid

from ortools.sat.python import cp_model


class TotalHeatingRate(base.calculations.Calculation):
    """Calculates the total heating rate of a nucleosynthesis chamber."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        raise NotImplementedError("TotalHeatingRate.__call__ is not implemented.")

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
        heating_rates = [component.heat if isinstance(component, (NucleosynthesisBeam, PlasmaGlass, PlasmaNozzle)) else 0 for component in components]

        heat_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(len(seq))]
        for i, component in enumerate(seq):
            model.AddElement(component, heating_rates, heat_contrib[i])
        
        total_heating = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(heat_contrib) == total_heating)
        return total_heating


class TotalCoolingRate(base.calculations.Calculation):
    """Calculates the total cooling rate of a nucleosynthesis chamber."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        raise NotImplementedError("TotalCoolingRate.__call__ is not implemented.")

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
        cooling_rates = [component.cooling if isinstance(component, NucleosynthesisHeater) else 0 for component in components]

        cooling_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in range(len(seq))]
        for i, component in enumerate(seq):
            model.AddElement(component, cooling_rates, cooling_contrib[i])
        
        total_cooling = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(sum(cooling_contrib) == total_cooling)
        return total_cooling
