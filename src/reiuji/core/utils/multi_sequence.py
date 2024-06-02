"""A multi-dimensional sequence."""

import typing
from collections import abc
import math

import pydantic


class MultiSequence[E](pydantic.BaseModel, abc.Sequence[E]):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    seq: list[E]
    shape: tuple[int, ...]

    @pydantic.model_validator(mode="after")
    def check_shape(self) -> typing.Self:
        if len(self.seq) != math.prod(self.shape):
            raise ValueError("Shape and sequence length mismatch.")
        return self

    def __len__(self) -> int:
        return len(self.seq)
    
    def index_tuple_to_int(self, index: tuple[int, ...]) -> int:
        """Converts a tuple of indices to a single integer index.

        Args:
            index (tuple[int, ...]): The tuple of indices.

        Returns:
            int: The converted integer index.
        """
        return sum(index[i] * math.prod(self.shape[i + 1:]) for i in range(len(index)))
    
    def index_int_to_tuple(self, index: int) -> tuple[int, ...]:
        """Converts an integer index to a tuple of indices based on the shape of the multi-sequence.

        Args:
            index (int): The integer index to convert.

        Returns:
            tuple[int, ...]: A tuple of indices representing the position in the multi-sequence.
        """
        return tuple((index // math.prod(self.shape[i + 1:])) % self.shape[i] for i in range(len(self.shape)))

    @typing.overload
    def __getitem__(self, index: int) -> E:
        """
        Get the element at the specified index in the multi-sequence.

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            E: The element at the specified index.
        """
        ...
    
    @typing.overload
    def __getitem__(self, index: slice) -> abc.Sequence[E]:
        """
        Get a sequence of elements from the multi-sequence based on the given slice.

        Args:
            index (slice): The slice object specifying the range of indices to retrieve.

        Returns:
            abc.Sequence[E]: A sequence of elements from the multi-sequence.
        """
        ...

    @typing.overload
    def __getitem__(self, index: tuple[int, ...]) -> E:
        """
        Get the element at the specified index in the multi-sequence.

        Args:
            index (tuple[int, ...]): The index of the element to retrieve.

        Returns:
            E: The element at the specified index.
        """
        ...

    def __getitem__(self, index: int | slice | tuple[int, ...]) -> E | abc.Sequence[E]:
        if isinstance(index, (int, slice)):
            return self.seq[index]
        elif isinstance(index, tuple):
            return self.seq[self.index_tuple_to_int(index)]
        else:
            raise TypeError("Invalid index type")
    
    def __setitem__(self, index: int, value: E) -> None:
        """
        Set the value at the specified index in the multi-sequence.

        Args:
            index (int): The index of the element to set.
            value (E): The value to set at the specified index.

        Returns:
            None: This function does not return anything.
        """
        self.seq[index] = value
    
    def iter(self) -> abc.Iterator[E]:
        """Returns an iterator over the elements of the multi-sequence.

        Returns:
            abc.Iterator[E]: An iterator over the elements of the multi-sequence.
        """
        return iter(self.seq)
    
    def neighbors(self, index: int | tuple[int, ...], axis: int) -> tuple[E | None, E | None]:
        """Returns the neighboring elements of the given index along the specified axis.

        Args:
            index (int | tuple[int, ...]): The index of the element.
            axis (int): The axis along which to find the neighbors.

        Returns:
            tuple[E | None, E | None]: A tuple containing the left and right neighboring elements.
        """
        if isinstance(index, int):
            index = self.index_int_to_tuple(index)
        if not 0 <= axis < len(self.shape):
            raise ValueError("Axis out of bounds.")
        left = None if index[axis] == 0 else self[index[:axis] + (index[axis] - 1,) + index[axis + 1:]]
        right = None if index[axis] == self.shape[axis] - 1 else self[index[:axis] + (index[axis] + 1,) + index[axis + 1:]]
        return left, right
