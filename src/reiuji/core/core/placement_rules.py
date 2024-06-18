"""Core placement rule classes."""

import enum
import itertools
import typing
import uuid
from abc import ABC, abstractmethod

import pydantic
from ortools.sat.python import cp_model
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import PlainValidator

from .. import utils

# Base classes


class Neighbor(pydantic.BaseModel):
    name: str
    type: str
    active: bool = pydantic.Field(default=False)


class CPNeighbor(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: cp_model.IntVar
    active: cp_model.IntVar


class BasePlacementRule(utils.registered_model.RegisteredModel, ABC):
    @abstractmethod
    def is_satisfied(self, neighbors: list[Neighbor]) -> bool: ...

    @abstractmethod
    def to_cp_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[CPNeighbor],
        mapping: list[tuple[str, str]],
        target: cp_model.IntVar,
    ) -> None: ...


PlacementRule = typing.Annotated[
    BasePlacementRule,
    PlainValidator(utils.registered_model.model_validate(BasePlacementRule)),
    PlainSerializer(utils.registered_model.model_dump(BasePlacementRule)),
]

# Core classes


class CountType(enum.StrEnum):
    AT_LEAST = "AT_LEAST"
    EXACTLY = "EXACTLY"
    AT_MOST = "AT_MOST"


class AdjacencyType(enum.StrEnum):
    STANDARD = "STANDARD"
    AXIAL = "AXIAL"
    VERTEX = "VERTEX"
    EDGE = "EDGE"


