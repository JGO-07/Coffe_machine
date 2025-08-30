# Coffee Machine (no classes)
# Author: Jesus Vargas Pacheco

from typing import Dict, Tuple
import os

RECIPES: Dict[str, Dict[str, int]] = {
    "espresso":   {"water": 250, "milk": 0,   "beans": 16, "price": 4},
    "latte":      {"water": 350, "milk": 75,  "beans": 20, "price": 7},
    "cappuccino": {"water": 200, "milk": 100, "beans": 12, "price": 6},
}

MAX_CAPACITY = {
    "water": 2500,
    "milk": 1000,
    "beans": 200,
    "cups": 10,
}

# Estados iniciales
state = {
    "water": MAX_CAPACITY["water"],
    "milk": MAX_CAPACITY["milk"],
    "beans": MAX_CAPACITY["beans"],
    "cups": MAX_CAPACITY["cups"],
    "money": 0,            # dinero actualmente en la máquina
    "sold_espresso": 0,
    "sold_latte": 0,
    "sold_cappuccino": 0,
    "donated": 0,          # dinero donado a la caridad
    "withdrawn_total": 0,  # retiros totales
}

# Helpers (funciones puras)

def can_make(drink: str, st: Dict[str, int]) -> Tuple[bool, str]:
    """Check if there are enough resources to make the drink."""
    if drink not in RECIPES:
        return False, f"Bebida desconocida: {drink}"
    req = RECIPES[drink]
    lacking = []
    for res in ("water", "milk", "beans", "cups"):
        need = (req.get(res, 0) if res != "cups" else 1)
        if st[res] < need:
            lacking.append(res)
    if lacking:
        return False, "Faltan recursos: " + ", ".join(lacking)
    return True, ""

def spend_resources(drink: str, st: Dict[str, int]) -> None:
    """Deduct the resources for a given drink (mutates st)."""
    req = RECIPES[drink]
    st["water"] -= req["water"]
    st["milk"]  -= req["milk"]
    st["beans"] -= req["beans"]
    st["cups"]  -= 1

def record_sale(drink: str, st: Dict[str, int]) -> None:
    if drink == "espresso":
        st["sold_espresso"] += 1
    elif drink == "latte":
        st["sold_latte"] += 1
    elif drink == "cappuccino":
        st["sold_cappuccino"] += 1

def is_full(st: Dict[str, int]) -> bool:
    return all(st[k] >= MAX_CAPACITY[k] for k in ("water","milk","beans","cups"))

def clamp_fill(st: Dict[str, int], to_fill: Dict[str, int]) -> Dict[str, int]:
    """Return the actual amounts that can be added without exceeding capacity."""
    added = {}
    for k in ("water","milk","beans","cups"):
        current = st[k]
        cap = MAX_CAPACITY[k]
        add = max(0, min(to_fill.get(k, 0), cap - current))
        added[k] = add
        st[k] += add
    return added


