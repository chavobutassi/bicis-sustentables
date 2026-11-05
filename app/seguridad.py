"""Contraseñas, sesiones firmadas, CSRF y límite de intentos de acceso."""
import hmac
import secrets
import time
from collections import defaultdict, deque

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from itsdangerous import BadSignature, URLSafeTimedSerializer

from . import config

_hasher = PasswordHasher()
_serializador = URLSafeTimedSerializer(config.SECRET_KEY, salt="bicis-sesion")

COOKIE = "bicis_sesion"
MIN_LARGO_CLAVE = 12

# Hash de relleno: se verifica igual cuando el usuario no existe, para que el
# tiempo de respuesta no revele qué correos están registrados.
_HASH_RELLENO = _hasher.hash(secrets.token_urlsafe(16))


def hashear(clave: str) -> str:
    return _hasher.hash(clave)


def verificar(clave: str, hash_guardado: str | None) -> bool:
    try:
        return _hasher.verify(hash_guardado or _HASH_RELLENO, clave) and hash_guardado is not None
    except (VerifyMismatchError, InvalidHashError):
        return False


def validar_clave_nueva(clave: str) -> str | None:
    """Devuelve un mensaje de error, o None si la contraseña es aceptable."""
    if len(clave) < MIN_LARGO_CLAVE:
        return f"La contraseña debe tener al menos {MIN_LARGO_CLAVE} caracteres."
    if clave.lower() == clave or clave.upper() == clave or not any(c.isdigit() for c in clave):
        return "Usá mayúsculas, minúsculas y al menos un número."
    return None


def crear_cookie_sesion(usuario_id: int) -> str:
    return _serializador.dumps({"u": usuario_id, "csrf": secrets.token_urlsafe(24)})


def leer_cookie_sesion(valor: str | None) -> dict | None:
    if not valor:
        return None
    try:
        return _serializador.loads(valor, max_age=config.SESION_HORAS * 3600)
    except BadSignature:
        return None


def csrf_valido(sesion: dict, enviado: str | None) -> bool:
    return bool(enviado) and hmac.compare_digest(sesion["csrf"], enviado)


class LimiteIntentos:
    """Máximo de intentos fallidos por clave (IP + correo) dentro de una ventana."""

    def __init__(self, maximo=5, ventana_s=900):
        self.maximo, self.ventana = maximo, ventana_s
        self._fallos = defaultdict(deque)

    def _limpiar(self, clave):
        ahora, q = time.monotonic(), self._fallos[clave]
        while q and ahora - q[0] > self.ventana:
            q.popleft()
        return q

    def bloqueado(self, clave) -> bool:
        return len(self._limpiar(clave)) >= self.maximo

    def fallo(self, clave):
        self._limpiar(clave).append(time.monotonic())

    def exito(self, clave):
        self._fallos.pop(clave, None)
