#!/usr/bin/env python3
"""Fase 2: modelo de riesgo de falla por bicicleta y sistema.

Pregunta que responde: "¿esta bicicleta va a tener una FALLA en los próximos
`horizonte` días?". Se arma un panel con una foto semanal de cada bicicleta,
usando solo lo que el negocio sabe en ese momento (edad, horas de uso, ritmo de
uso reciente y atraso de cada tarea del plan de mantenimiento). La fragilidad
oculta y las columnas de data/verdad_* NO se usan para entrenar: solo para
evaluar qué tan cerca queda el modelo del proceso verdadero.

Uso:
    DATABASE_URL=postgresql:///bicis python3 modelo/riesgo_falla.py
    DATABASE_URL=... python3 modelo/riesgo_falla.py --escribir   # guarda en prediccion_mantenimiento
    DATABASE_URL=... python3 modelo/riesgo_falla.py --solo-puntuar --escribir   # modo desatendido (job diario)

El modo desatendido no evalúa ni usa los archivos de la verdad simulada: reentrena con todo lo que hay en la
base y agrega las predicciones de hoy. Conserva las de días anteriores, así que se puede correr todos los días.
"""
import argparse
import gzip
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression, PoissonRegressor
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parent.parent
SISTEMAS = ["TRANSMISION", "FRENOS", "NEUMATICOS", "CUADRO", "SUSPENSION"]
VERSION = "v1"
SEMILLA = 7


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def leer(con, sql):
    with con.cursor() as cur:
        cur.execute(sql)
        cols = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def cargar(con):
    d = {}
    d["bicis"] = leer(con, """
        SELECT b.id AS bicicleta_id, b.tipo_bicicleta_id AS tipo, b.fecha_alta, b.fecha_baja, b.horas_uso AS horas_final
        FROM bicicleta b""")
    d["plan"] = leer(con, """
        SELECT id AS plan_id, tipo_bicicleta_id AS tipo, sistema, cada_horas, cada_dias
        FROM plan_mantenimiento WHERE activo""")
    d["servicios"] = leer(con, """
        SELECT o.bicicleta_id, o.plan_id, o.cerrada_en, o.horas_uso
        FROM orden_mantenimiento o JOIN estado_orden e ON e.id = o.estado_id
        WHERE e.codigo = 'CERRADA' AND o.plan_id IS NOT NULL AND o.horas_uso IS NOT NULL
        ORDER BY o.bicicleta_id, o.plan_id, o.cerrada_en""")
    d["usos"] = leer(con, """
        SELECT bicicleta_id, devuelta_en, round(segundos_uso / 3600.0, 2)::float AS horas,
               CASE modalidad WHEN 'DIA' THEN 6.0 * ceil(segundos_uso / 86400.0)
                              ELSE least(segundos_uso / 3600.0, 8.0) END AS horas_ef
        FROM alquiler_detalle WHERE devuelta_en IS NOT NULL AND anulado_en IS NULL
        ORDER BY bicicleta_id, devuelta_en""")
    d["usos"]["horas_ef"] = d["usos"]["horas_ef"].astype(float)
    d["alquileres"] = leer(con, """
        SELECT d.id AS detalle_id, d.bicicleta_id, d.salida_real AS t,
               CASE d.modalidad WHEN 'DIA' THEN 6.0 * ceil(d.segundos_uso / 86400.0)
                                ELSE least(d.segundos_uso / 3600.0, 8.0) END AS horas_ef,
               EXISTS (SELECT 1 FROM incidencia i WHERE i.detalle_id = d.id AND i.tipo = 'FALLA') AS falla,
               COALESCE((SELECT array_agg(DISTINCT COALESCE(i.sistema, 'OTRO')) FROM incidencia i
                          WHERE i.detalle_id = d.id AND i.tipo = 'FALLA'), '{}') AS sistemas
        FROM alquiler_detalle d WHERE d.devuelta_en IS NOT NULL AND d.anulado_en IS NULL""")
    d["alquileres"]["t"] = pd.to_datetime(d["alquileres"]["t"], utc=True)
    d["alquileres"]["horas_ef"] = d["alquileres"]["horas_ef"].astype(float).clip(lower=0.25)
    d["alquileres"]["falla"] = d["alquileres"]["falla"].astype(int)
    d["fallas"] = leer(con, """
        SELECT bicicleta_id, ocurrida_en, COALESCE(sistema, 'OTRO') AS sistema
        FROM incidencia WHERE tipo = 'FALLA' ORDER BY bicicleta_id, ocurrida_en""")
    for k, col in [("servicios", "cerrada_en"), ("usos", "devuelta_en"), ("fallas", "ocurrida_en")]:
        d[k][col] = pd.to_datetime(d[k][col], utc=True)
    d["bicis"]["fecha_alta"] = pd.to_datetime(d["bicis"]["fecha_alta"], utc=True)
    d["bicis"]["fecha_baja"] = pd.to_datetime(d["bicis"]["fecha_baja"], utc=True)
    d["horas_final"] = d["bicis"].set_index("bicicleta_id")["horas_final"].astype(float)
    return d


