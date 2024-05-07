"""Calculations specific to NuclearCraft: Overhauled's turbine dynamo designer."""

from .... import core
from ....components.types import *
from ... import base

import uuid

from ortools.sat.python import cp_model


class TurbineDynamoConductivity(base.calculations.Calculation):
    """Calculates the conductivity of a turbine dynamo configuration."""
    def __call__(self, seq: core.multi_sequence.MultiSequence[Component]) -> float:
        coil_count = 0
        bearing_count = 0
        total_conductivity = 0.0
        for component in seq:
            if isinstance(component, DynamoCoil):
                coil_count += 1
                total_conductivity += component.conductivity
            if component.type == "bearing":
                bearing_count += 1
        if coil_count == 0:
            return 0.0
        return total_conductivity / max(bearing_count / 2, coil_count)
    
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
        conductivities = [round(component.conductivity * base.scaled_calculations.SCALE_FACTOR) if isinstance(component, DynamoCoil) else 0 for component in components]
        
        is_coil = [model.NewBoolVar(str(uuid.uuid4())) for _ in seq]
        is_bearing = [model.NewBoolVar(str(uuid.uuid4())) for _ in seq]
        for i, component in enumerate(seq):
            model.AddAllowedAssignments([seq[i]], [(coil_id,) for coil_id in type_to_id["coil"]]).OnlyEnforceIf(is_coil[i])
            model.AddForbiddenAssignments([seq[i]], [(coil_id,) for coil_id in type_to_id["coil"]]).OnlyEnforceIf(is_coil[i].Not())
            model.AddAllowedAssignments([seq[i]], [(bearing_id,) for bearing_id in type_to_id["bearing"]]).OnlyEnforceIf(is_bearing[i])
            model.AddForbiddenAssignments([seq[i]], [(bearing_id,) for bearing_id in type_to_id["bearing"]]).OnlyEnforceIf(is_bearing[i].Not())
        
        conductivity_contrib = [model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4())) for _ in seq]
        for i, component in enumerate(seq):
            model.AddElement(seq[i], conductivities, conductivity_contrib[i])
        
        coil_count = model.NewIntVar(0, len(seq), str(uuid.uuid4()))
        bearing_count = model.NewIntVar(0, len(seq), str(uuid.uuid4()))
        total_conductivity = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.Add(coil_count == sum(is_coil))
        model.Add(bearing_count == sum(is_bearing))
        model.Add(total_conductivity == sum(conductivity_contrib))

        coil_count_float = model.NewIntVar(0, len(seq) * base.scaled_calculations.SCALE_FACTOR, str(uuid.uuid4()))
        model.AddMultiplicationEquality(coil_count_float, coil_count, base.scaled_calculations.SCALE_FACTOR)
        bearing_count_float = model.NewIntVar(0, len(seq) * base.scaled_calculations.SCALE_FACTOR, str(uuid.uuid4()))
        model.AddMultiplicationEquality(bearing_count_float, bearing_count, base.scaled_calculations.SCALE_FACTOR)
        reduced_bearing_count_float = model.NewIntVar(0, len(seq) * base.scaled_calculations.SCALE_FACTOR, str(uuid.uuid4()))
        model.AddDivisionEquality(reduced_bearing_count_float, bearing_count_float, 2)

        more_coils = model.NewBoolVar(str(uuid.uuid4()))
        model.Add(coil_count_float >= reduced_bearing_count_float).OnlyEnforceIf(more_coils)
        model.Add(coil_count_float < reduced_bearing_count_float).OnlyEnforceIf(more_coils.Not())
        reducing_factor = model.NewIntVar(50, len(seq) * base.scaled_calculations.SCALE_FACTOR, str(uuid.uuid4()))
        model.Add(reducing_factor == coil_count_float).OnlyEnforceIf(more_coils)
        model.Add(reducing_factor == reduced_bearing_count_float).OnlyEnforceIf(more_coils.Not())

        total_conductivity_ = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddMultiplicationEquality(total_conductivity_, total_conductivity, base.scaled_calculations.SCALE_FACTOR)

        reduced_conductivity = model.NewIntVar(0, cp_model.INT32_MAX, str(uuid.uuid4()))
        model.AddDivisionEquality(reduced_conductivity, total_conductivity_, reducing_factor)

        return reduced_conductivity