class AdjacencyPlacementRule(BasePlacementRule, reg_key="core.adjacent"):
    req_name: str
    req_type: str | None = pydantic.Field(default=None)
    amount: int
    count_type: CountType = pydantic.Field(default=CountType.AT_LEAST)
    adjacency_type: AdjacencyType = pydantic.Field(default=AdjacencyType.STANDARD)

    @pydantic.model_validator(mode="after")
    def check_rule(self) -> typing.Self:
        if self.amount > 6:
            raise ValueError(
                "Adjacency placement rules cannot require more than 6 adjacencies."
            )
        if self.amount < 0:
            raise ValueError(
                "Adjacency placement rules cannot require less than 0 adjacencies."
            )
        if self.amount == 0 and self.count_type != CountType.EXACTLY:
            raise ValueError(
                "Adjacency placement rules cannot require 0 adjacencies unless it is an exact rule."
            )
        if self.adjacency_type == AdjacencyType.AXIAL and self.amount % 2 != 0:
            raise ValueError(
                "Axial adjacency placement rules must have an even number of adjacencies."
            )
        if self.adjacency_type == AdjacencyType.VERTEX:
            if self.amount != 3:
                raise ValueError(
                    "Vertex adjacency placement rules must require 3 adjacencies."
                )
            if self.count_type == CountType.AT_MOST:
                raise ValueError(
                    "Vertex adjacency placement rules cannot be an 'at most' rule."
                )
        if self.adjacency_type == AdjacencyType.EDGE:
            if self.amount != 2:
                raise ValueError(
                    "Edge adjacency placmenet rules must require 2 adjacencies."
                )
            if self.count_type == CountType.AT_MOST:
                raise ValueError(
                    "Edge adjacency placement rules cannot be an 'at most' rule."
                )
        return self

    def is_satisfied(self, neighbors: list[Neighbor]) -> bool:
        if len(neighbors) % 2 != 0:
            raise ValueError("The number of neighbors must be even.")
        matches = [
            neighbor.name == self.req_name
            and (
                isinstance(self.req_type, type(None)) or neighbor.type == self.req_type
            )
            and neighbor.active
            for neighbor in neighbors
        ]

        if self.adjacency_type == AdjacencyType.STANDARD:
            if self.count_type == CountType.AT_LEAST:
                return sum(matches) >= self.amount
            elif self.count_type == CountType.EXACTLY:
                return sum(matches) == self.amount
            elif self.count_type == CountType.AT_MOST:
                return sum(matches) <= self.amount
        elif self.adjacency_type == AdjacencyType.AXIAL:
            axials = [pos and neg for pos, neg in itertools.batched(matches, 2)]
            if self.count_type == CountType.AT_LEAST:
                return sum(axials) >= self.amount // 2
            if self.count_type == CountType.EXACTLY:
                return sum(axials) == self.amount // 2
            if self.count_type == CountType.AT_MOST:
                return sum(axials) <= self.amount // 2
        elif self.adjacency_type == AdjacencyType.VERTEX:
            if len(neighbors) == 6:
                vertices = [
                    matches[a] and matches[b] and matches[c]
                    for a, b, c in [
                        (0, 2, 4),
                        (0, 2, 5),
                        (0, 3, 4),
                        (0, 3, 5),
                        (1, 2, 4),
                        (1, 2, 5),
                        (1, 3, 4),
                        (1, 3, 5),
                    ]
                ]
            else:
                raise ValueError("Vertex placement rules require exactly 3 dimensions.")
            if self.count_type == CountType.AT_LEAST:
                return any(vertices) and sum(matches) >= self.amount
            elif self.count_type == CountType.EXACTLY:
                return any(vertices) and sum(matches) == self.amount
        elif self.adjacency_type == AdjacencyType.EDGE:
            if len(neighbors) == 4:
                edges = [
                    matches[a] and matches[b]
                    for a, b in [(0, 2), (0, 3), (1, 2), (1, 3)]
                ]
            elif len(neighbors) == 6:
                edges = [
                    matches[a] and matches[b]
                    for a, b in [
                        (0, 2),
                        (0, 3),
                        (0, 4),
                        (0, 5),
                        (1, 2),
                        (1, 3),
                        (1, 4),
                        (1, 5),
                        (2, 4),
                        (2, 5),
                        (3, 4),
                        (3, 5),
                    ]
                ]
            else:
                raise ValueError(
                    "Edge placement rules require either 2 or 3 dimensions."
                )
            if self.count_type == CountType.AT_LEAST:
                return any(edges) and sum(matches) >= self.amount
            elif self.count_type == CountType.EXACTLY:
                return any(edges) and sum(matches) == self.amount
        raise RuntimeError("Internal Error!")

    def to_cp_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[CPNeighbor],
        mapping: list[tuple[str, str]],
        target: cp_model.IntVar,
    ) -> None:
        if len(neighbors) % 2 != 0:
            raise ValueError("The number of neighbors must be even.")
        allowed_ids = [
            i
            for i, (name, type_) in enumerate(mapping)
            if name == self.req_name
            and (isinstance(self.req_type, type(None)) or type_ == self.req_type)
        ]
        matches = [model.new_bool_var(str(uuid.uuid4())) for _ in neighbors]
        for neighbor, match in zip(neighbors, matches):
            id_match = model.new_bool_var(str(uuid.uuid4()))
            model.add_allowed_assignments(
                (neighbor.id,), [(i,) for i in allowed_ids]
            ).only_enforce_if(id_match)
            model.add_forbidden_assignments(
                (neighbor.id,), [(i,) for i in allowed_ids]
            ).only_enforce_if(~id_match)
            model.add_bool_and([id_match, neighbor.active]).only_enforce_if(match)
            model.add_bool_or([~id_match, ~neighbor.active]).only_enforce_if(~match)

        if self.adjacency_type == AdjacencyType.STANDARD:
            if self.count_type == CountType.AT_LEAST:
                model.add(sum(matches) >= self.amount).only_enforce_if(target)
                model.add(sum(matches) < self.amount).only_enforce_if(~target)
            elif self.count_type == CountType.EXACTLY:
                model.add(sum(matches) == self.amount).only_enforce_if(target)
                model.add(sum(matches) != self.amount).only_enforce_if(~target)
            elif self.count_type == CountType.AT_MOST:
                model.add(sum(matches) <= self.amount).only_enforce_if(target)
                model.add(sum(matches) > self.amount).only_enforce_if(~target)
        elif self.adjacency_type == AdjacencyType.AXIAL:
            axials = [
                model.new_bool_var(str(uuid.uuid4()))
                for _ in range(len(neighbors) // 2)
            ]
            for axial, (pos, neg) in zip(axials, itertools.batched(matches, 2)):
                model.add_bool_and([pos, neg]).only_enforce_if(axial)
                model.add_bool_or([~pos, ~neg]).only_enforce_if(~axial)
            if self.count_type == CountType.AT_LEAST:
                model.add(sum(axials) >= self.amount // 2).only_enforce_if(target)
                model.add(sum(axials) < self.amount // 2).only_enforce_if(~target)
            elif self.count_type == CountType.EXACTLY:
                model.add(sum(axials) == self.amount // 2).only_enforce_if(target)
                model.add(sum(axials) != self.amount // 2).only_enforce_if(~target)
            elif self.count_type == CountType.AT_MOST:
                model.add(sum(axials) <= self.amount // 2).only_enforce_if(target)
                model.add(sum(axials) > self.amount // 2).only_enforce_if(~target)
        elif self.adjacency_type == AdjacencyType.VERTEX:
            if len(neighbors) == 6:
                vertices = [model.new_bool_var(str(uuid.uuid4())) for _ in range(8)]
                for vertex, (a, b, c) in zip(
                    vertices,
                    [
                        (0, 2, 4),
                        (0, 2, 5),
                        (0, 3, 4),
                        (0, 3, 5),
                        (1, 2, 4),
                        (1, 2, 5),
                        (1, 3, 4),
                        (1, 3, 5),
                    ],
                ):
                    model.add_bool_and(
                        [matches[a], matches[b], matches[c]]
                    ).only_enforce_if(vertex)
                    model.add_bool_or(
                        [~matches[a], ~matches[b], ~matches[c]]
                    ).only_enforce_if(~vertex)
            else:
                raise ValueError("Vertex placement rules require exactly 3 dimensions.")

            vertex_exists = model.new_bool_var(str(uuid.uuid4()))
            model.add_bool_and(vertices).only_enforce_if(vertex_exists)
            model.add_bool_or([~vertex for vertex in vertices]).only_enforce_if(
                ~vertex_exists
            )

            amount_satisfied = model.new_bool_var(str(uuid.uuid4()))
            if self.count_type == CountType.AT_LEAST:
                model.add(sum(matches) >= self.amount).only_enforce_if(amount_satisfied)
                model.add(sum(matches) < self.amount).only_enforce_if(~amount_satisfied)
            elif self.count_type == CountType.EXACTLY:
                model.add(sum(matches) == self.amount).only_enforce_if(amount_satisfied)
                model.add(sum(matches) != self.amount).only_enforce_if(
                    ~amount_satisfied
                )
            elif self.count_type == CountType.AT_MOST:
                model.add(sum(matches) <= self.amount).only_enforce_if(amount_satisfied)
                model.add(sum(matches) > self.amount).only_enforce_if(~amount_satisfied)

            model.add_bool_and([vertex_exists, amount_satisfied]).only_enforce_if(
                target
            )
            model.add_bool_or([~vertex_exists, ~amount_satisfied]).only_enforce_if(
                ~target
            )
        elif self.adjacency_type == AdjacencyType.EDGE:
            if len(neighbors) == 4:
                edges = [model.new_bool_var(str(uuid.uuid4())) for _ in range(4)]
                for edge, (a, b) in zip(edges, [(0, 2), (0, 3), (1, 2), (1, 3)]):
                    model.add_bool_and([matches[a], matches[b]]).only_enforce_if(edge)
                    model.add_bool_or([~matches[a], ~matches[b]]).only_enforce_if(~edge)
            elif len(neighbors) == 6:
                edges = [model.new_bool_var(str(uuid.uuid4())) for _ in range(12)]
                for edge, (a, b) in zip(
                    edges,
                    [
                        (0, 2),
                        (0, 3),
                        (0, 4),
                        (0, 5),
                        (1, 2),
                        (1, 3),
                        (1, 4),
                        (1, 5),
                        (2, 4),
                        (2, 5),
                        (3, 4),
                        (3, 5),
                    ],
                ):
                    model.add_bool_and([matches[a], matches[b]]).only_enforce_if(edge)
                    model.add_bool_or([~matches[a], ~matches[b]]).only_enforce_if(~edge)
            else:
                raise ValueError(
                    "Edge placement rules require either 2 or 3 dimensions."
                )

            edge_exists = model.new_bool_var(str(uuid.uuid4()))
            model.add_bool_and(edges).only_enforce_if(edge_exists)
            model.add_bool_or([~edge for edge in edges]).only_enforce_if(~edge_exists)

            amount_satisfied = model.new_bool_var(str(uuid.uuid4()))
            if self.count_type == CountType.AT_LEAST:
                model.add(sum(matches) >= self.amount).only_enforce_if(amount_satisfied)
                model.add(sum(matches) < self.amount).only_enforce_if(~amount_satisfied)
            elif self.count_type == CountType.EXACTLY:
                model.add(sum(matches) == self.amount).only_enforce_if(amount_satisfied)
                model.add(sum(matches) != self.amount).only_enforce_if(
                    ~amount_satisfied
                )
            elif self.count_type == CountType.AT_MOST:
                model.add(sum(matches) <= self.amount).only_enforce_if(amount_satisfied)
                model.add(sum(matches) > self.amount).only_enforce_if(~amount_satisfied)

            model.add_bool_and([edge_exists, amount_satisfied]).only_enforce_if(target)
            model.add_bool_or([~edge_exists, ~amount_satisfied]).only_enforce_if(
                ~target
            )


class LogicType(enum.StrEnum):
    AND = "AND"
    OR = "OR"


class CompoundPlacementRule(BasePlacementRule, reg_key="core.compound"):
    subrules: list[PlacementRule]
    logic_type: LogicType

    def is_satisfied(self, neighbors: list[Neighbor]) -> bool:
        if self.logic_type == LogicType.AND:
            return all([subrule.is_satisfied(neighbors) for subrule in self.subrules])
        return any([subrule.is_satisfied(neighbors) for subrule in self.subrules])

    def to_cp_model(
        self,
        model: cp_model.CpModel,
        neighbors: list[CPNeighbor],
        mapping: list[tuple[str, str]],
        target: cp_model.IntVar,
    ) -> None:
        subtargets = [model.new_bool_var(str(uuid.uuid4())) for _ in self.subrules]
        for subrule, subtarget in zip(self.subrules, subtargets):
            subrule.to_cp_model(model, neighbors, mapping, subtarget)
        if self.logic_type == LogicType.AND:
            model.add_bool_and(subtargets).only_enforce_if(target)
            model.add_bool_or([~subtarget for subtarget in subtargets]).only_enforce_if(
                ~target
            )
        else:
            model.add_bool_or(subtargets).only_enforce_if(target)
            model.add_bool_and(
                [~subtarget for subtarget in subtargets]
            ).only_enforce_if(~target)
