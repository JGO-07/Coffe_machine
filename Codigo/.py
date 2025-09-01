# Coffee Machine 
# Authors: Jesus Vargas Pacheco, Josue Godoy Orozco, Eduardo Nestor Perez Davalos

# Librerias para tipado y manejo de sistema
from typing import Dict, Tuple
import os

# Declaración de los tipos de bebidas posibles y sus atributos
RECIPES: Dict[str, Dict[str, int]] = {
    "espresso":   {"water": 250, "milk": 0,   "beans": 16, "price": 4},
    "latte":      {"water": 350, "milk": 75,  "beans": 20, "price": 7},
    "cappuccino": {"water": 200, "milk": 100, "beans": 12, "price": 6},
}

# Declaración del máximo de los atributos
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
    "money": 0,            # dinero actualmente en la máquina (caja)
    "wallet": 0.0,         # <<< saldo del usuario (cartera)
    "sold_espresso": 0,
    "sold_latte": 0,
    "sold_cappuccino": 0,
    "donated": 0,          # dinero donado a la caridad
    "withdrawn_total": 0,  # retiros totales
}

# Configuración inicial del Admin
admin_credentials = {
    "username": "admin",
    "password": "1234"
}

ADMIN_MODE = False

# Helpers
def can_make(drink: str, st: Dict[str, int]) -> Tuple[bool, str]:
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
    req = RECIPES[drink]
    st["water"] -= req["water"]
    st["milk"]  -= req["milk"]
    st["beans"] -= req["beans"]
    st["cups"]  -= 1

# Registro de ventas
def record_sale(drink: str, st: Dict[str, int]) -> None:
    if drink == "espresso":
        st["sold_espresso"] += 1
    elif drink == "latte":
        st["sold_latte"] += 1
    elif drink == "cappuccino":
        st["sold_cappuccino"] += 1

# Verificar si la máquina está llena
def is_full(st: Dict[str, int]) -> bool:
    return all(st[k] >= MAX_CAPACITY[k] for k in ("water","milk","beans","cups"))

# Limitar el llenado de los recursos
def clamp_fill(st: Dict[str, int], to_fill: Dict[str, int]) -> Dict[str, int]:
    added = {}
    for k in ("water","milk","beans","cups"):
        current = st[k]
        cap = MAX_CAPACITY[k]
        add = max(0, min(to_fill.get(k, 0), cap - current))
        added[k] = add
        st[k] += add
    return added

# Mostrar datos de la máquina
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
        f"Dinero en máquina (caja): ${st['money']}",
        f"Saldo de cartera del usuario: ${st['wallet']:.2f}",
        "--- Ventas ---",
        f"Espresso: {st['sold_espresso']}",
        f"Latte: {st['sold_latte']}",
        f"Cappuccino: {st['sold_cappuccino']}",
        f"Ingresos por ventas (histórico): ${total_sales}",
        f"Retirado: ${st['withdrawn_total']}   Donado: ${st['donated']}",
    ]
    return "\n".join(lines)

# Generar recibo de compra
def generate_receipt(drink: str, paid: float, change: float) -> str:
    price = RECIPES[drink]["price"]
    return f"""
=== RECIBO DE COMPRA ===
Café: {drink.capitalize()}
Precio: ${price}
Pagado: ${paid:.2f}
Cambio: ${change:.2f}
¡Gracias por su compra!
========================
"""

# MENÚS

# Menú principal
def main_menu_text() -> str:
    return (
        "\n=== COFFEE MACHINE ===\n"
        "1) Modo Usuario\n"
        "2) Modo Administrador\n"
        "3) Salir\n"
        "Seleccione opción: "
    )

# Menú de usuario
def user_menu_text(st: Dict[str, int]) -> str:
    # Se muestra el saldo actual para comodidad
    return (
        f"\n=== MODO USUARIO ===   (Saldo: ${st['wallet']:.2f})\n"
        "1) Insertar dinero en cartera\n"
        "2) Hacer café\n"
        "3) Reembolsar saldo de cartera\n"
        "4) Regresar al menú principal\n"
        "Seleccione opción: "
    )

# Menú de administrador
def admin_menu_text() -> str:
    return (
        "\n=== MODO ADMINISTRADOR ===\n"
        "1) Hacer café\n"
        "2) Rellenar máquina\n"
        "3) Retirar dinero / Donar a caridad\n"
        "4) Mostrar datos\n"
        "5) Cambiar credenciales\n"
        "6) Regresar al menú principal\n"
        "Seleccione opción: "
    )

# Limpiar pantalla
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ACCIONES

# Insertar dinero
def action_insert_money(st: Dict[str, int]) -> None:
    print("\n--- Insertar dinero ---")
    try:
        amount = float(input("Monto a ingresar ($): ").strip())
        if amount <= 0:
            print("Monto inválido.")
            return
        st["wallet"] = round(st["wallet"] + amount, 2)
        print(f"Saldo actualizado: ${st['wallet']:.2f}")
    except ValueError:
        print("Entrada inválida.")