# ---------------------------------------------------------------------------
# Panel: una fila por (bicicleta, semana)
# ---------------------------------------------------------------------------
def variables(d, pares):
    """Variables conocidas en el instante t para cada par (bicicleta_id, t) de `pares`.

    Solo usa el pasado de t: edad, horas acumuladas, ritmo de uso reciente y atraso
    de cada tarea del plan (0 = al día, 1 = el doble del intervalo).
    """
    filas = []
    plan_por_tipo = {t: g for t, g in d["plan"].groupby("tipo")}
    bicis = d["bicis"].set_index("bicicleta_id")
    for bid, grupo in pares.groupby("bicicleta_id"):
        b = bicis.loc[bid]
        usos = d["usos"][d["usos"]["bicicleta_id"] == bid]
        t_uso, h_uso = usos["devuelta_en"].values, usos["horas"].values
        acum = np.concatenate([[0.0], np.cumsum(h_uso)])
        acum_ef = np.concatenate([[0.0], np.cumsum(usos["horas_ef"].values)])
        plan = plan_por_tipo.get(b.tipo)
        serv = d["servicios"][d["servicios"]["bicicleta_id"] == bid]
        # horas con las que la bicicleta ya llegaba antes del primer alquiler registrado
        horas_alta = d["horas_final"][bid] - acum[-1]
        for t in grupo["t"]:
            i = np.searchsorted(t_uso, t.to_datetime64(), side="right")
            horas_t = horas_alta + acum[i]
            fila = {"bicicleta_id": bid, "t": t, "tipo": b.tipo,
                    "edad": (t - b.fecha_alta).days / 365.25, "horas_acum": horas_t}
            for dias in (30, 90):
                j = np.searchsorted(t_uso, (t - pd.Timedelta(days=dias)).to_datetime64(), side="right")
                fila[f"horas_{dias}d"] = acum[i] - acum[j]
                fila[f"usos_{dias}d"] = i - j
                fila[f"horas_ef_{dias}d"] = acum_ef[i] - acum_ef[j]
            fila["verano"] = int(t.month in (11, 12, 1, 2, 3))
            atrasos = {s: 0.0 for s in SISTEMAS}
            vencidas, dias_desde = 0, []
            if plan is not None:
                for p in plan.itertuples():
                    s_p = serv[(serv["plan_id"] == p.plan_id) & (serv["cerrada_en"] <= t)]
                    if len(s_p):
                        ult_fecha, ult_horas = s_p.iloc[-1]["cerrada_en"], float(s_p.iloc[-1]["horas_uso"])
                    else:
                        ult_fecha, ult_horas = b.fecha_alta, horas_alta
                    r_h = (horas_t - ult_horas) / p.cada_horas if p.cada_horas else 0.0
                    r_d = (t - ult_fecha).days / p.cada_dias if p.cada_dias else 0.0
                    atraso = min(max(max(r_h, r_d) - 1.0, 0.0), 1.5)
                    dias_desde.append((t - ult_fecha).days)
                    vencidas += atraso > 0
                    if p.sistema in atrasos:
                        atrasos[p.sistema] = max(atrasos[p.sistema], atraso)
            for s in SISTEMAS:
                fila[f"atraso_{s}"] = atrasos[s]
            fila["atraso_max"] = max(atrasos.values())
            fila["atraso_suma"] = sum(atrasos.values())
            fila["tareas_vencidas"] = vencidas
            fila["dias_desde_servicio"] = max(dias_desde) if dias_desde else 0
            filas.append(fila)
    v = pd.DataFrame(filas)
    v["ritmo_uso"] = v["horas_90d"] / 90.0
    v["ritmo_ef"] = v["horas_ef_90d"] / 90.0  # horas efectivas (las que exponen a falla) por día
    for k in range(1, 7):
        v[f"tipo_{k}"] = (v["tipo"] == k).astype(int)
    return v


