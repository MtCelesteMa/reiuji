"""A multi-dimensional sequence."""

import typing
from collections import abc
import math


class MultiSequence[E](abc.Sequence[E], abc.Iterable[E]):
    """A class representing a multi-dimensional sequence.

    This class combines the functionality of both `abc.Sequence` and `abc.Iterable` to provide
    a multi-dimensional sequence object.

    Attributes:
        seq (abc.Sequence[E]): The input sequence.
        shape (tuple[int, ...]): The desired shape of the MultiSequence.
    """
    def __init__(self, seq: abc.Sequence[E], shape: tuple[int, ...]) -> None:
        """Initializes a MultiSequence object.

        Args:
            seq (abc.Sequence[E]): The input sequence.
            shape (tuple[int, ...]): The desired shape of the MultiSequence.

        Raises:
            ValueError: If the shape does not match the length of the sequence.
        """
        self.seq = seq
        self.shape = shape
        if math.prod(shape) != len(seq):
            raise ValueError("Shape does not match sequence length")
    
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
        ...
    
    @typing.overload
    def __getitem__(self, index: slice) -> abc.Sequence[E]:
        ...

    @typing.overload
    def __getitem__(self, index: tuple[int, ...]) -> E:
        ...

    def __getitem__(self, index: int | slice | tuple[int, ...]) -> E | abc.Sequence[E]:
        if isinstance(index, (int, slice)):
            return self.seq[index]
        elif isinstance(index, tuple):
            return self.seq[self.index_tuple_to_int(index)]
        else:
            raise TypeError("Invalid index type")
    
    def __iter__(self) -> abc.Iterator[E]:
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
