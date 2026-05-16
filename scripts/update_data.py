# scripts/update_data.py

from services.finanzas_service import obtener_finanzas


def actualizar_datos():
    # Obtener datos ya procesados
    df = obtener_finanzas()

    # Guardar CSV
    df.to_csv("data/processed/datos.csv", index=False)

    return len(df)


if __name__ == "__main__":
    total = actualizar_datos()
    print(f"✅ Datos actualizados: {total} registros")