def construir_panel(d, desde, hasta, horizonte, paso_dias=7):
    """Una foto cada `paso_dias` por bicicleta activa, con la etiqueta de falla en (t, t + horizonte].

    Si t + horizonte supera el último dato, la etiqueta es NaN (sirve para puntuar "hoy").
    """
    ultimo_dato = max(d["usos"]["devuelta_en"].max(), d["fallas"]["ocurrida_en"].max())
    desde, hasta = pd.Timestamp(desde), pd.Timestamp(hasta)
    desde = desde.tz_localize("UTC") if desde.tzinfo is None else desde.tz_convert("UTC")
    hasta = hasta.tz_localize("UTC") if hasta.tzinfo is None else hasta.tz_convert("UTC")
    fechas = pd.date_range(desde, hasta, freq=f"{paso_dias}D")
    pares = []
    for b in d["bicis"].itertuples():
        for t in fechas:
            if t >= b.fecha_alta and not (pd.notna(b.fecha_baja) and t >= b.fecha_baja):
                pares.append((b.bicicleta_id, t))
    panel = variables(d, pd.DataFrame(pares, columns=["bicicleta_id", "t"]))
    y = np.full(len(panel), np.nan)
    ys = {s: np.full(len(panel), np.nan) for s in SISTEMAS}
    fallas = {b: g for b, g in d["fallas"].groupby("bicicleta_id")}
    for n, (bid, t) in enumerate(zip(panel["bicicleta_id"], panel["t"])):
        t_fin = t + pd.Timedelta(days=horizonte)
        if t_fin > ultimo_dato:
            continue
        g = fallas.get(bid)
        ventana = g[(g["ocurrida_en"] > t) & (g["ocurrida_en"] <= t_fin)] if g is not None else None
        y[n] = 0 if ventana is None else int(len(ventana) > 0)
        for s in SISTEMAS:
            ys[s][n] = 0 if ventana is None else int((ventana["sistema"] == s).any())
    panel["falla"] = y
    for s in SISTEMAS:
        panel[f"falla_{s}"] = ys[s]
    # horas efectivas que de hecho se usaron en la ventana (para entrenar el pronóstico de uso)
    acum = {b: (g["devuelta_en"].values, np.concatenate([[0.0], np.cumsum(g["horas_ef"].values)]))
            for b, g in d["usos"].groupby("bicicleta_id")}
    h_fut = np.full(len(panel), np.nan)
    for n, (bid, t) in enumerate(zip(panel["bicicleta_id"], panel["t"])):
        t_fin = t + pd.Timedelta(days=horizonte)
        if t_fin > ultimo_dato or bid not in acum:
            continue
        t_uso, c = acum[bid]
        h_fut[n] = c[np.searchsorted(t_uso, t_fin.to_datetime64(), side="right")] - \
            c[np.searchsorted(t_uso, t.to_datetime64(), side="right")]
    panel["horas_ef_futuras"] = h_fut
    return panel


def indice_mensual(d, limite):
    """Horas efectivas por bicicleta activa y por día, según el mes del año, con datos anteriores a `limite`."""
    u = d["usos"][d["usos"]["devuelta_en"] < limite]
    dias = pd.date_range(u["devuelta_en"].min().normalize(), limite.normalize() - pd.Timedelta(days=1), freq="D")
    alta, baja = d["bicis"]["fecha_alta"], d["bicis"]["fecha_baja"]
    activas = np.array([((alta <= dia) & (baja.isna() | (baja > dia))).sum() for dia in dias])
    horas = u.groupby(u["devuelta_en"].dt.normalize())["horas_ef"].sum().reindex(dias, fill_value=0.0).values
    tabla = pd.DataFrame({"mes": dias.month, "h": horas, "a": activas}).groupby("mes").sum()
    idx = (tabla["h"] / tabla["a"].clip(lower=1)).reindex(range(1, 13))
    return idx.fillna(idx.mean())


