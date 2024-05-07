"""Constraints specific to the QMD decelerator designer."""

from .... import core
from ....components.types import *
from ... import base
from .. import synchrotron

import uuid

from ortools.sat.python import cp_model


class EnergyConstraint(base.constraints.Constraint):
    """Ensures that the maximum acceptable energy is greater than a given value."""
    def __init__(self, minimum_energy: int, maximum_energy: int, charge: float, radius: float, mass: float) -> None:
        self.minimum_energy = minimum_energy
        self.maximum_energy = maximum_energy
        self.charge = charge
        self.radius = radius
        self.mass = mass
    
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("EnergyConstraint.is_satisfied is not implemented.")

    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        dipole_energy = synchrotron.calculations.MaxDipoleEnergy(self.charge, self.radius, self.mass).to_model(model, seq, components)
        model.Add(dipole_energy >= self.minimum_energy)
        model.Add(dipole_energy <= self.maximum_energy)


class OneCavityConstraint(base.constraints.Constraint):
    """Ensures that only one cavity is present in the structure."""
    def is_satisfied(self, seq: core.multi_sequence.MultiSequence[Component]) -> bool:
        raise NotImplementedError("EnergyConstraint.is_satisfied is not implemented.")

    def to_model(
        self,
        model: cp_model.CpModel,
        seq: core.multi_sequence.MultiSequence[cp_model.IntVar],
        components: list[Component]
    ) -> None:
        type_to_id = dict()
        for i, component in enumerate(components):
            if component.type not in type_to_id:
                type_to_id[component.type] = [i]
            else:
                type_to_id[component.type].append(i)
        cavity_ids = type_to_id["cavity"]

        # North cavity
        has_cavity_N = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddAllowedAssignments([seq[2, z, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_N[z - 2])
            model.AddForbiddenAssignments([seq[2, z, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_N[z - 2].Not())
        
        n_cavities_N = model.NewIntVar(0, seq.shape[1] - 4, str(uuid.uuid4()))
        model.Add(n_cavities_N == sum(has_cavity_N))

        # South cavity
        has_cavity_S = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 4)]
        for z in range(2, seq.shape[1] - 2):
            model.AddAllowedAssignments([seq[seq.shape[0] - 3, z, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_S[z - 2])
            model.AddForbiddenAssignments([seq[seq.shape[0] - 3, z, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_S[z - 2].Not())
        
        n_cavities_S = model.NewIntVar(0, seq.shape[1] - 4, str(uuid.uuid4()))
        model.Add(n_cavities_S == sum(has_cavity_S))

        # West cavity
        has_cavity_W = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddAllowedAssignments([seq[x, 2, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_W[x - 4])
            model.AddForbiddenAssignments([seq[x, 2, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_W[x - 4].Not())
        
        n_cavities_W = model.NewIntVar(0, seq.shape[0] - 8, str(uuid.uuid4()))
        model.Add(n_cavities_W == sum(has_cavity_W))

        # East cavity
        has_cavity_E = [model.NewBoolVar(str(uuid.uuid4())) for _ in range(seq.shape[1] - 8)]
        for x in range(4, seq.shape[0] - 4):
            model.AddAllowedAssignments([seq[x, seq.shape[1] - 3, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_E[x - 4])
            model.AddForbiddenAssignments([seq[x, seq.shape[1] - 3, 3]], [(cavity_id,) for cavity_id in cavity_ids]).OnlyEnforceIf(has_cavity_E[x - 4].Not())
        
        n_cavities_E = model.NewIntVar(0, seq.shape[0] - 8, str(uuid.uuid4()))
        model.Add(n_cavities_E == sum(has_cavity_E))

        model.Add(sum([n_cavities_N, n_cavities_S, n_cavities_W, n_cavities_E]) == 1)

