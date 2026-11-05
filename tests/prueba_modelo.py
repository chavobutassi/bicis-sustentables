"""Pruebas del modelo de riesgo de falla (fase 2) contra una base con los datos de demostración.

Solo LEE de la base, salvo la comprobación final de la tabla de predicciones (que hay que haber
generado antes con `--escribir`). No necesita una copia:

    DATABASE_URL=postgresql://.../bicis python3 tests/prueba_modelo.py
"""
import gzip
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "modelo"))
import riesgo_falla as R  # noqa: E402

fallos = []


def comprobar(nombre, condicion, detalle=""):
    print(("OK   " if condicion else "FALLA"), nombre, detalle)
    if not condicion:
        fallos.append(nombre)


url = os.environ.get("DATABASE_URL")
if not url:
    sys.exit("Definí DATABASE_URL.")

with psycopg.connect(url) as con:
    d = R.cargar(con)
    x = R.alquileres_con_variables(d)

    # 1. Las etiquetas son las incidencias de falla de la base (y coinciden con la verdad simulada)
    with gzip.open(RAIZ / "data" / "verdad_exposicion.csv.gz", "rt") as f:
        v = pd.read_csv(f)
    m = x.merge(v[["detalle_id", "hubo_falla", "edad_anios", "atraso_max"]], on="detalle_id", suffixes=("", "_v"))
    comprobar("una fila por alquiler devuelto", len(x) == len(d["alquileres"]) == len(v))
    comprobar("la etiqueta coincide con la verdad simulada", (m["falla"] == m["hubo_falla"]).all())

    # 2. Las variables, calculadas solo con el pasado, reproducen lo que usó el simulador
    comprobar("edad reproduce la verdad", np.corrcoef(m["edad"], m["edad_anios"])[0, 1] > 0.999)
    r = np.corrcoef(m["atraso_max"], m["atraso_max_v"])[0, 1]
    comprobar("atraso de mantenimiento reproduce la verdad", r > 0.9, f"(correlación {r:.3f})")

    # 3. Sin filtraciones: ninguna variable depende de lo que ocurre después de t
    corte = pd.Timestamp("2026-01-01", tz="UTC")
    a = R.variables(d, pd.DataFrame({"bicicleta_id": [1, 2], "t": [corte, corte]}))
    d2 = dict(d)
    d2["usos"] = d["usos"][d["usos"]["devuelta_en"] <= corte]
    d2["servicios"] = d["servicios"][d["servicios"]["cerrada_en"] <= corte]
    d2["horas_final"] = d["horas_final"] - d["usos"][d["usos"]["devuelta_en"] > corte].groupby("bicicleta_id")["horas"].sum().reindex(d["horas_final"].index, fill_value=0.0)
    b = R.variables(d2, pd.DataFrame({"bicicleta_id": [1, 2], "t": [corte, corte]}))
    cols = R.VARS_TASA + ["horas_acum", "ritmo_ef"]
    comprobar("las variables no cambian si se borra el futuro", np.allclose(a[cols].values, b[cols].values))

    # 4. Probabilidades guardadas
    p = R.leer(con, "SELECT bicicleta_id, sistema, probabilidad, horizonte_dias FROM prediccion_mantenimiento "
                    "WHERE modelo_version LIKE 'tasa-poisson-%'")
    comprobar("hay predicciones guardadas (correr con --escribir)", len(p) > 0)
    if len(p):
        pr = p["probabilidad"].astype(float)
        comprobar("probabilidades entre 0 y 1", ((pr >= 0) & (pr <= 1)).all())
        tot = p[p["sistema"].isna()].set_index("bicicleta_id")["probabilidad"].astype(float)
        mx = p[p["sistema"].notna()].groupby("bicicleta_id")["probabilidad"].apply(lambda s: s.astype(float).max())
        comprobar("el riesgo total no es menor que el de ningún sistema", (tot.reindex(mx.index) + 1e-3 >= mx).all())
        vivas = R.leer(con, "SELECT id FROM bicicleta WHERE fecha_baja IS NULL")["id"]
        comprobar("una predicción total por bicicleta activa", set(tot.index) == set(vivas))

print("\n" + ("TODO OK" if not fallos else f"{len(fallos)} FALLO(S): {fallos}"))
sys.exit(1 if fallos else 0)
