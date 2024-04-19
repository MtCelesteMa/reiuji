"""Tests for the MultiSequence class."""

import pytest
from reiuji.core.multi_sequence import MultiSequence


@pytest.fixture
def multi_sequence() -> MultiSequence[int]:
    return MultiSequence(range(24), (2, 3, 4))


def test_len(multi_sequence: MultiSequence[int]) -> None:
    assert len(multi_sequence) == 24


def test_index_tuple_to_int(multi_sequence: MultiSequence[int]) -> None:
    assert multi_sequence.index_tuple_to_int((0, 0, 0)) == 0
    assert multi_sequence.index_tuple_to_int((0, 0, 1)) == 1
    assert multi_sequence.index_tuple_to_int((0, 0, 2)) == 2
    assert multi_sequence.index_tuple_to_int((0, 0, 3)) == 3
    assert multi_sequence.index_tuple_to_int((0, 1, 0)) == 4
    assert multi_sequence.index_tuple_to_int((0, 1, 1)) == 5
    assert multi_sequence.index_tuple_to_int((0, 1, 2)) == 6
    assert multi_sequence.index_tuple_to_int((0, 1, 3)) == 7
    assert multi_sequence.index_tuple_to_int((0, 2, 0)) == 8
    assert multi_sequence.index_tuple_to_int((0, 2, 1)) == 9
    assert multi_sequence.index_tuple_to_int((0, 2, 2)) == 10
    assert multi_sequence.index_tuple_to_int((0, 2, 3)) == 11
    assert multi_sequence.index_tuple_to_int((1, 0, 0)) == 12
    assert multi_sequence.index_tuple_to_int((1, 0, 1)) == 13
    assert multi_sequence.index_tuple_to_int((1, 0, 2)) == 14
    assert multi_sequence.index_tuple_to_int((1, 0, 3)) == 15
    assert multi_sequence.index_tuple_to_int((1, 1, 0)) == 16
    assert multi_sequence.index_tuple_to_int((1, 1, 1)) == 17
    assert multi_sequence.index_tuple_to_int((1, 1, 2)) == 18
    assert multi_sequence.index_tuple_to_int((1, 1, 3)) == 19
    assert multi_sequence.index_tuple_to_int((1, 2, 0)) == 20
    assert multi_sequence.index_tuple_to_int((1, 2, 1)) == 21
    assert multi_sequence.index_tuple_to_int((1, 2, 2)) == 22
    assert multi_sequence.index_tuple_to_int((1, 2, 3)) == 23


def test_index_int_to_tuple(multi_sequence: MultiSequence[int]) -> None:
    assert multi_sequence.index_int_to_tuple(0) == (0, 0, 0)
    assert multi_sequence.index_int_to_tuple(1) == (0, 0, 1)
    assert multi_sequence.index_int_to_tuple(2) == (0, 0, 2)
    assert multi_sequence.index_int_to_tuple(3) == (0, 0, 3)
    assert multi_sequence.index_int_to_tuple(4) == (0, 1, 0)
    assert multi_sequence.index_int_to_tuple(5) == (0, 1, 1)
    assert multi_sequence.index_int_to_tuple(6) == (0, 1, 2)
    assert multi_sequence.index_int_to_tuple(7) == (0, 1, 3)
    assert multi_sequence.index_int_to_tuple(8) == (0, 2, 0)
    assert multi_sequence.index_int_to_tuple(9) == (0, 2, 1)
    assert multi_sequence.index_int_to_tuple(10) == (0, 2, 2)
    assert multi_sequence.index_int_to_tuple(11) == (0, 2, 3)
    assert multi_sequence.index_int_to_tuple(12) == (1, 0, 0)
    assert multi_sequence.index_int_to_tuple(13) == (1, 0, 1)
    assert multi_sequence.index_int_to_tuple(14) == (1, 0, 2)
    assert multi_sequence.index_int_to_tuple(15) == (1, 0, 3)
    assert multi_sequence.index_int_to_tuple(16) == (1, 1, 0)
    assert multi_sequence.index_int_to_tuple(17) == (1, 1, 1)
    assert multi_sequence.index_int_to_tuple(18) == (1, 1, 2)
    assert multi_sequence.index_int_to_tuple(19) == (1, 1, 3)
    assert multi_sequence.index_int_to_tuple(20) == (1, 2, 0)
    assert multi_sequence.index_int_to_tuple(21) == (1, 2, 1)
    assert multi_sequence.index_int_to_tuple(22) == (1, 2, 2)
    assert multi_sequence.index_int_to_tuple(23) == (1, 2, 3)


def test_getitem(multi_sequence: MultiSequence[int]) -> None:
    assert multi_sequence[0] == multi_sequence[0, 0, 0] == 0
    assert multi_sequence[1] == multi_sequence[0, 0, 1] == 1
    assert multi_sequence[2] == multi_sequence[0, 0, 2] == 2
    assert multi_sequence[3] == multi_sequence[0, 0, 3] == 3
    assert multi_sequence[4] == multi_sequence[0, 1, 0] == 4
    assert multi_sequence[5] == multi_sequence[0, 1, 1] == 5
    assert multi_sequence[6] == multi_sequence[0, 1, 2] == 6
    assert multi_sequence[7] == multi_sequence[0, 1, 3] == 7
    assert multi_sequence[8] == multi_sequence[0, 2, 0] == 8
    assert multi_sequence[9] == multi_sequence[0, 2, 1] == 9
    assert multi_sequence[10] == multi_sequence[0, 2, 2] == 10
    assert multi_sequence[11] == multi_sequence[0, 2, 3] == 11
    assert multi_sequence[12] == multi_sequence[1, 0, 0] == 12
    assert multi_sequence[13] == multi_sequence[1, 0, 1] == 13
    assert multi_sequence[14] == multi_sequence[1, 0, 2] == 14
    assert multi_sequence[15] == multi_sequence[1, 0, 3] == 15
    assert multi_sequence[16] == multi_sequence[1, 1, 0] == 16
    assert multi_sequence[17] == multi_sequence[1, 1, 1] == 17
    assert multi_sequence[18] == multi_sequence[1, 1, 2] == 18
    assert multi_sequence[19] == multi_sequence[1, 1, 3] == 19
    assert multi_sequence[20] == multi_sequence[1, 2, 0] == 20
    assert multi_sequence[21] == multi_sequence[1, 2, 1] == 21
    assert multi_sequence[22] == multi_sequence[1, 2, 2] == 22
    assert multi_sequence[23] == multi_sequence[1, 2, 3] == 23


def test_neighbors(multi_sequence: MultiSequence[int]) -> None:
    assert multi_sequence.neighbors((0, 0, 0), 0) == (None, 12)
    assert multi_sequence.neighbors((0, 0, 0), 1) == (None, 4)
    assert multi_sequence.neighbors((0, 0, 0), 2) == (None, 1)
    assert multi_sequence.neighbors((0, 0, 1), 0) == (None, 13)
    assert multi_sequence.neighbors((0, 0, 1), 1) == (None, 5)
    assert multi_sequence.neighbors((0, 0, 1), 2) == (0, 2)
    assert multi_sequence.neighbors((0, 0, 2), 0) == (None, 14)
    assert multi_sequence.neighbors((0, 0, 2), 1) == (None, 6)
    assert multi_sequence.neighbors((0, 0, 2), 2) == (1, 3)
    assert multi_sequence.neighbors((0, 0, 3), 0) == (None, 15)
    assert multi_sequence.neighbors((0, 0, 3), 1) == (None, 7)
    assert multi_sequence.neighbors((0, 0, 3), 2) == (2, None)
