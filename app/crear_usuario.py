"""Crea o restablece la contraseña de acceso de un usuario existente.

Uso:   python -m app.crear_usuario correo@ejemplo.test [--rol ADMIN]

Pide la contraseña por teclado (no queda en el historial de la terminal).
Al ingresar por primera vez la aplicación obliga a cambiarla.
Si el correo no existe se lo da de alta (hace falta --nombre y --apellido).
"""
import argparse
import getpass
import sys

from . import db, seguridad


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("email")
    p.add_argument("--rol", action="append", default=[], help="ADMIN, MOSTRADOR o TECNICO (repetible)")
    p.add_argument("--nombre")
    p.add_argument("--apellido")
    a = p.parse_args()
    email = a.email.strip().lower()

    clave = getpass.getpass("Contraseña temporal: ")
    if clave != getpass.getpass("Repetir: "):
        sys.exit("Las contraseñas no coinciden.")
    error = seguridad.validar_clave_nueva(clave)
    if error:
        sys.exit(error)

    db.abrir()
    try:
        with db.conexion() as con:
            u = con.execute("SELECT id FROM usuario WHERE lower(email) = %s", (email,)).fetchone()
            if not u:
                if not (a.nombre and a.apellido):
                    sys.exit("El usuario no existe: indicá --nombre y --apellido para crearlo.")
                u = con.execute(
                    "INSERT INTO usuario (nombre, apellido, email) VALUES (%s, %s, %s) RETURNING id",
                    (a.nombre, a.apellido, email)).fetchone()
            for rol in a.rol:
                r = con.execute("SELECT id FROM rol WHERE codigo = %s", (rol.upper(),)).fetchone()
                if not r:
                    sys.exit(f"Rol inexistente: {rol}")
                con.execute("INSERT INTO usuario_rol VALUES (%s, %s) ON CONFLICT DO NOTHING",
                            (u["id"], r["id"]))
            con.execute(
                """INSERT INTO credencial_acceso (usuario_id, password_hash, debe_cambiar)
                   VALUES (%s, %s, TRUE)
                   ON CONFLICT (usuario_id) DO UPDATE
                     SET password_hash = EXCLUDED.password_hash, debe_cambiar = TRUE, actualizada_en = now()""",
                (u["id"], seguridad.hashear(clave)))
        print(f"Listo: {email} deberá cambiar la contraseña al ingresar.")
    finally:
        db.cerrar()


if __name__ == "__main__":
    main()
