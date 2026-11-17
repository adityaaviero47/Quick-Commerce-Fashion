"""Step 3: the delivery-promise rule behind a size-level "60-min" badge.

This is the logic the PRD's acceptance criteria describe. tests/test_availability.py
checks every criterion, so a change that breaks the promise fails CI before launch.
"""
from dataclasses import dataclass
from datetime import time

CUTOFF = time(21, 0)       # last order time for same-hour delivery
MIN_SELLABLE = 1           # units that must be sellable at the hub after the buffer
BUFFER = 1                 # one unit held back for stock-accuracy gaps


@dataclass
class HubStock:
    on_hand: int
    reserved: int = 0      # picked for open orders
    damaged: int = 0       # failed quality check

    @property
    def sellable(self) -> int:
        return max(self.on_hand - self.reserved - self.damaged - BUFFER, 0)


def promise(size_stock: HubStock | None, pin_serviceable: bool, order_time: time) -> str:
    """Delivery promise for ONE size on the product page."""
    if size_stock is None or not pin_serviceable:
        return "standard"
    if size_stock.sellable < MIN_SELLABLE:
        return "standard"
    if order_time >= CUTOFF:
        return "tomorrow_morning"
    return "60_min"


def listing_badge(stock_by_size: dict, pin_serviceable: bool, order_time: time) -> str:
    """Badge on the listing tile: never claim 60 minutes for every size unless it is true."""
    p = [promise(s, pin_serviceable, order_time) for s in stock_by_size.values()]
    if p and all(x == "60_min" for x in p):
        return "60_min_all_sizes"
    if any(x == "60_min" for x in p):
        return "60_min_some_sizes"
    return "none"