# Reembolsar saldo de cartera
def action_refund_wallet(st: Dict[str, int]) -> None:
    print("\n--- Reembolsar saldo ---")
    if st["wallet"] <= 0:
        print("No hay saldo en la cartera.")
        return
    print(f"Reembolsando ${st['wallet']:.2f}.")
    st["wallet"] = 0.0

# Hacer café
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
    if st["wallet"] < price:
        faltan = price - st["wallet"]
        print(f"Precio: ${price}. Saldo en cartera: ${st['wallet']:.2f}.")
        print(f"Saldo insuficiente. Faltan ${faltan:.2f}. Inserte más dinero desde el menú de usuario.")
        return

    # Cobro desde la cartera
    st["wallet"] = round(st["wallet"] - price, 2)
    spend_resources(drink, st)
    st["money"] += price
    record_sale(drink, st)

    print(f"Preparando {drink.capitalize()}... ¡Listo!")
    print(generate_receipt(drink, price, 0.0))

    # Ofrecer reembolsar lo que aún quede en la cartera (opcional)
    if st["wallet"] > 0:
        op = input(f"Quedan ${st['wallet']:.2f} en su cartera. ¿Desea reembolsarlos ahora? (s/n): ").lower()
        if op == "s":
            print(f"Reembolsando ${st['wallet']:.2f}.")
            st["wallet"] = 0.0
        else:
            print("El saldo permanece en su cartera para futuras compras.")

# Rellenar máquina
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

# Retirar o donar dinero
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

# Mostrar datos de la máquina
def action_show_data(st: Dict[str, int]) -> None:
    print()
    print(show_data(st))

# LOGIN Y CREDENCIALES ADMIN

# Función para iniciar sesión como administrador
def admin_login() -> bool:
    print("\n=== LOGIN ADMINISTRADOR ===")
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            username = input("Usuario: ").strip()
            password = input("Contraseña: ").strip()
            if username == admin_credentials["username"] and password == admin_credentials["password"]:
                clear_screen()
                print("Login exitoso. Bienvenido al modo administrador")
                return True
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"Contraseña o usuario incorrecto. Te quedan {remaining} intentos.")
                else:
                    print("Demasiados intentos fallidos. Regresando al menú principal.")
        except KeyboardInterrupt:
            print("\n Login cancelado por el usuario.")
            return False
    return False

# Cambiar credenciales de administrador
def change_admin_credentials() -> None:
    print("\n=== CAMBIAR CREDENCIALES ===")
    print("Confirme su identidad actual:")
    current_user = input("Usuario actual: ").strip()
    current_pass = input("Contraseña actual: ").strip()
    if current_user != admin_credentials["username"] or current_pass != admin_credentials["password"]:
        print("Credenciales actuales incorrectas. Operación cancelada.")
        return
    print("\n Ingrese las nuevas credenciales:")
    new_username = input("Nuevo usuario: ").strip()
    new_password = input("Nueva contraseña: ").strip()
    if new_username == "" or new_password == "":
        print("Las credenciales no pueden estar vacías. Operación cancelada.")
        return
    confirm = input(f"¿Confirmar cambio de usuario a '{new_username}'? (s/n): ").lower()
    if confirm == 's':
        admin_credentials["username"] = new_username
        admin_credentials["password"] = new_password
        print("Credenciales actualizadas exitosamente.")
    else:
        print("Cambio de credenciales cancelado.")

# LOOPS

# Modo Usuario
def user_mode() -> None:
    print("Modo Usuario")
    while True:
        choice = input(user_menu_text(state)).strip()
        if choice == "1":
            clear_screen()
            action_insert_money(state)
        elif choice == "2":
            clear_screen()
            action_make_coffee(state)
        elif choice == "3":
            clear_screen()
            action_refund_wallet(state)
        elif choice == "4":
            clear_screen()
            print("Regresando al menú principal...")
            break
        else:
            clear_screen()
            print("Opción no válida. Intente de nuevo.")

# Modo Administrador
def admin_mode() -> None:
    if not admin_login():
        return
    print("Modo Administrador")
    while True:
        choice = input(admin_menu_text()).strip()
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
            change_admin_credentials()
        elif choice == "6":
            clear_screen()
            print("Saliendo del modo administrador...")
            break
        else:
            clear_screen()
            print("Opción no válida. Intente de nuevo.")

# MAIN

# Función principal
def main() -> None:
    print("Bienvenido a Coffee Machine")
    while True:
        choice = input(main_menu_text()).strip()
        if choice == "1":
            clear_screen()
            user_mode()
        elif choice == "2":
            clear_screen()
            admin_mode()
        elif choice == "3":
            clear_screen()
            print("Sesión finalizada. ¡Hasta luego!")
            break
        else:
            clear_screen()
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