def agregar_pronostico(panel, d, limite, horizonte):
    """Agrega el ritmo de la flota y el cociente estacional (próximo horizonte / últimos 90 días)."""
    idx = indice_mensual(d, limite)
    def razon(t):
        fut = pd.date_range(t + pd.Timedelta(days=1), periods=horizonte, freq="D")
        pas = pd.date_range(t - pd.Timedelta(days=90), periods=90, freq="D")
        return idx[fut.month].mean() / idx[pas.month].mean()
    r = {t: razon(t) for t in panel["t"].unique()}
    out = panel.copy()
    out["ratio_est"] = out["t"].map(r)
    out["ritmo_flota"] = out.groupby(["t", "tipo"])["ritmo_ef"].transform("mean")
    out["h_base_bici"] = out["ritmo_ef"] * out["ratio_est"] * horizonte
    out["h_base_flota"] = out["ritmo_flota"] * out["ratio_est"] * horizonte
    return out


def modelo_uso(entrenamiento):
    """Pronóstico de horas efectivas del próximo horizonte (coeficientes no negativos, sin intercepto)."""
    m = LinearRegression(positive=True, fit_intercept=False)
    e = entrenamiento.dropna(subset=["horas_ef_futuras"])
    return m.fit(e[["h_base_bici", "h_base_flota"]], e["horas_ef_futuras"])


def verdad_ventana(panel, horizonte):
    """Probabilidad verdadera de falla en la ventana, según el proceso simulado
    (1 - prod(1 - prob_falla) de los alquileres que de hecho ocurren en ella)."""
    ruta = RAIZ / "data" / "verdad_exposicion.csv.gz"
    with gzip.open(ruta, "rt") as f:
        v = pd.read_csv(f, parse_dates=["fecha"])
    v["fecha"] = v["fecha"].dt.tz_localize("UTC")
    v["l"] = np.log1p(-v["prob_falla"].clip(upper=0.999999))
    out = np.zeros(len(panel))
    for b, g in panel.groupby("bicicleta_id"):
        vv = v[v["bicicleta_id"] == b].sort_values("fecha")
        f = vv["fecha"].values
        c = np.concatenate([[0.0], np.cumsum(vv["l"].values)])
        t0 = g["t"].values.astype("datetime64[ns]")
        t1 = (g["t"] + pd.Timedelta(days=horizonte)).values.astype("datetime64[ns]")
        a = np.searchsorted(f, t0, side="right")
        z = np.searchsorted(f, t1, side="right")
        out[panel.index.get_indexer(g.index)] = 1 - np.exp(c[z] - c[a])
    return out


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
# Para el panel de 30 días (modelo directo, sirve de comparación).
VARS_BASE = ["edad", "horas_acum", "horas_30d", "horas_90d", "usos_90d", "ritmo_uso",
             "atraso_max", "atraso_suma", "tareas_vencidas", "dias_desde_servicio"] + \
            [f"atraso_{s}" for s in SISTEMAS] + [f"tipo_{k}" for k in range(1, 7)]
# Para la tasa de falla por hora de uso (modelo principal).
VARS_TASA = ["edad", "atraso_max", "atraso_suma", "verano"] + \
            [f"atraso_{s}" for s in SISTEMAS] + [f"tipo_{k}" for k in range(1, 7)]


def modelos():
    return {
        "logistica": make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000)),
        "gradiente": HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                    min_samples_leaf=40, l2_regularization=1.0,
                                                    random_state=SEMILLA),
    }


def modelo_tasa(tipo):
    """Regresión de Poisson de la tasa por hora (y / horas, con peso = horas)."""
    if tipo == "poisson":
        return make_pipeline(StandardScaler(), PoissonRegressor(alpha=1e-3, max_iter=1000))
    return HistGradientBoostingRegressor(loss="poisson", max_depth=3, learning_rate=0.05, max_iter=150,
                                         min_samples_leaf=60, l2_regularization=1.0, random_state=SEMILLA)


def ajustar_tasa(tipo, X, y, h):
    m = modelo_tasa(tipo)
    if tipo == "poisson":
        m.fit(X, y / h, poissonregressor__sample_weight=h)
    else:
        m.fit(X, y / h, sample_weight=h)
    return m


