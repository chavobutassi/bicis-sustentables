"""Acceso a PostgreSQL con un pool de conexiones."""
from contextlib import contextmanager

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from . import config

pool = ConnectionPool(
    config.DATABASE_URL,
    min_size=1,
    max_size=8,
    kwargs={"row_factory": dict_row},
    open=False,
)


def abrir():
    pool.open(wait=True, timeout=30)


def cerrar():
    pool.close()


@contextmanager
def conexion():
    """Una transacción: confirma al salir bien, revierte si hay una excepción."""
    with pool.connection() as con:
        yield con


def consultar(sql, params=None):
    with conexion() as con:
        return con.execute(sql, params).fetchall()


def consultar_uno(sql, params=None):
    with conexion() as con:
        return con.execute(sql, params).fetchone()
