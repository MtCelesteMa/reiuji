"""Tests for the `reiuji.core.utils.catalog` module."""

import pytest

from reiuji.core.utils.catalog import Catalog


@pytest.fixture
def catalog() -> Catalog[int]:
    return Catalog(catalog={"a": {"b": 1, "c": 2}, "d": {"e": 3, "f": 4}})


def test_getitem(catalog: Catalog[int]) -> None:
    assert catalog["a", "b"] == 1
    assert catalog["a", "c"] == 2
    assert catalog["d", "e"] == 3
    assert catalog["d", "f"] == 4
    with pytest.raises(KeyError):
        catalog["a", "d"]


def test_setitem(catalog: Catalog[int]) -> None:
    catalog["a", "b"] = 5
    assert catalog["a", "b"] == 5
    catalog["g", "h"] = 10
    assert catalog["g", "h"] == 10


def test_as_list(catalog: Catalog[int]) -> None:
    assert catalog.as_list() == [[1, 2], [3, 4]]
