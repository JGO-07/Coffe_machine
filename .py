# Coffee Machine
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

# Comprobar si se puede hacer la bebida
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

# Gastar recursos
def spend_resources(drink: str, st: Dict[str, int]) -> None:
    """Deduct the resources for a given drink (mutates st)."""
    req = RECIPES[drink]
    st["water"] -= req["water"]
    st["milk"]  -= req["milk"]
    st["beans"] -= req["beans"]
    st["cups"]  -= 1

# Registrar venta
def record_sale(drink: str, st: Dict[str, int]) -> None:
    if drink == "espresso":
        st["sold_espresso"] += 1
    elif drink == "latte":
        st["sold_latte"] += 1
    elif drink == "cappuccino":
        st["sold_cappuccino"] += 1

# Comprobar si está lleno
def is_full(st: Dict[str, int]) -> bool:
    return all(st[k] >= MAX_CAPACITY[k] for k in ("water","milk","beans","cups"))

# Limitar el llenado
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

# Funcion de mostrar datos
def show_data(st: Dict[str, int]) -> str:
    total_sales = (st["sold_espresso"] * RECIPES["espresso"]["price"] +
                   st["sold_latte"] * RECIPES["latte"]["price"] +
                   st["sold_cappuccino"] * RECIPES["cappuccino"]["price"])
    lines = [
        "=== ESTADO DE LA MÁQUINA ===",
        f"Agua: {st['water']} / {MAX_CAPACITY['water']} ml",
        f"Leche: {st['milk']} / {MAX_CAPACITY['milk']} ml",
        f"Café molido (beans): {st['beans']} / {MAX_CAPACITY['beans']} g",
        f"Vasos: {st['cups']} / {MAX_CAPACITY['cups']} u",
        f"Dinero en máquina: ${st['money']}",
        "--- Ventas ---",
        f"Espresso: {st['sold_espresso']}",
        f"Latte: {st['sold_latte']}",
        f"Cappuccino: {st['sold_cappuccino']}",
        f"Ingresos por ventas (histórico): ${total_sales}",
        f"Retirado: ${st['withdrawn_total']}   Donado: ${st['donated']}",
    ]
    return "\n".join(lines)

# Menú de opciones
def menu_text() -> str:
    return (
        "\n=== MENÚ ===\n"
        "1) Hacer café\n"
        "2) Rellenar máquina\n"
        "3) Retirar dinero / Donar a caridad\n"
        "4) Mostrar datos\n"
        "5) Salir\n"
        "Seleccione opción: "
    )


# Limpiar pantalla
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Acciones

# Acción: Hacer café
def action_make_coffee(st: Dict[str, int]) -> None:
    print("\n--- Hacer café ---")
    print("Tipos: 1) Espresso ($4)  2) Latte ($7)  3) Cappuccino ($6)  4) Cancelar")
    choice = input("Elija (1-4): ").strip()
    mapping = {"1":"espresso", "2":"latte", "3":"cappuccino"}
    if choice == "4" or choice.lower() == "c":
        print("Operación cancelada.")
        return
    drink = mapping.get(choice)
    if not drink:
        print("Opción inválida.")
        return
    ok, msg = can_make(drink, st)
    if not ok:
        print("No se puede preparar:", msg)
        return
    price = RECIPES[drink]["price"]
    print(f"Precio: ${price}")
    try:
        paid = float(input("Inserte dinero ($): ").strip())
    except ValueError:
        print("Entrada inválida; cancelando.")
        return
    if paid < price:
        print(f"Dinero insuficiente. Reembolsando ${paid:.2f}.")
        return
    change = round(paid - price, 2)
    spend_resources(drink, st)
    st["money"] += price
    record_sale(drink, st)
    print(f"Preparando {drink.capitalize()}... ¡Listo!")
    if change > 0:
        print(f"Su cambio: ${change:.2f}")

# Acción: Rellenar máquina
def action_fill_machine(st: Dict[str, int]) -> None:
    print("\n--- Rellenar máquina ---")
    if is_full(st):
        print("La máquina ya está al 100% de capacidad.")
        return
    try:
        add_water = int(input(f"Agregar agua (ml, máx {MAX_CAPACITY['water'] - st['water']}): ").strip() or "0")
        add_milk  = int(input(f"Agregar leche (ml, máx {MAX_CAPACITY['milk'] - st['milk']}): ").strip() or "0")
        add_beans = int(input(f"Agregar café molido (g, máx {MAX_CAPACITY['beans'] - st['beans']}): ").strip() or "0")
        add_cups  = int(input(f"Agregar vasos (u, máx {MAX_CAPACITY['cups'] - st['cups']}): ").strip() or "0")
    except ValueError:
        print("Entrada inválida.")
        return
    added = clamp_fill(st, {"water": add_water, "milk": add_milk, "beans": add_beans, "cups": add_cups})
    print("Cargado (sin exceder capacidad):", added)


# Acción: Retirar dinero / Donar
def action_withdraw_or_donate(st: Dict[str, int]) -> None:
    print("\n--- Caja ---")
    print(f"Dinero disponible en máquina: ${st['money']}")
    print("1) Retirar todo\n2) Donar todo a caridad\n3) Cancelar")
    op = input("Elija (1-3): ").strip()
    if op == "1":
        st["withdrawn_total"] += st["money"]
        print(f"Retirados ${st['money']}.")
        st["money"] = 0
    elif op == "2":
        st["donated"] += st["money"]
        print(f"Donados ${st['money']} a caridad. ¡Gracias!")
        st["money"] = 0
    else:
        print("Operación cancelada.")

def action_show_data(st: Dict[str, int]) -> None:
    print()
    print(show_data(st))

# Main loop

def main() -> None:
    print("Bienvenido a Coffee Machine\n")
    while True:
        choice = input(menu_text()).strip()
        if choice == "1":
            clear_screen()
            action_make_coffee(state)
        elif choice == "2":
            clear_screen()
            action_fill_machine(state)
        elif choice == "3":
            clear_screen()
            action_withdraw_or_donate(state)
        elif choice == "4":
            clear_screen()
            action_show_data(state)
        elif choice == "5":
            clear_screen()
            print("Sesión finalizada. ¡Hasta luego!")
            break
        else:
            clear_screen()
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()