"""Tests for the placement rule parser."""

from reiuji.core.placement_rules import parse_rule_string


RULE_STRINGS = [
    "one cell",
    "two cells",
    "one cell && one moderator",
    "two axial glowstone sinks",
    "one reflector && one iron heater",
    "exactly two different cells",
    "two different cavity",
    "one yoke && one cavity",
    "one iron heater || exactly two reflectors"
]

SOLUTIONS = [
    {"type": "cell", "quantity": 1, "exact": False, "axial": False, "different": False},
    {"type": "cell", "quantity": 2, "exact": False, "axial": False, "different": False},
    {
        "rules": [
            {"type": "cell", "quantity": 1, "exact": False, "axial": False, "different": False},
            {"type": "moderator", "quantity": 1, "exact": False, "axial": False, "different": False}
        ],
        "mode": "AND"
    },
    {"name": "glowstone", "type": "sink", "quantity": 2, "exact": False, "axial": True},
    {
        "rules": [
            {"type": "reflector", "quantity": 1, "exact": False, "axial": False, "different": False},
            {"name": "iron", "type": "heater", "quantity": 1, "exact": False, "axial": False}
        ],
        "mode": "AND"
    },
    {"type": "cell", "quantity": 2, "exact": True, "axial": False, "different": True},
    {"type": "cavity", "quantity": 2, "exact": False, "axial": False, "different": True},
    {
        "rules": [
            {"type": "yoke", "quantity": 1, "exact": False, "axial": False, "different": False},
            {"type": "cavity", "quantity": 1, "exact": False, "axial": False, "different": False}
        ],
        "mode": "AND"
    },
    {
        "rules": [
            {"name": "iron", "type": "heater", "quantity": 1, "exact": False, "axial": False},
            {"type": "reflector", "quantity": 2, "exact": True, "axial": False, "different": False}
        ],
        "mode": "OR"
    }
]


def test_parser() -> None:
    for rule_str, solution in zip(RULE_STRINGS, SOLUTIONS):
        assert parse_rule_string(rule_str).to_dict() == solution
