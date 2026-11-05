"""Carga el esquema ya creado con los datos de demostración de Bicis sustentables, sin necesitar `psql`.

Pensado para Windows o para quien no tiene el cliente de PostgreSQL. Usa la misma
biblioteca que la aplicación (psycopg).

    pip install "psycopg[binary]"
    DATABASE_URL en el entorno (PowerShell:  $env:DATABASE_URL = '...')
    python scripts/cargar_demo.py

- La base debe tener db/schema.sql cargado y NO tener bicicletas ni alquileres.
- Conserva los usuarios que ya existan (por ejemplo tu administrador, con su
  contraseña y roles): los saca antes de cargar y los vuelve a crear al final.
- Todo ocurre en una sola transacción: si algo falla, no queda nada a medias.
- Los datos de demostración incluyen 8 usuarios ficticios SIN contraseña, que
  no pueden ingresar a la aplicación.
"""
import gzip
import os
import sys
import time
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SEMILLA = Path(__file__).resolve().parent.parent / "data" / "seed.sql.gz"
LOTE = 400  # sentencias por viaje al servidor: pocas idas y vueltas aunque la base esté lejos


def main():
    url = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATABASE_URL", "")).strip()
    if not url:
        sys.exit("Falta DATABASE_URL (variable de entorno o primer argumento).")
    if not SEMILLA.exists():
        sys.exit(f"No encuentro {SEMILLA}.")

    sentencias = []
    with gzip.open(SEMILLA, "rt", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("--") and linea not in ("BEGIN;", "COMMIT;", "ANALYZE;"):
                if not linea.endswith(";"):
                    sys.exit("El archivo de datos tiene una línea inesperada; no se carga nada.")
                sentencias.append(linea)
    print(f"{len(sentencias):,} sentencias a ejecutar.")

    with psycopg.connect(url, row_factory=dict_row, autocommit=False) as con:
        con.execute("SET statement_timeout = 0")
        for tabla in ("bicicleta", "alquiler", "ubicacion", "tipo_bicicleta"):
            if con.execute(f"SELECT count(*) AS n FROM {tabla}").fetchone()["n"]:
                sys.exit(f"La base ya tiene datos en {tabla}: este cargador es solo para una base vacía.")

        # Los usuarios existentes se apartan: la demo trae los suyos con ids fijos.
        usuarios = con.execute(
            """SELECT u.*, c.password_hash, c.debe_cambiar,
                      COALESCE((SELECT array_agg(rol_id) FROM usuario_rol WHERE usuario_id = u.id), '{}') AS roles
                 FROM usuario u LEFT JOIN credencial_acceso c ON c.usuario_id = u.id""").fetchall()
        if usuarios:
            print(f"Conservando {len(usuarios)} usuario(s) existente(s): "
                  + ", ".join(u["email"] for u in usuarios))
            con.execute("DELETE FROM credencial_acceso")
            con.execute("DELETE FROM usuario_rol")
            con.execute("DELETE FROM usuario")

        inicio = time.time()
        for i in range(0, len(sentencias), LOTE):
            con.execute("\n".join(sentencias[i:i + LOTE]))
            hecho = min(i + LOTE, len(sentencias))
            print(f"  {hecho:>6,} / {len(sentencias):,}  ({time.time() - inicio:.0f} s)", flush=True)

        for u in usuarios:
            nuevo = con.execute(
                """INSERT INTO usuario (nombre, apellido, email, activo, creado_en)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (u["nombre"], u["apellido"], u["email"], u["activo"], u["creado_en"])).fetchone()["id"]
            for rol in u["roles"]:
                con.execute("INSERT INTO usuario_rol VALUES (%s, %s)", (nuevo, rol))
            if u["password_hash"]:
                con.execute(
                    "INSERT INTO credencial_acceso (usuario_id, password_hash, debe_cambiar) VALUES (%s, %s, %s)",
                    (nuevo, u["password_hash"], u["debe_cambiar"]))
        con.commit()
        con.autocommit = True
        con.execute("ANALYZE")

        r = con.execute("""SELECT (SELECT count(*) FROM bicicleta) AS bicis,
                                  (SELECT count(*) FROM alquiler) AS alquileres,
                                  (SELECT count(*) FROM reserva) AS reservas,
                                  (SELECT count(*) FROM incidencia) AS incidencias,
                                  (SELECT count(*) FROM orden_mantenimiento) AS ordenes""").fetchone()
    print(f"Listo en {time.time() - inicio:.0f} s: {r['bicis']} bicicletas, {r['alquileres']:,} alquileres, "
          f"{r['reservas']:,} reservas, {r['incidencias']} incidencias, {r['ordenes']:,} órdenes de taller.")


if __name__ == "__main__":
    main()
