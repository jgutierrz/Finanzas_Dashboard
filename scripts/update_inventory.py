# scripts/update_inventory.py

from services.inventory_service import obtener_inventario


def actualizar_inventario():
    # Obtener datos ya procesados
    df = obtener_inventario()

    # Guardar CSV
    df.to_csv("data/processed/inventario.csv", index=False)

    return len(df)


if __name__ == "__main__":
    total = actualizar_inventario()
    print(f"✅ Inventario actualizado: {total} registros")