"""Acceptance criteria from PRD.md, one test per criterion (AC-1 ... AC-8)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from datetime import time
from availability import HubStock, promise, listing_badge

NOON, LATE = time(12, 0), time(21, 30)


def test_ac1_60min_only_when_selected_size_is_sellable():
    assert promise(HubStock(on_hand=3), True, NOON) == "60_min"


def test_ac2_size_not_at_hub_falls_back_to_standard():
    assert promise(None, True, NOON) == "standard"


def test_ac3_buffer_unit_is_never_promised():
    assert promise(HubStock(on_hand=1), True, NOON) == "standard"


def test_ac4_reserved_and_damaged_units_are_not_sellable():
    assert promise(HubStock(on_hand=4, reserved=2, damaged=1), True, NOON) == "standard"
    assert promise(HubStock(on_hand=5, reserved=2, damaged=1), True, NOON) == "60_min"


def test_ac5_pin_code_outside_service_area_gets_standard():
    assert promise(HubStock(on_hand=10), False, NOON) == "standard"


def test_ac6_after_cutoff_promises_next_morning():
    assert promise(HubStock(on_hand=10), True, LATE) == "tomorrow_morning"


def test_ac7_listing_says_some_sizes_when_a_size_is_missing():
    stock = {"M": HubStock(5), "L": HubStock(5), "XL": None}
    assert listing_badge(stock, True, NOON) == "60_min_some_sizes"


def test_ac8_listing_says_all_sizes_only_when_every_size_qualifies():
    assert listing_badge({"M": HubStock(5), "L": HubStock(4)}, True, NOON) == "60_min_all_sizes"
    assert listing_badge({"M": None, "L": HubStock(1)}, True, NOON) == "none"
