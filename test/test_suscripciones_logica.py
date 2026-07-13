from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


def _cargar_modulo():
    modulo_path = (
        Path(__file__).resolve().parents[1] / "app" / "pages" / "03_Suscripciones.py"
    )
    spec = importlib.util.spec_from_file_location("suscripciones_page", modulo_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_aplicar_colores_vencimiento_marca_rojo_a_7_dias():
    modulo = _cargar_modulo()

    df = pd.DataFrame({"Dias_Vencimiento": [-1, 0, 7, 8]})

    resultado = modulo._aplicar_colores_vencimiento(df)

    assert (
        resultado.loc[resultado["Dias_Vencimiento"] == -1, "Estado_Visual"].iloc[0]
        == "🔴 Vencida"
    )
    assert (
        resultado.loc[resultado["Dias_Vencimiento"] == 0, "Estado_Visual"].iloc[0]
        == "🔴 Vence pronto"
    )
    assert (
        resultado.loc[resultado["Dias_Vencimiento"] == 7, "Estado_Visual"].iloc[0]
        == "🔴 Vence pronto"
    )
    assert (
        resultado.loc[resultado["Dias_Vencimiento"] == 8, "Estado_Visual"].iloc[0]
        == "🟢 Vigente"
    )
