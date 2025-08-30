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