def metricas(y, p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    top = p >= np.quantile(p, 0.9)
    return {"auc": roc_auc_score(y, p), "ap": average_precision_score(y, p),
            "log_loss": log_loss(y, p), "brier": brier_score_loss(y, p),
            "lift_decil_superior": float(y[top].mean() / y.mean()) if y.mean() > 0 else float("nan")}


def alquileres_con_variables(d, con_verdad=True):
    a = d["alquileres"]
    v = variables(d, a[["bicicleta_id", "t"]].drop_duplicates())
    x = a.merge(v, on=["bicicleta_id", "t"], how="left")
    assert x[VARS_TASA].notna().all().all() and len(x) == len(a), "variables incompletas"
    if con_verdad:  # solo para evaluar contra el simulador; en producción no existe
        ruta = RAIZ / "data" / "verdad_exposicion.csv.gz"
        with gzip.open(ruta, "rt") as f:
            x = x.merge(pd.read_csv(f)[["detalle_id", "prob_falla", "tasa_por_hora"]], on="detalle_id")
    return x


def evaluar_alquileres(x, corte):
    """Nivel alquiler: ¿qué probabilidad tiene ESTE alquiler de terminar en una falla?"""
    corte = pd.Timestamp(corte, tz="UTC")
    tr, te = x[x["t"] <= corte], x[x["t"] > corte]
    y_tr, y_te, h_tr, h_te = tr["falla"].values, te["falla"].values, tr["horas_ef"].values, te["horas_ef"].values
    res = {"filas_train": len(tr), "filas_test": len(te), "fallas_train": int(y_tr.sum()),
           "fallas_test": int(y_te.sum()), "tasa_test": float(y_te.mean())}
    tasa_global = y_tr.sum() / h_tr.sum()
    pred = {"base_tasa_global": 1 - np.exp(-tasa_global * h_te)}
    tasa_tipo = tr.groupby("tipo").apply(lambda g: g["falla"].sum() / g["horas_ef"].sum())
    pred["base_tasa_por_tipo"] = 1 - np.exp(-te["tipo"].map(tasa_tipo).fillna(tasa_global).values * h_te)
    r_tr = tr["atraso_max"] > 0
    t_v = tr.loc[r_tr, "falla"].sum() / tr.loc[r_tr, "horas_ef"].sum()
    t_n = tr.loc[~r_tr, "falla"].sum() / tr.loc[~r_tr, "horas_ef"].sum()
    pred["base_regla_vencida"] = 1 - np.exp(-np.where(te["atraso_max"] > 0, t_v, t_n) * h_te)
    tasas = {}
    for nombre in ("poisson", "gradiente"):
        m = ajustar_tasa(nombre, tr[VARS_TASA], y_tr, h_tr)
        tasas[nombre] = np.clip(m.predict(te[VARS_TASA]), 1e-6, None)
        pred[nombre] = 1 - np.exp(-tasas[nombre] * h_te)
    pred["verdad_simulada"] = te["prob_falla"].values
    res["modelos"] = {k: metricas(y_te, v) for k, v in pred.items()}
    res["correlacion_tasa_con_verdad"] = {k: float(np.corrcoef(v, te["tasa_por_hora"])[0, 1]) for k, v in tasas.items()}
    return res


def evaluar_sistemas(x, corte):
    """Nivel alquiler y sistema: ¿en cuál sistema es más probable la falla?"""
    corte = pd.Timestamp(corte, tz="UTC")
    out = {}
    for s in SISTEMAS:
        x_s = x.copy()
        x_s["y"] = x_s["sistemas"].apply(lambda l: int(s in l))
        x_s["atraso_sis"] = x_s[f"atraso_{s}"]
        tr, te = x_s[x_s["t"] <= corte], x_s[x_s["t"] > corte]
        if te["y"].sum() < 5:
            continue
        v = VARS_TASA + ["atraso_sis"]
        m = ajustar_tasa("poisson", tr[v], tr["y"].values, tr["horas_ef"].values)
        p = 1 - np.exp(-np.clip(m.predict(te[v]), 1e-6, None) * te["horas_ef"].values)
        r = tr["atraso_sis"] > 0
        t_v = tr.loc[r, "y"].sum() / tr.loc[r, "horas_ef"].sum()
        t_n = tr.loc[~r, "y"].sum() / max(tr.loc[~r, "horas_ef"].sum(), 1e-9)
        base = 1 - np.exp(-np.where(te["atraso_sis"] > 0, t_v, t_n) * te["horas_ef"].values)
        out[s] = {"fallas_test": int(te["y"].sum()),
                  "auc_modelo": float(roc_auc_score(te["y"], p)),
                  "auc_regla_vencida": float(roc_auc_score(te["y"], base))}
    return out


def evaluar_panel(panel, x, horizonte, corte):
    """Nivel bicicleta-semana (lo que se guarda en prediccion_mantenimiento): ¿falla en 30 días?

    Compara el modelo directo con la tasa por hora llevada a 30 días con el uso pronosticado.
    """
    corte = pd.Timestamp(corte, tz="UTC")
    etiquetado = panel.dropna(subset=["falla"]).copy()
    tr = etiquetado[etiquetado["t"] <= corte - pd.Timedelta(days=horizonte)]
    te = etiquetado[etiquetado["t"] > corte]
    y_tr, y_te = tr["falla"].astype(int).values, te["falla"].astype(int).values
    res = {"filas_train": len(tr), "filas_test": len(te), "tasa_train": float(y_tr.mean()),
           "tasa_test": float(y_te.mean())}
    pred = {}
    pred["base_tasa_por_tipo"] = te["tipo"].map(tr.groupby("tipo")["falla"].mean()).fillna(y_tr.mean()).values
    pred["base_regla_vencida"] = np.where(te["atraso_max"].values > 0,
                                          tr.loc[tr["atraso_max"] > 0, "falla"].mean(),
                                          tr.loc[tr["atraso_max"] <= 0, "falla"].mean())
    for nombre, m in modelos().items():
        m.fit(tr[VARS_BASE], y_tr)
        pred[f"directo_{nombre}"] = m.predict_proba(te[VARS_BASE])[:, 1]
    # tasa por hora x horas pronosticadas
    uso = modelo_uso(tr)
    h_ingenuo = te["ritmo_ef"].values * horizonte          # ritmo de los últimos 90 días, sin estación
    h_pron = uso.predict(te[["h_base_bici", "h_base_flota"]])
    xa = x[x["t"] <= corte - pd.Timedelta(days=horizonte)]
    for nombre in ("poisson", "gradiente"):
        m = ajustar_tasa(nombre, xa[VARS_TASA], xa["falla"].values, xa["horas_ef"].values)
        tasa = np.clip(m.predict(te[VARS_TASA]), 1e-6, None)
        pred[f"tasa_{nombre}_uso_ingenuo"] = 1 - np.exp(-tasa * h_ingenuo)
        pred[f"tasa_{nombre}"] = 1 - np.exp(-tasa * h_pron)
        if nombre == "poisson":
            pred["tasa_poisson_uso_real_(techo)"] = 1 - np.exp(-tasa * te["horas_ef_futuras"].values)
    pred["verdad_simulada"] = te["p_verdad"].values
    res["modelos"] = {k: metricas(y_te, v) for k, v in pred.items()}
    res["correlacion_con_verdad"] = {k: float(np.corrcoef(v, te["p_verdad"])[0, 1])
                                     for k, v in pred.items() if k != "verdad_simulada"}
    real = te["horas_ef_futuras"].values
    res["pronostico_de_uso"] = {
        "horas_reales_media": float(real.mean()),
        "horas_ingenuo_media": float(h_ingenuo.mean()), "corr_ingenuo": float(np.corrcoef(h_ingenuo, real)[0, 1]),
        "horas_pronostico_media": float(h_pron.mean()), "corr_pronostico": float(np.corrcoef(h_pron, real)[0, 1]),
        "coeficientes": {"bici": float(uso.coef_[0]), "flota": float(uso.coef_[1])}}
    # incertidumbre: remuestreo de bicicletas (las ventanas semanales de una misma bicicleta se solapan)
    rng = np.random.default_rng(SEMILLA)
    bicis = te["bicicleta_id"].values
    por_bici = {b: np.flatnonzero(bicis == b) for b in np.unique(bicis)}
    ids = np.array(list(por_bici))
    difs = {c: [] for c in ("directo_logistica", "base_regla_vencida")}
    for _ in range(400):
        ix = np.concatenate([por_bici[b] for b in rng.choice(ids, len(ids))])
        if y_te[ix].min() == y_te[ix].max():
            continue
        a_ = roc_auc_score(y_te[ix], pred["tasa_poisson"][ix])
        for c in difs:
            difs[c].append(a_ - roc_auc_score(y_te[ix], pred[c][ix]))
    res["auc_tasa_poisson_menos"] = {c: {"media": float(np.mean(v)), "ic95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))]}
                                      for c, v in difs.items()}
    res["calibracion_media"] = {k: float(v.mean()) for k, v in pred.items()} | {"observada": float(y_te.mean())}
    return res


# ---------------------------------------------------------------------------
# Puntuar hoy y guardar
# ---------------------------------------------------------------------------
def sistemas_con_tarea(d):
    return {(r.tipo, r.sistema) for r in d["plan"].itertuples()}


def puntuar_hoy(d, x, panel, horizonte, ahora):
    """Ajusta con todos los datos y devuelve la probabilidad de falla en `horizonte` días para cada
    bicicleta activa: total (sistema NULL) y por sistema con tarea en su plan."""
    activas = d["bicis"][(d["bicis"]["fecha_baja"].isna()) & (d["bicis"]["fecha_alta"] <= ahora)]
    hoy = variables(d, pd.DataFrame({"bicicleta_id": activas["bicicleta_id"], "t": ahora}))
    hoy = agregar_pronostico(hoy, d, ahora, horizonte)
    etiquetado = agregar_pronostico(panel.dropna(subset=["falla"]), d, ahora, horizonte)
    horas_esperadas = modelo_uso(etiquetado).predict(hoy[["h_base_bici", "h_base_flota"]])
    m = ajustar_tasa("poisson", x[VARS_TASA], x["falla"].values, x["horas_ef"].values)
    p_total = 1 - np.exp(-np.clip(m.predict(hoy[VARS_TASA]), 1e-6, None) * horas_esperadas)
    filas = [pd.DataFrame({"bicicleta_id": hoy["bicicleta_id"], "sistema": None, "probabilidad": p_total})]
    tiene = sistemas_con_tarea(d)
    for s in SISTEMAS:
        xs = x.copy()
        xs["y"] = xs["sistemas"].apply(lambda l: int(s in l))
        xs["atraso_sis"] = xs[f"atraso_{s}"]
        v = VARS_TASA + ["atraso_sis"]
        ms = ajustar_tasa("poisson", xs[v], xs["y"].values, xs["horas_ef"].values)
        h = hoy.assign(atraso_sis=hoy[f"atraso_{s}"])
        ok = np.array([(t, s) in tiene for t in h["tipo"]])
        p = 1 - np.exp(-np.clip(ms.predict(h[v]), 1e-6, None) * horas_esperadas)
        filas.append(pd.DataFrame({"bicicleta_id": h["bicicleta_id"][ok], "sistema": s, "probabilidad": p[ok]}))
    return pd.concat(filas, ignore_index=True)


def fecha_de_calculo(ultimo, fecha=None, hoy=None, dias_maximos=7):
    """Fecha (medianoche UTC) a la que se calculan las predicciones.

    Por defecto es hoy. Si el último dato de la base tiene más de `dias_maximos` días, hoy no sirve (el ritmo de
    uso daría casi cero y las predicciones serían engañosas): se calcula al día siguiente del último dato y se avisa.
    """
    if fecha:
        return pd.Timestamp(fecha, tz="UTC")
    hoy = (hoy or pd.Timestamp.now(tz="UTC")).normalize()
    if (hoy - ultimo.normalize()).days > dias_maximos:
        print(f"AVISO: el último dato es del {ultimo.date()}, hace más de {dias_maximos} días; "
              "se calcula a partir de esa fecha.", file=sys.stderr)
        return ultimo.normalize() + pd.Timedelta(days=1)
    return max(hoy, ultimo.normalize())


def validar(pred, d, ahora):
    """Aborta antes de escribir si las predicciones no son confiables."""
    p = pred["probabilidad"].astype(float)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise SystemExit("Predicciones inválidas (NaN o fuera de [0, 1]): no se escribe nada.")
    activas = set(d["bicis"][(d["bicis"]["fecha_baja"].isna()) & (d["bicis"]["fecha_alta"] <= ahora)]["bicicleta_id"])
    totales = set(pred[pred["sistema"].isna()]["bicicleta_id"])
    if not activas or totales != activas:
        raise SystemExit(f"Faltan o sobran bicicletas en las predicciones ({len(totales)} de {len(activas)}): "
                         "no se escribe nada.")


def guardar(con, pred, horizonte, ahora):
    """Agrega las predicciones de `ahora`. Conserva las de fechas anteriores (historial para medir el
    modelo con el tiempo); repetir la corrida del mismo día reemplaza solo las de ese día."""
    version = f"tasa-poisson-{VERSION}"
    with con.transaction():
        with con.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_xact_lock(734210)")
            if not cur.fetchone()[0]:
                print("Hay otra corrida en curso: se omite esta.")
                return 0, version
            cur.execute("DELETE FROM prediccion_mantenimiento WHERE modelo_version = %s AND calculada_en = %s",
                        (version, ahora.to_pydatetime()))
            cur.executemany(
                "INSERT INTO prediccion_mantenimiento (bicicleta_id, calculada_en, horizonte_dias, sistema, probabilidad, modelo_version)"
                " VALUES (%s, %s, %s, %s, %s, %s)",
                [(int(r.bicicleta_id), ahora.to_pydatetime(), horizonte, r.sistema,
                  round(float(min(max(r.probabilidad, 0.0), 1.0)), 4), version) for r in pred.itertuples()])
    return len(pred), version


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--horizonte", type=int, default=30, help="días hacia adelante (por defecto 30)")
    ap.add_argument("--corte", default="2026-03-01", help="fecha de corte train/test (AAAA-MM-DD)")
    ap.add_argument("--escribir", action="store_true", help="guardar predicciones de hoy en la base")
    ap.add_argument("--solo-puntuar", action="store_true",
                    help="modo desatendido: no evalúa ni toca resultados.json ni usa la verdad simulada")
    ap.add_argument("--fecha", help="fecha de cálculo AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--salida", default=str(RAIZ / "modelo" / "resultados.json"))
    a = ap.parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("Definí DATABASE_URL.")
    with psycopg.connect(url) as con:
        d = cargar(con)
        ultimo = max(d["usos"]["devuelta_en"].max(), d["fallas"]["ocurrida_en"].max())
        ahora = fecha_de_calculo(ultimo, a.fecha)
        x = alquileres_con_variables(d, con_verdad=not a.solo_puntuar)
        ultima_foto = ahora - pd.Timedelta(days=a.horizonte)
        panel = construir_panel(d, "2025-01-01", ultima_foto, a.horizonte)
        if not a.solo_puntuar:
            panel["p_verdad"] = verdad_ventana(panel, a.horizonte)
            panel_eval = agregar_pronostico(panel, d, pd.Timestamp(a.corte, tz="UTC"), a.horizonte)
            res = {"alquiler": evaluar_alquileres(x, a.corte),
                   "por_sistema": evaluar_sistemas(x, a.corte),
                   "panel_30d": evaluar_panel(panel_eval, x, a.horizonte, a.corte),
                   "parametros": {"horizonte_dias": a.horizonte, "corte": a.corte, "primera_foto": "2025-01-01",
                                  "ultima_foto": str(ultima_foto.date()), "paso_dias": 7,
                                  "variables_tasa": VARS_TASA, "variables_directo": VARS_BASE}}
            Path(a.salida).write_text(json.dumps(res, indent=2, ensure_ascii=False))
            print(json.dumps({k: v for k, v in res.items() if k != "parametros"}, indent=2, ensure_ascii=False))
        if a.escribir:
            pred = puntuar_hoy(d, x, panel, a.horizonte, ahora)
            validar(pred, d, ahora)
            n, v = guardar(con, pred, a.horizonte, ahora)
            mayores = pred[pred["sistema"].isna()].merge(d["bicis"][["bicicleta_id"]], on="bicicleta_id") \
                .nlargest(3, "probabilidad")
            print(f"Guardadas {n} predicciones ({v}) calculadas al {ahora.date()} con datos hasta {ultimo.date()}.")
            print("Mayor riesgo total: " + ", ".join(f"bici {int(r.bicicleta_id)} {r.probabilidad:.0%}"
                                                     for r in mayores.itertuples()))


if __name__ == "__main__":
    main()
