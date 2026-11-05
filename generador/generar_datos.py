#!/usr/bin/env python3
"""Generador de datos sintéticos para Bicis sustentables (solo biblioteca estándar).

Simula, evento por evento y en orden cronológico, dos temporadas de un negocio
ficticio de alquiler de bicicletas: reservas con seña, retiros en mostrador,
grupos con varias bicicletas, devoluciones con demora, cobros, daños, órdenes de
taller y mantenimiento preventivo con atrasos. Todo se escribe como sentencias
SQL que ejecutan las mismas reglas (triggers) que usaría la aplicación.

Los datos son ficticios: personas, documentos, teléfonos y correos inventados
(dominios reservados .test). Es determinista: misma semilla y fecha, mismo resultado.

La probabilidad de que una bicicleta sufra un daño durante un alquiler es:

    tasa/hora = base[tipo] · exp(0,12 · edad_en_años) · fragilidad[bicicleta]
                · exp(1,4 · min(atraso_del_mantenimiento, 1,2)) · (1,12 en verano)

donde el atraso es la fracción del intervalo del plan (en horas de uso o en
días) que lleva vencida la tarea más atrasada. Ese es el proceso que un modelo
debería poder descubrir. El sistema afectado depende de qué tarea está atrasada.

Uso:
    python3 generador/generar_datos.py --hasta 2026-11-04T12:00 --salida data/seed.sql.gz
"""
import argparse
import gzip
import heapq
import math
import random
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

TZ = timezone(timedelta(hours=-3))          # Argentina no usa horario de verano

# ---------------------------------------------------------------- parámetros
ESCALA_DEMANDA = 0.55                         # multiplica la demanda diaria (volumen total del conjunto)
INFLACION_MENSUAL = 0.028
SENIA_PORCENTAJE = Decimal("0.30")

# alquileres por día según el mes (antes de escalar): temporada alta de noviembre a marzo
DEMANDA_MES = {1: 40, 2: 36, 3: 24, 4: 13, 5: 7, 6: 6, 7: 15, 8: 8, 9: 11, 10: 16, 11: 24, 12: 34}
DEMANDA_DIA_SEMANA = [0.80, 0.75, 0.80, 0.90, 1.15, 1.55, 1.45]      # lunes ... domingo
VERANO = {11, 12, 1, 2, 3}

# id de catálogos (coinciden con los datos iniciales de db/schema.sql)
ROL_ADMIN, ROL_MOSTRADOR, ROL_TECNICO = 1, 2, 3
ORD_ABIERTA, ORD_EN_CURSO, ORD_CERRADA, ORD_CANCELADA = 1, 2, 3, 4
MANT_PREVENTIVO, MANT_CORRECTIVO = 1, 2
EST_DISPONIBLE = 1

UBICACIONES = [  # id, nombre, tipo, dirección, capacidad
    (1, "Estación Costanera", "ESTACION", "Av. Costanera 1200", 40),
    (2, "Estación Parque Municipal", "ESTACION", "Acceso norte del Parque Municipal", 30),
    (3, "Estación Terminal", "ESTACION", "Terminal de ómnibus, andén 1", 25),
    (4, "Taller Central", "TALLER", "Calle del Herrero 340", None),
]
ESTACIONES = [1, 2, 3]
TALLER = 4
PESO_ESTACION = {1: 0.50, 2: 0.30, 3: 0.20}

TIPOS = {  # id: (código, nombre, precio_hora, precio_dia al inicio, falla base por hora de uso)
    1: ("URBANA",    "Urbana",           3000, 12000, 0.0027),
    2: ("MTB",       "Mountain bike",    4500, 18000, 0.0051),
    3: ("ELECTRICA", "Eléctrica",        8000, 32000, 0.0042),
    4: ("RUTA",      "Ruta",             5000, 20000, 0.0036),
    5: ("INFANTIL",  "Infantil",         2000,  8000, 0.0030),
    6: ("TANDEM",    "Tándem",           6500, 26000, 0.0036),
}
FLOTA_INICIAL = {  # estación: {tipo: cantidad}
    1: {1: 8, 2: 6, 3: 5, 4: 2, 5: 5, 6: 2},
    2: {1: 6, 2: 6, 3: 3, 4: 1, 5: 3, 6: 1},
    3: {1: 4, 2: 3, 3: 3, 4: 1, 5: 1, 6: 0},
}
MARCAS = ["Pehuén", "Austral", "Nahuel", "Calafate", "Lenga", "Ñire"]
MODELOS = {1: ["Paseo", "Ciudad", "Mirador"], 2: ["Sendero", "Cumbre", "Alerce"], 3: ["Eco E1", "Eco E2"],
           4: ["Veloz", "Ruta 40"], 5: ["Pequeño", "Aventura"], 6: ["Dúo"]}
TALLES = {1: ["S", "M", "L"], 2: ["M", "L", "XL"], 3: ["M", "L"], 4: ["M", "L"], 5: ["U"], 6: ["U"]}

# plan de mantenimiento: (tarea, sistema, cada_horas, cada_dias, horas de trabajo, repuestos)
# repuestos: (descripción, cantidad, costo base en pesos del inicio, probabilidad)
TAREAS = {
    "cadena":     ("Lubricación y ajuste de cadena", "TRANSMISION", 120, 90, 0.8,
                   [("Lubricante y limpieza de transmisión", 1, 1800, 1.0), ("Cadena nueva", 1, 14000, 0.20)]),
    "frenos":     ("Revisión de frenos", "FRENOS", 240, 180, 1.2,
                   [("Pastillas de freno", 2, 4500, 0.45), ("Cable y funda de freno", 1, 2500, 0.30)]),
    "neumaticos": ("Control de neumáticos y rayos", "NEUMATICOS", 400, 240, 1.0,
                   [("Cámara", 1, 3200, 0.35), ("Cubierta", 1, 15000, 0.25)]),
    "general":    ("Service general (dirección y rodamientos)", "CUADRO", 700, 365, 2.5,
                   [("Grasa y rodamientos de dirección", 1, 9000, 1.0)]),
    "suspension": ("Service de suspensión", "SUSPENSION", 500, 365, 2.0,
                   [("Kit de service de suspensión", 1, 24000, 1.0)]),
    "electrico":  ("Revisión de batería y motor", "ELECTRICO", 350, 240, 1.8,
                   [("Diagnóstico de batería y motor", 1, 13000, 1.0)]),
}
PLAN_POR_TIPO = {
    1: ["cadena", "frenos", "neumaticos", "general"],
    2: ["cadena", "frenos", "neumaticos", "general", "suspension"],
    3: ["cadena", "frenos", "neumaticos", "general", "electrico"],
    4: ["cadena", "frenos", "neumaticos", "general"],
    5: ["cadena", "frenos", "neumaticos"],
    6: ["cadena", "frenos", "neumaticos", "general"],
}
AJUSTE_PLAN = {(6, "frenos"): (150, 120), (4, "neumaticos"): (260, 180)}   # tándem y ruta, más exigentes

# reparaciones: sistema -> (descripciones del problema, repuestos (desc, cant, costo base, prob))
FALLAS = {
    "FRENOS":      (["Frenos sin mordiente", "Ruido y pérdida de frenada", "Palanca de freno floja"],
                    [("Pastillas de freno", 2, 4500, 0.7), ("Disco de freno", 1, 9000, 0.25), ("Cable y funda de freno", 1, 2500, 0.4)]),
    "TRANSMISION": (["Cadena cortada", "Cambios que saltan", "Desviador torcido"],
                    [("Cadena nueva", 1, 14000, 0.6), ("Desviador", 1, 16000, 0.25), ("Cassette", 1, 21000, 0.2)]),
    "NEUMATICOS":  (["Pinchadura", "Cubierta rajada", "Válvula dañada"],
                    [("Cámara", 1, 3200, 0.85), ("Cubierta", 1, 15000, 0.35)]),
    "RUEDAS":      (["Rueda desalineada", "Rayos rotos", "Llanta abollada"],
                    [("Rayos y centrado de rueda", 1, 7000, 0.8), ("Llanta", 1, 22000, 0.15)]),
    "CUADRO":      (["Cuadro con fisura visible", "Dirección floja", "Pedalier con juego"],
                    [("Rodamientos de dirección", 1, 9000, 0.5), ("Pedalier", 1, 18000, 0.35)]),
    "SUSPENSION":  (["Horquilla sin retorno", "Pérdida de aceite en la suspensión"],
                    [("Kit de sellos de suspensión", 1, 24000, 0.8)]),
    "ELECTRICO":   (["La asistencia eléctrica se corta", "Batería que no carga", "Display sin señal"],
                    [("Controlador", 1, 45000, 0.25), ("Cargador", 1, 18000, 0.25), ("Cableado y conectores", 1, 8000, 0.5)]),
    "OTRO":        (["Manubrio torcido", "Pedal roto", "Asiento flojo", "Guardabarros roto"],
                    [("Repuesto menor", 1, 4000, 1.0)]),
}
SISTEMAS_FIJOS = ["RUEDAS", "OTRO"]            # fallas que no dependen de una tarea del plan
TARIFA_MO_HORA = 6000                          # mano de obra del taller, por hora, al inicio

NOMBRES = ["Agustín", "Alejandro", "Ana", "Andrea", "Belén", "Bruno", "Camila", "Carlos", "Carolina", "Cecilia",
           "Daniel", "Diego", "Eduardo", "Elena", "Emilia", "Facundo", "Federico", "Florencia", "Gabriel", "Gabriela",
           "Gonzalo", "Guillermo", "Ignacio", "Inés", "Javier", "Julia", "Juan", "Laura", "Lautaro", "Lucas",
           "Lucía", "Luciana", "Manuel", "Marcos", "María", "Mariana", "Martín", "Matías", "Mercedes", "Micaela",
           "Nicolás", "Noelia", "Pablo", "Paula", "Rafael", "Ramiro", "Romina", "Santiago", "Sofía", "Tomás",
           "Valentina", "Verónica", "Victoria", "Yamila"]
APELLIDOS = ["Acosta", "Aguirre", "Álvarez", "Benítez", "Blanco", "Cabrera", "Castro", "Córdoba", "Díaz", "Domínguez",
             "Fernández", "Ferreyra", "Figueroa", "Flores", "Gallardo", "García", "Giménez", "Gómez", "González", "Gutiérrez",
             "Herrera", "Ibáñez", "Juárez", "Ledesma", "López", "Luna", "Maldonado", "Martínez", "Medina", "Méndez",
             "Molina", "Morales", "Moreno", "Navarro", "Ortiz", "Pereyra", "Pérez", "Quiroga", "Ramírez", "Ríos",
             "Rivero", "Rodríguez", "Rojas", "Romero", "Ruiz", "Sánchez", "Silva", "Sosa", "Suárez", "Torres",
             "Vargas", "Vega", "Villalba", "Zárate"]
EXTRANJEROS = [("BR", ["João", "Pedro", "Ana", "Carla", "Lucas"], ["Silva", "Santos", "Oliveira", "Souza"]),
               ("CL", ["Felipe", "Catalina", "Sebastián", "Javiera"], ["Muñoz", "Rojas", "Soto", "Contreras"]),
               ("US", ["Emily", "Michael", "Sarah", "David"], ["Smith", "Johnson", "Miller", "Davis"]),
               ("DE", ["Lukas", "Anna", "Jonas", "Mia"], ["Müller", "Schmidt", "Weber", "Fischer"]),
               ("FR", ["Louis", "Chloé", "Hugo", "Léa"], ["Martin", "Bernard", "Dubois", "Moreau"]),
               ("ES", ["Pablo", "Lucía", "Álvaro", "Carmen"], ["García", "Ruiz", "Navarro", "Serrano"])]
PERSONAL = [  # nombre, apellido, rol
    ("Lucía", "Ferrer", ROL_ADMIN),
    ("Martina", "Quiroga", ROL_MOSTRADOR), ("Joaquín", "Bustos", ROL_MOSTRADOR), ("Paola", "Ledesma", ROL_MOSTRADOR),
    ("Esteban", "Cardozo", ROL_MOSTRADOR), ("Brenda", "Salinas", ROL_MOSTRADOR),
    ("Ramón", "Aguilera", ROL_TECNICO), ("Fabián", "Montenegro", ROL_TECNICO),
]

# ---------------------------------------------------------------- utilidades de formato


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, Decimal)):
        return str(v)
    if isinstance(v, float):
        return repr(round(v, 6))
    if isinstance(v, datetime):
        return "'" + v.astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S") + "-03'"
    if isinstance(v, date):
        return "'" + v.isoformat() + "'"
    return "'" + str(v).replace("'", "''") + "'"


def insertar(tabla, fila):
    cols = ", ".join(fila)
    vals = ", ".join(q(v) for v in fila.values())
    ov = " OVERRIDING SYSTEM VALUE" if "id" in fila else ""
    return f"INSERT INTO {tabla} ({cols}){ov} VALUES ({vals});"


def actualizar(tabla, cambios, donde):
    sets = ", ".join(f"{k} = {q(v)}" for k, v in cambios.items())
    return f"UPDATE {tabla} SET {sets} WHERE id = {donde};"


def dec(x, nd=2):
    return Decimal(x).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


def redondear_50(x):
    return Decimal(int((Decimal(x) / 50).to_integral_value(rounding=ROUND_HALF_UP)) * 50)


def importe_py(modalidad, ph, pd, seg):
    """Misma regla que fn_importe() de la base."""
    horas = max(1, -((-(seg - 600)) // 3600))
    dias = max(1, -((-(seg - 3600)) // 86400))
    if modalidad == "DIA":
        return Decimal(dias) * pd
    return min(Decimal(horas) * ph, Decimal(dias) * pd)


def horas_de(seg):
    return (Decimal(seg) / Decimal(3600)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def draw_atraso(rnd):
    """Fracción del intervalo que se demora el taller en hacer una tarea vencida."""
    u = rnd.random()
    if u < 0.55:
        return rnd.uniform(0, 0.08)
    if u < 0.80:
        return rnd.uniform(0.08, 0.30)
    if u < 0.95:
        return rnd.uniform(0.30, 0.80)
    return rnd.uniform(0.80, 1.50)


def poisson(rnd, lam):
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(rnd.gauss(lam, math.sqrt(lam)))))
    limite, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= limite:
            return k
        k += 1


def elegir(rnd, pares):
    """pares: lista de (valor, peso)."""
    total = sum(p for _, p in pares)
    u = rnd.random() * total
    acum = 0.0
    for v, p in pares:
        acum += p
        if u <= acum:
            return v
    return pares[-1][0]


# ---------------------------------------------------------------- modelo en memoria
class Bici:
    __slots__ = ("id", "codigo", "tipo", "base", "alta", "frag", "horas", "usos", "estado", "ubic",
                 "ordenes", "ultimo", "demora", "en_curso")

    def __init__(self, id, codigo, tipo, base, alta, frag):
        self.id, self.codigo, self.tipo, self.base, self.alta, self.frag = id, codigo, tipo, base, alta, frag
        self.horas = Decimal("0")
        self.usos = 0
        self.estado = "DISPONIBLE"
        self.ubic = base
        self.ordenes = 0                 # órdenes abiertas
        self.ultimo = {}                 # tarea -> (horas al ingresar, fecha de cierre)
        self.demora = {}                 # tarea -> fracción del intervalo que el taller deja pasar
        self.en_curso = set()            # tareas con orden preventiva abierta


class Plan:
    __slots__ = ("id", "clave", "tarea", "sistema", "cada_h", "cada_d", "trabajo", "repuestos")

    def __init__(self, id, clave, tarea, sistema, cada_h, cada_d, trabajo, repuestos):
        self.id, self.clave, self.tarea, self.sistema = id, clave, tarea, sistema
        self.cada_h, self.cada_d, self.trabajo, self.repuestos = cada_h, cada_d, trabajo, repuestos


class Obj:
    """Registro simple con atributos libres."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def en(t, h, m=0):
    return t.replace(hour=h, minute=m, second=0, microsecond=0)


def sig_laboral(t):
    """Primer momento hábil del taller (lunes a sábado, 8 a 18) desde t."""
    t = t.replace(microsecond=0)
    if t.hour < 8:
        t = en(t, 8, 0)
    elif t.hour >= 18:
        t = en(t + timedelta(days=1), 8, 0)
    if t.weekday() == 6:
        t = en(t + timedelta(days=1), 8, 0)
    return t


class Sim:
    def __init__(self, a):
        self.a = a
        self.rnd = random.Random(a.semilla)
        self.inicio = datetime.fromisoformat(a.desde).replace(tzinfo=TZ)
        self.hasta = datetime.fromisoformat(a.hasta).replace(tzinfo=TZ)
        self.escala = ESCALA_DEMANDA * a.escala
        self.f = gzip.open(a.salida, "wt", encoding="utf-8", compresslevel=6)
        self.n_sql = 0
        self.heap, self.seq = [], 0
        self.ids = defaultdict(int)
        self.bicis = {}
        self.planes = {}                 # tipo -> [Plan]
        self.tarifas = defaultdict(list)  # tipo -> [(desde, ph, pd)]
        self.clientes = {}               # id -> Obj(local)
        self.locales = []
        self.docs = set()
        self.res_abiertas = {}
        self.det_abiertos = {}
        self.taller_abiertas = 0
        self.mostrador, self.tecnicos, self.admin = [], [], None
        self.verdad_inc = []             # incidentes con su causa real
        self.verdad_exp = []             # exposición: una fila por devolución
        self.verdad_bici = []
        self.stats = defaultdict(int)
        self.rueda_tec = 0

    # ---------------------------------------------------------- salida
    def w(self, sql):
        self.f.write(sql + "\n")
        self.n_sql += 1

    def ins(self, tabla, fila):
        self.w(insertar(tabla, fila))

    def nid(self, nombre):
        self.ids[nombre] += 1
        return self.ids[nombre]

    def prog(self, t, tipo, *datos):
        self.seq += 1
        heapq.heappush(self.heap, (t.replace(microsecond=0), self.seq, tipo, datos))

    def infl(self, t):
        meses = (t.date() - self.inicio.date()).days / 30.4375
        return (1 + INFLACION_MENSUAL) ** meses

    def tarifa_en(self, tipo, fecha):
        vig = None
        for d, ph, pd in self.tarifas[tipo]:
            if d <= fecha:
                vig = (ph, pd)
        return vig

    def staff_mostrador(self, t, est):
        return self.mostrador[(t.date().toordinal() + est) % len(self.mostrador)]

    def tecnico(self):
        self.rueda_tec += 1
        return self.tecnicos[self.rueda_tec % len(self.tecnicos)]

    # ---------------------------------------------------------- catálogos, personal, flota
    def iniciar(self):
        r = self.rnd
        self.w("-- Datos sintéticos de Bicis sustentables (generados; ver generador/generar_datos.py)")
        self.w("BEGIN;")
        for uid, nom, tipo, dire, cap in UBICACIONES:
            self.ins("ubicacion", dict(id=uid, nombre=nom, tipo=tipo, direccion=dire, capacidad=cap))
        for tid, (cod, nom, ph, pd, _b) in TIPOS.items():
            self.ins("tipo_bicicleta", dict(id=tid, codigo=cod, nombre=nom))
        # personal
        creado = self.inicio - timedelta(days=420)
        for i, (nom, ape, rol) in enumerate(PERSONAL, 1):
            email = (nom + "." + ape).lower().replace("í", "i").replace("á", "a").replace("ó", "o") \
                .replace("é", "e").replace("ú", "u").replace("ñ", "n") + "@bicis.test"
            self.ins("usuario", dict(id=i, nombre=nom, apellido=ape, email=email, creado_en=creado))
            self.w(f"INSERT INTO usuario_rol (usuario_id, rol_id) VALUES ({i}, {rol});")
            (self.mostrador if rol == ROL_MOSTRADOR else self.tecnicos if rol == ROL_TECNICO else []).append(i)
            if rol == ROL_ADMIN:
                self.admin = i
        self.ids["usuario"] = len(PERSONAL)
        # tarifas: la primera vigente desde el inicio; las demás se publican cada trimestre
        self.tarifa_pendiente = []
        fecha = self.inicio.date()
        k = 0
        while fecha <= self.hasta.date() + timedelta(days=1):
            self.tarifa_pendiente.append((fecha, k))
            k += 1
            mes = fecha.month + 3
            fecha = date(fecha.year + (mes - 1) // 12, (mes - 1) % 12 + 1, 1)
        self.precios_base = {tid: (ph, pd) for tid, (_c, _n, ph, pd, _b) in TIPOS.items()}
        for fecha, k in list(self.tarifa_pendiente):
            if k == 0:
                self.publicar_tarifa(self.inicio - timedelta(minutes=1), fecha, k)
            else:
                self.prog(en(datetime(fecha.year, fecha.month, fecha.day, tzinfo=TZ), 0, 5), "tarifa", fecha, k)
        # plan de mantenimiento
        for tid in TIPOS:
            self.planes[tid] = []
            for clave in PLAN_POR_TIPO[tid]:
                tarea, sis, ch, cd, trab, rep = TAREAS[clave]
                ch, cd = AJUSTE_PLAN.get((tid, clave), (ch, cd))
                pid = self.nid("plan")
                self.ins("plan_mantenimiento", dict(id=pid, tipo_bicicleta_id=tid, tarea=tarea, sistema=sis,
                                                    cada_horas=ch, cada_dias=cd))
                self.planes[tid].append(Plan(pid, clave, tarea, sis, ch, cd, trab, rep))
        self.crear_flota_inicial()

    def publicar_tarifa(self, t, fecha, k):
        factor = (1 + INFLACION_MENSUAL) ** (3 * k)
        for tid, (ph, pd) in self.precios_base.items():
            nph = int(round(ph * factor / 100.0)) * 100
            npd = int(round(pd * factor / 500.0)) * 500
            self.tarifas[tid].append((fecha, Decimal(nph), Decimal(npd)))
            self.ins("tarifa", dict(tipo_bicicleta_id=tid, vigente_desde=fecha, precio_hora=Decimal(nph),
                                    precio_dia=Decimal(npd)))
        if k > 0:
            self.w(insertar("auditoria_sistema", dict(
                usuario_id=self.admin, accion="TARIFA_ACTUALIZADA", entidad="tarifa", entidad_id=None,
                detalle=__import__("json").dumps({"vigente_desde": fecha.isoformat(), "ajuste_pct": round((factor / ((1 + INFLACION_MENSUAL) ** (3 * (k - 1))) - 1) * 100, 1)}),
                creado_en=t)))

    def ev_tarifa(self, t, fecha, k):
        self.publicar_tarifa(t, fecha, k)

    def nueva_bici(self, tid, base, alta, t_alta, historico):
        r = self.rnd
        bid = self.nid("bici")
        cod, *_ = TIPOS[tid]
        self.ids["cod_" + cod] += 1
        codigo = f"{cod[:3]}-{self.ids['cod_' + cod]:03d}"
        frag = min(1.8, max(0.6, r.lognormvariate(0, 0.25)))
        b = Bici(bid, codigo, tid, base, alta, frag)
        if historico:
            dias = (self.inicio.date() - alta).days
            b.horas = dec(dias * r.uniform(0.5, 2.0))
            b.usos = int(float(b.horas) / 2.5)
        self.bicis[bid] = b
        self.verdad_bici.append((bid, codigo, round(frag, 4), alta.isoformat()))
        self.ins("bicicleta", dict(
            id=bid, codigo=codigo, tipo_bicicleta_id=tid, estado_id=EST_DISPONIBLE, ubicacion_base_id=base,
            ubicacion_id=base, marca=r.choice(MARCAS), modelo=r.choice(MODELOS[tid]), talle=r.choice(TALLES[tid]),
            fecha_alta=alta, horas_uso=b.horas, usos=b.usos))
        self.w(insertar("historial_estado_bicicleta", dict(
            bicicleta_id=bid, estado_ant_id=None, estado_nuevo_id=EST_DISPONIBLE, cambiado_en=t_alta,
            origen="USUARIO", usuario_id=self.admin, motivo="Alta de la bicicleta")))
        return b

    def crear_flota_inicial(self):
        r = self.rnd
        for est, tipos in FLOTA_INICIAL.items():
            for tid, cant in tipos.items():
                for _ in range(cant):
                    tope = 700 if tid == 3 else 1500
                    dias = r.randint(60, tope)
                    alta = self.inicio.date() - timedelta(days=dias)
                    self.nueva_bici(tid, est, alta, en(datetime(alta.year, alta.month, alta.day, tzinfo=TZ), 9, 0), True)
        # servicios anteriores al inicio de los datos: cada tarea tiene su último servicio
        for b in sorted(self.bicis.values(), key=lambda x: x.id):
            antiguedad = (self.inicio.date() - b.alta).days
            historicas = []
            sin_historia = []
            for p in self.planes[b.tipo]:
                f_dias = r.uniform(0.0, 0.95)
                f_horas = r.uniform(0.0, 0.95)
                ult_dia = self.inicio.date() - timedelta(days=max(3, int(f_dias * p.cada_d)))
                if (ult_dia - b.alta).days >= 3 and antiguedad >= 20:
                    historicas.append([p, ult_dia, float(b.horas) - f_horas * p.cada_h])
                else:
                    sin_historia.append(p)
            if sin_historia:
                tope_h = 0.9 * min(p.cada_h for p in sin_historia)
                if float(b.horas) > tope_h:
                    b.horas = dec(tope_h * r.uniform(0.4, 1.0))
                    self.w(f"UPDATE bicicleta SET horas_uso = {b.horas}, usos = {int(float(b.horas) / 2.5)} WHERE id = {b.id};")
                    b.usos = int(float(b.horas) / 2.5)
            for p in sin_historia:
                b.ultimo[p.clave] = (Decimal(0), b.alta)
                b.demora[p.clave] = draw_atraso(r)
            historicas.sort(key=lambda x: x[1])
            previo = None
            for p, dia, h_ult in historicas:
                if previo and dia <= previo:
                    dia = previo + timedelta(days=2)
                if dia >= self.inicio.date() - timedelta(days=1):
                    dia = self.inicio.date() - timedelta(days=1)
                previo = dia
                h_ult = max(0.0, h_ult)
                t = en(datetime(dia.year, dia.month, dia.day, tzinfo=TZ), 8, 0) + timedelta(minutes=r.randint(0, 90))
                self.orden_historica(b, p, t, Decimal(str(round(h_ult, 2))))
                b.ultimo[p.clave] = (Decimal(str(round(h_ult, 2))), dia)
                b.demora[p.clave] = draw_atraso(r)
            # alinear: la última entrada de horas no debe superar las horas acumuladas
            for k, (h, d) in list(b.ultimo.items()):
                if h > b.horas:
                    b.ultimo[k] = (b.horas, d)

    def orden_historica(self, b, p, t, horas):
        """Orden preventiva cerrada, anterior al inicio de los datos."""
        r = self.rnd
        oid = self.nid("orden")
        tec = self.tecnico()
        ini = t + timedelta(minutes=r.randint(20, 60))
        fin = ini + timedelta(minutes=int(p.trabajo * 60 * r.uniform(0.8, 1.4)))
        self.ins("orden_mantenimiento", dict(
            id=oid, bicicleta_id=b.id, tipo_id=MANT_PREVENTIVO, estado_id=ORD_ABIERTA, plan_id=p.id, tecnico_id=tec,
            taller_id=TALLER, descripcion=p.tarea, abierta_en=t, horas_uso=horas))
        self.w(actualizar("orden_mantenimiento", dict(estado_id=ORD_EN_CURSO, iniciada_en=ini), oid))
        self.items_preventiva(oid, p, t)
        self.w(actualizar("orden_mantenimiento", dict(estado_id=ORD_CERRADA, cerrada_en=fin), oid))

    # ---------------------------------------------------------- ítems de las órdenes
    def precio_rep(self, base, t):
        return dec(redondear_50(Decimal(str(base * self.infl(t) * self.rnd.uniform(0.9, 1.15)))), 2)

    def item(self, oid, desc, cant, costo):
        self.ins("orden_item", dict(orden_id=oid, descripcion=desc, cantidad=cant, costo_unitario=costo))

    def mano_obra(self, oid, horas, t):
        precio = dec(redondear_50(Decimal(str(TARIFA_MO_HORA * self.infl(t)))), 2)
        self.item(oid, "Mano de obra del taller", dec(horas), precio)

    def items_preventiva(self, oid, p, t):
        r = self.rnd
        self.mano_obra(oid, p.trabajo * r.uniform(0.9, 1.3), t)
        for desc, cant, base, prob in p.repuestos:
            if r.random() < prob:
                self.item(oid, desc, Decimal(cant), self.precio_rep(base, t))

    def items_correctiva(self, oid, sistema, sev, t):
        r = self.rnd
        horas = {"LEVE": r.uniform(0.8, 2.0), "MODERADA": r.uniform(2.0, 5.0), "GRAVE": r.uniform(5.0, 16.0)}[sev]
        self.mano_obra(oid, horas, t)
        _desc, reps = FALLAS[sistema]
        puestos = 0
        for desc, cant, base, prob in reps:
            pr = min(1.0, prob * {"LEVE": 0.8, "MODERADA": 1.0, "GRAVE": 1.25}[sev])
            if r.random() < pr:
                self.item(oid, desc, Decimal(cant), self.precio_rep(base, t))
                puestos += 1
        if puestos == 0 and sev != "LEVE":
            desc, cant, base, _p = reps[0]
            self.item(oid, desc, Decimal(cant), self.precio_rep(base, t))

    # ---------------------------------------------------------- clientes
    def nuevo_cliente(self, t, turista=None):
        r = self.rnd
        cid = self.nid("cliente")
        if turista is None:
            turista = r.random() < 0.22
        if turista:
            if r.random() < 0.55:
                pais, nombres, apes = r.choice(EXTRANJEROS)
                nom, ape = r.choice(nombres), r.choice(apes)
                tipo = "PASAPORTE"
                while True:
                    num = r.choice("ABCDEFGHJKLMNPRSTUVXYZ") + "".join(r.choice("0123456789") for _ in range(8))
                    if (tipo, pais, num) not in self.docs:
                        break
            else:                                     # turista argentino de otra provincia
                pais, tipo = "AR", "DNI"
                nom, ape = r.choice(NOMBRES), r.choice(APELLIDOS)
                num = self.dni_nuevo()
        else:
            pais, tipo = "AR", "DNI"
            nom, ape = r.choice(NOMBRES), r.choice(APELLIDOS)
            num = self.dni_nuevo()
        self.docs.add((tipo, pais, num))
        quitar = str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN")
        email = None
        if r.random() < 0.85:
            email = f"{nom}.{ape}{r.randint(1, 99)}".translate(quitar).lower().replace(" ", "") + "@correo.test"
        tel = f"+54 9 11 5550-{r.randint(0, 9999):04d}" if r.random() < 0.8 else None
        self.ins("cliente", dict(id=cid, nombre=nom, apellido=ape, tipo_documento=tipo, pais_documento=pais,
                                 numero_documento=num, email=email, telefono=tel, creado_en=t))
        self.clientes[cid] = Obj(turista=turista)
        if not turista:
            self.locales.append(cid)
        self.stats["clientes"] += 1
        return cid

    def dni_nuevo(self):
        while True:
            n = str(self.rnd.randint(17_000_000, 48_000_000))
            if ("DNI", "AR", n) not in self.docs:
                return n

    def elegir_cliente(self, t):
        if self.locales and self.rnd.random() < 0.30:
            return self.rnd.choice(self.locales)
        return self.nuevo_cliente(t)

    # ---------------------------------------------------------- demanda
    def ev_planificar(self, t, d):
        """Genera los grupos que querrán alquilar el día d (ya se pueden reservar con hasta 7 días de anticipación)."""
        r = self.rnd
        clima = r.lognormvariate(0, 0.28)
        if r.random() < (0.07 if d.month in VERANO else 0.15):
            clima *= 0.35                                  # día de lluvia o viento fuerte
        lam = DEMANDA_MES[d.month] * DEMANDA_DIA_SEMANA[d.weekday()] * self.escala * clima
        for _ in range(poisson(r, lam)):
            g = self.nuevo_grupo(d)
            if g.reserva:
                lead = g.lead
                creada = g.inicio - lead
                if g.canal != "WEB":                       # el mostrador y el teléfono atienden de 9 a 20
                    if creada.hour < 9:
                        creada = en(creada - timedelta(days=1), 18, r.randint(0, 50))
                    elif creada.hour >= 20:
                        creada = en(creada, 19, r.randint(0, 50))
                creada = max(creada, self.inicio + timedelta(hours=1))
                if creada < g.inicio - timedelta(minutes=30):
                    self.prog(creada, "res_crear", g)
                    continue
            self.prog(g.inicio, "walkin", g)

    def nuevo_grupo(self, d):
        r = self.rnd
        n = elegir(r, [(1, 50), (2, 28), (3, 10), (4, 7), (5, 2), (6, 2), (8, 1)])
        bicis = defaultdict(int)
        for _ in range(n):
            bicis[elegir(r, [(1, 30), (2, 20), (3, 19), (4, 5), (5, 16), (6, 10)])] += 1
        est = elegir(r, [(k, v) for k, v in PESO_ESTACION.items()])
        if r.random() < 0.18:
            modalidad = "DIA"
            dur = elegir(r, [(1, 60), (2, 25), (3, 10), (7, 5)])
            hora = elegir(r, [(h, p) for h, p in zip(range(9, 16), [12, 18, 18, 14, 14, 12, 8])])
            inicio = en(datetime(d.year, d.month, d.day, tzinfo=TZ), hora, r.randint(0, 59))
            fin = inicio + timedelta(days=dur)
        else:
            modalidad = "HORA"
            dur = elegir(r, [(1, 20), (2, 30), (3, 20), (4, 15), (5, 8), (6, 7)])
            hora = elegir(r, [(9, 6), (10, 12), (11, 16), (12, 12), (13, 10), (14, 14), (15, 14), (16, 9), (17, 5)])
            inicio = en(datetime(d.year, d.month, d.day, tzinfo=TZ), hora, r.randint(0, 59))
            tope = en(inicio, 19, 30)
            fin = min(inicio + timedelta(hours=dur), tope)
            if fin - inicio < timedelta(hours=1):
                fin = inicio + timedelta(hours=1)
        g = Obj(bicis=dict(bicis), est=est, modalidad=modalidad, inicio=inicio, fin=fin,
                reserva=r.random() < 0.45, canal=None, lead=None)
        if g.reserva:
            g.canal = elegir(r, [("WEB", 55), ("TELEFONO", 20), ("MOSTRADOR", 25)])
            if g.canal == "WEB":
                horas = elegir(r, [((2, 24), 40), ((24, 72), 35), ((72, 168), 25)])
            elif g.canal == "TELEFONO":
                horas = (2, 72)
            else:
                horas = (1, 36)
            g.lead = timedelta(minutes=int(r.uniform(*horas) * 60))
        return g

    # ---------------------------------------------------------- reservas
    def cupo(self, est, tp, ini, fin, excluir=None):
        """Réplica de fn_cupo() de la base."""
        flota = sum(1 for b in self.bicis.values()
                    if b.base == est and b.tipo == tp and b.estado not in ("BAJA", "FUERA_DE_SERVICIO"))
        reservado = sum(rv.qty.get(tp, 0) for rv in self.res_abiertas.values()
                        if rv.id != excluir and rv.est == est and rv.ini < fin and rv.fin > ini)
        afuera = sum(1 for d in self.det_abiertos.values()
                     if d.bici.base == est and d.bici.tipo == tp and d.alq.fin_prev > ini)
        return flota - reservado - afuera

    def precio_estimado(self, g, tp, cant, t):
        ph, pd = self.tarifa_en(tp, t.date())
        seg = int((g.fin - g.inicio).total_seconds())
        return cant * importe_py(g.modalidad, ph, pd, seg)

    def ev_res_crear(self, t, g):
        r = self.rnd
        pedido = {}
        for tp, n in sorted(g.bicis.items()):
            c = self.cupo(g.est, tp, g.inicio, g.fin)
            if c > 0:
                pedido[tp] = min(n, c)
        if not pedido:
            self.stats["demanda_perdida_reserva"] += 1
            return
        cid = self.elegir_cliente(t)
        rid = self.nid("reserva")
        staff = None if g.canal == "WEB" else self.staff_mostrador(t, g.est)
        self.ins("reserva", dict(id=rid, cliente_id=cid, ubicacion_id=g.est, inicio_previsto=g.inicio,
                                 fin_previsto=g.fin, canal=g.canal, creada_en=t, creada_por=staff))
        for tp, n in pedido.items():
            self.w(insertar("reserva_detalle", dict(reserva_id=rid, tipo_bicicleta_id=tp, cantidad=n)))
        rv = Obj(id=rid, cliente=cid, est=g.est, ini=g.inicio, fin=g.fin, qty=dict(pedido), canal=g.canal,
                 modalidad=g.modalidad, estado="PENDIENTE", sena=None, sena_monto=Decimal(0), creada=t, staff=staff)
        self.res_abiertas[rid] = rv
        self.stats["reservas"] += 1
        total = sum(self.precio_estimado(g, tp, n, t) for tp, n in pedido.items())
        rv.sena_monto = max(Decimal(500), redondear_50(total * SENIA_PORCENTAJE))
        # ¿paga la seña?
        if g.canal == "WEB":
            if r.random() < 0.94:
                self.prog(t + timedelta(minutes=r.randint(2, 12)), "res_confirmar", rid)
            else:
                self.prog(t + timedelta(minutes=30), "res_vencer", rid, "Seña no acreditada en 30 minutos")
                return
        elif g.canal == "TELEFONO":
            if r.random() < 0.85:
                self.prog(t + timedelta(minutes=r.randint(10, 150)), "res_confirmar", rid)
            else:
                self.prog(t + timedelta(hours=3), "res_vencer", rid, "Seña no acreditada en 3 horas")
                return
        else:
            self.prog(t + timedelta(minutes=r.randint(1, 4)), "res_confirmar", rid)
        # destino de la reserva confirmada
        u = r.random()
        confirm_aprox = t + timedelta(hours=3)
        if u < 0.11:
            margen = (g.inicio - confirm_aprox).total_seconds() / 3600.0
            if margen > 1.0:
                cuando = g.inicio - timedelta(hours=r.uniform(0.5, min(margen, 60.0)))
                cuando = max(cuando, confirm_aprox)
                self.prog(cuando, "res_cancelar", rid)
                return
        elif u < 0.18:
            self.prog(g.inicio + timedelta(minutes=61), "res_ausente", rid)
            return
        self.prog(g.inicio + timedelta(minutes=r.randint(-8, 30)), "res_retiro", rid)

    def pago(self, t, **kw):
        pid = self.nid("pago")
        fila = dict(id=pid, creado_en=t)
        fila.update(kw)
        self.ins("pago", fila)
        return pid

    def medio(self, canal):
        r = self.rnd
        if canal == "WEB":
            return r.choice(["TARJETA", "BILLETERA_VIRTUAL", "TARJETA"])
        if canal == "TELEFONO":
            return r.choice(["TRANSFERENCIA", "BILLETERA_VIRTUAL"])
        return elegir(r, [("EFECTIVO", 40), ("TARJETA", 30), ("BILLETERA_VIRTUAL", 22), ("TRANSFERENCIA", 8)])

    def referencia(self, medio):
        if medio == "EFECTIVO":
            return None
        return {"TARJETA": "TJ-", "BILLETERA_VIRTUAL": "BV-", "TRANSFERENCIA": "TR-"}[medio] + \
            "".join(self.rnd.choice("0123456789ABCDEF") for _ in range(10))

    def ev_res_confirmar(self, t, rid):
        rv = self.res_abiertas.get(rid)
        if rv is None or rv.estado != "PENDIENTE":
            return
        medio = self.medio(rv.canal)
        rv.sena = self.pago(t, reserva_id=rid, tipo="SENIA", monto=rv.sena_monto, medio=medio,
                            referencia=self.referencia(medio), registrado_por=rv.staff)
        rv.sena_medio = medio
        self.w(actualizar("reserva", dict(estado="CONFIRMADA"), rid))
        rv.estado = "CONFIRMADA"

    def cerrar_reserva(self, t, rv, estado, motivo):
        self.w(actualizar("reserva", dict(estado=estado, cerrada_en=t, motivo_cierre=motivo), rv.id))
        rv.estado = estado
        del self.res_abiertas[rv.id]

    def ev_res_vencer(self, t, rid, motivo):
        rv = self.res_abiertas.get(rid)
        if rv is None or rv.estado != "PENDIENTE":
            return
        self.cerrar_reserva(t, rv, "VENCIDA", motivo)
        self.stats["reservas_vencidas"] += 1

    def ev_res_ausente(self, t, rid):
        rv = self.res_abiertas.get(rid)
        if rv is None or rv.estado != "CONFIRMADA":
            return
        self.cerrar_reserva(t, rv, "VENCIDA", "El cliente no se presentó (seña retenida)")
        self.stats["reservas_ausentes"] += 1

    def reembolsar(self, t, rv, fraccion, staff):
        monto = redondear_50(rv.sena_monto * Decimal(str(fraccion)))
        monto = min(monto, rv.sena_monto)
        if monto <= 0:
            return
        self.pago(t, reserva_id=rv.id, tipo="REEMBOLSO", monto=monto, medio=rv.sena_medio,
                  referencia=self.referencia(rv.sena_medio), pago_origen_id=rv.sena, registrado_por=staff)

    def ev_res_cancelar(self, t, rid):
        rv = self.res_abiertas.get(rid)
        if rv is None or rv.estado != "CONFIRMADA" or rv.ini - t < timedelta(minutes=30):
            if rv is not None and rv.estado == "CONFIRMADA":
                self.prog(rv.ini + timedelta(minutes=self.rnd.randint(-5, 20)), "res_retiro", rid)
            return
        anticipada = rv.ini - t >= timedelta(hours=24)
        self.cerrar_reserva(t, rv, "CANCELADA", "Cancelada por el cliente")
        self.reembolsar(t, rv, 1.0 if anticipada else 0.5, rv.staff)
        self.stats["reservas_canceladas"] += 1

    def ev_res_retiro(self, t, rid):
        rv = self.res_abiertas.get(rid)
        if rv is None or rv.estado != "CONFIRMADA":
            return
        elegidas = []
        for tp, n in sorted(rv.qty.items()):
            libres = [b for b in self.bicis.values() if b.estado == "DISPONIBLE" and b.ubic == rv.est and b.tipo == tp]
            for _ in range(min(n, len(libres))):
                b = min(self.rnd.sample(libres, min(2, len(libres))), key=lambda x: x.horas)
                libres.remove(b)
                elegidas.append(b)
        if not elegidas:
            self.cerrar_reserva(t, rv, "CANCELADA", "Cancelada por el local: sin bicicletas disponibles")
            self.reembolsar(t, rv, 1.0, self.staff_mostrador(t, rv.est))
            self.stats["reservas_canceladas_local"] += 1
            return
        dur = rv.fin - rv.ini
        self.abrir_alquiler(t, rv.cliente, rv.est, elegidas, rv.modalidad, dur, rv)

    def ev_walkin(self, t, g):
        res_pronto = defaultdict(int)
        for rv in self.res_abiertas.values():
            if rv.est == g.est and rv.ini < t + timedelta(minutes=120) and rv.fin > t:
                for tp, n in rv.qty.items():
                    res_pronto[tp] += n
        elegidas = []
        for tp, n in sorted(g.bicis.items()):
            libres = [b for b in self.bicis.values() if b.estado == "DISPONIBLE" and b.ubic == g.est and b.tipo == tp]
            permitido = max(0, len(libres) - res_pronto[tp])
            for _ in range(min(n, permitido)):
                b = min(self.rnd.sample(libres, min(2, len(libres))), key=lambda x: x.horas)
                libres.remove(b)
                elegidas.append(b)
        if not elegidas:
            self.stats["demanda_perdida_mostrador"] += 1
            return
        cid = self.elegir_cliente(t)
        self.abrir_alquiler(t, cid, g.est, elegidas, g.modalidad, g.fin - g.inicio, None)

    # ---------------------------------------------------------- alquileres
    def abrir_alquiler(self, t, cid, est, bicis, modalidad, dur, rv):
        r = self.rnd
        aid = self.nid("alquiler")
        op = self.staff_mostrador(t, est)
        dur = max(dur, timedelta(hours=1))
        fin_prev = t + dur
        self.ins("alquiler", dict(id=aid, cliente_id=cid, reserva_id=rv.id if rv else None, ubicacion_retiro_id=est,
                                  operador_id=op, salida_real=t, fin_previsto=fin_prev))
        alq = Obj(id=aid, cliente=cid, est=est, salida=t, fin_prev=fin_prev, dets=[], abiertos=0, reserva=rv,
                  anulado=False, cargos=Decimal(0), op=op)
        if rv is not None:
            del self.res_abiertas[rv.id]
            rv.estado = "CONVERTIDA"
        for b in bicis:
            did = self.nid("det")
            ph, pd = self.tarifa_en(b.tipo, t.date())
            self.ins("alquiler_detalle", dict(id=did, alquiler_id=aid, bicicleta_id=b.id, tipo_bicicleta_id=b.tipo,
                                              modalidad=modalidad, precio_hora=ph, precio_dia=pd, salida_real=t))
            det = Obj(id=did, alq=alq, bici=b, modalidad=modalidad, ph=ph, pd=pd, salida=t, importe=None)
            alq.dets.append(det)
            alq.abiertos += 1
            self.det_abiertos[did] = det
            b.estado, b.ubic = "ALQUILADA", None
        self.stats["alquileres"] += 1
        self.stats["bicis_alquiladas"] += len(bicis)
        if rv is None and r.random() < 0.006:
            alq.anulado = True
            self.prog(t + timedelta(minutes=r.randint(3, 15)), "anular", alq)
            return alq
        base = self.hora_devolucion(t, fin_prev)
        extra_idx = r.randrange(len(alq.dets)) if len(alq.dets) > 1 and r.random() < 0.08 else None
        for i, det in enumerate(alq.dets):
            ret = base + (timedelta(minutes=r.randint(5, 90)) if i == extra_idx else timedelta(0))
            destino = est if r.random() < 0.92 else r.choice([e for e in ESTACIONES if e != est])
            self.prog(self.dentro_de_horario(ret), "devolucion", det, destino)
        return alq

    def hora_devolucion(self, t_salida, fin_prev):
        r = self.rnd
        u = r.random()
        if u < 0.72:
            ret = fin_prev + timedelta(minutes=r.uniform(-20, 8))
        elif u < 0.89:
            ret = fin_prev + timedelta(minutes=r.uniform(8, 45))
        elif u < 0.96:
            ret = fin_prev + timedelta(minutes=r.uniform(45, 180))
        else:
            ret = fin_prev + timedelta(days=1, minutes=r.uniform(-30, 60))
        return max(ret, t_salida + timedelta(minutes=25))

    def dentro_de_horario(self, ret):
        if ret.hour >= 20:
            ret = en(ret + timedelta(days=1), 9, 0) + timedelta(minutes=self.rnd.randint(0, 40))
        elif ret.hour < 9:
            ret = en(ret, 9, 0) + timedelta(minutes=self.rnd.randint(0, 40))
        return ret

    def ev_anular(self, t, alq):
        self.w(actualizar("alquiler", dict(anulada_en=t, motivo_anulacion="Cargado por error en el mostrador"), alq.id))
        for det in alq.dets:
            del self.det_abiertos[det.id]
            det.bici.estado, det.bici.ubic = "DISPONIBLE", alq.est
        self.w(insertar("auditoria_sistema", dict(
            usuario_id=alq.op, accion="ALQUILER_ANULADO", entidad="alquiler", entidad_id=alq.id,
            detalle=__import__("json").dumps({"motivo": "Cargado por error en el mostrador"}), creado_en=t)))
        self.stats["alquileres_anulados"] += 1

    # ---------------------------------------------------------- riesgo (la verdad que el modelo debe descubrir)
    def medida(self, b, p, fecha):
        h, d = b.ultimo[p.clave]
        return max(float(b.horas - h) / p.cada_h, (fecha - d).days / p.cada_d)

    def riesgo(self, b, t):
        fecha = t.date()
        edad = (fecha - b.alta).days / 365.25
        atrasos = {p.clave: max(0.0, self.medida(b, p, fecha) - 1.0) for p in self.planes[b.tipo]}
        atraso = max(atrasos.values()) if atrasos else 0.0
        base = TIPOS[b.tipo][4]
        tasa = base * math.exp(0.12 * edad) * b.frag * math.exp(1.4 * min(atraso, 1.2)) * \
            (1.12 if t.month in VERANO else 1.0)
        return tasa, atraso, atrasos, edad

    def sistema_falla(self, b, atrasos):
        pesos = defaultdict(float)
        for p in self.planes[b.tipo]:
            pesos[p.sistema] += 1.0 + 8.0 * atrasos[p.clave]
        pesos["RUEDAS"] += 0.8
        pesos["OTRO"] += 0.8
        return elegir(self.rnd, list(pesos.items()))

    def sistema_usuario(self, b):
        pesos = [("RUEDAS", 25), ("CUADRO", 12), ("OTRO", 30), ("FRENOS", 8), ("TRANSMISION", 10), ("NEUMATICOS", 12)]
        if b.tipo == 2:
            pesos.append(("SUSPENSION", 6))
        if b.tipo == 3:
            pesos.append(("ELECTRICO", 5))
        return elegir(self.rnd, pesos)

    # ---------------------------------------------------------- devolución
    def ev_devolucion(self, t, det, destino):
        r = self.rnd
        alq, b = det.alq, det.bici
        if alq.anulado:
            return
        seg = int((t - det.salida).total_seconds())
        importe = importe_py(det.modalidad, det.ph, det.pd, seg)
        horas = seg / 3600.0
        if det.modalidad == "DIA":
            efectivas = min(horas, 6.0 * math.ceil(horas / 24.0))
        else:
            efectivas = min(horas, 8.0)
        tasa, atraso, atrasos, edad = self.riesgo(b, t)
        p_f = 1 - math.exp(-tasa * efectivas)
        tasa_u = 0.0016 * {5: 1.6, 2: 1.3}.get(b.tipo, 1.0)
        p_u = 1 - math.exp(-tasa_u * efectivas)
        falla = r.random() < p_f
        usuario = (not falla) and r.random() < p_u
        self.verdad_exp.append((det.id, b.id, t.date().isoformat(), round(efectivas, 2), round(tasa, 6),
                                round(atraso, 4), round(edad, 3), round(p_f, 6), int(falla)))
        tipo = sev = sistema = desc = None
        if falla:
            tipo = "FALLA"
            sev = elegir(r, [("LEVE", 55), ("MODERADA", 33), ("GRAVE", 12)])
            sistema = self.sistema_falla(b, atrasos)
            desc = r.choice(FALLAS[sistema][0])
        elif usuario:
            tipo = elegir(r, [("DANIO", 55), ("ACCIDENTE", 45)])
            sev = elegir(r, [("LEVE", 55), ("MODERADA", 33), ("GRAVE", 12)] if tipo == "DANIO"
                         else [("LEVE", 35), ("MODERADA", 42), ("GRAVE", 23)])
            sistema = self.sistema_usuario(b)
            desc = ("Daño del cliente: " if tipo == "DANIO" else "Accidente: ") + r.choice(FALLAS[sistema][0]).lower()
        dano = tipo is not None
        cambios = dict(devuelta_en=t, ubicacion_devolucion_id=destino,
                       estado_devolucion="CON_DANIO" if dano else "OK",
                       observaciones_devolucion=desc[:300] if dano else (
                           "Sin novedades" if r.random() < 0.15 else None))
        self.w(actualizar("alquiler_detalle", cambios, det.id))
        horas_antes = b.horas
        b.horas += horas_de(seg)
        b.usos += 1
        b.estado, b.ubic = ("FUERA_DE_SERVICIO" if dano else "DISPONIBLE"), destino
        det.importe, det.devuelta = importe, t
        del self.det_abiertos[det.id]
        alq.abiertos -= 1
        staff = self.staff_mostrador(t, destino)
        if dano:
            iid = self.nid("incidencia")
            ocurrida = t if tipo != "FALLA" else det.salida + (t - det.salida) * r.uniform(0.2, 0.95)
            self.ins("incidencia", dict(id=iid, bicicleta_id=b.id, detalle_id=det.id, reportada_por=staff, tipo=tipo,
                                        severidad=sev, sistema=sistema, descripcion=desc[:300],
                                        ocurrida_en=ocurrida.replace(microsecond=0), horas_uso=horas_antes))
            self.verdad_inc.append((iid, b.id, det.id, tipo, sistema, sev, round(tasa, 6), round(atraso, 4),
                                    round(atrasos.get(next((p.clave for p in self.planes[b.tipo] if p.sistema == sistema), ""), 0.0), 4)))
            self.stats["incidencias_" + tipo.lower()] += 1
            if tipo in ("DANIO", "ACCIDENTE") and r.random() < (0.8 if tipo == "DANIO" else 0.55):
                base = {"LEVE": r.uniform(3000, 9000), "MODERADA": r.uniform(10000, 35000),
                        "GRAVE": r.uniform(40000, 120000)}[sev]
                monto = dec(redondear_50(Decimal(str(base * self.infl(t)))) // 100 * 100, 2)
                monto = max(monto, Decimal(1000))
                self.ins("cargo_extra", dict(alquiler_id=alq.id, detalle_id=det.id, concepto="DANIO", monto=monto,
                                             descripcion=desc[:200], creado_en=t, registrado_por=staff))
                alq.cargos += monto
            self.prog(sig_laboral(t + timedelta(minutes=r.randint(15, 150))), "orden_corr", b, iid, sev, sistema, desc)
        if r.random() < (0.045 if b.tipo == 2 else 0.012):
            monto = dec(Decimal(int(2500 * self.infl(t) / 100) * 100), 2)
            self.ins("cargo_extra", dict(alquiler_id=alq.id, detalle_id=det.id, concepto="LIMPIEZA", monto=monto,
                                         descripcion="Limpieza de barro", creado_en=t, registrado_por=staff))
            alq.cargos += monto
        if alq.abiertos == 0:
            self.cobrar(t + timedelta(minutes=r.randint(1, 6)), alq, staff)

    def cobrar(self, t, alq, staff):
        r = self.rnd
        total = sum((d.importe for d in alq.dets if d.importe is not None), Decimal(0))
        rv = alq.reserva
        sena = rv.sena_monto if (rv is not None and rv.sena is not None) else Decimal(0)
        debe = Decimal(0)
        if alq.cargos > 0 and r.random() < 0.15:
            debe = alq.cargos
            self.stats["alquileres_con_deuda"] += 1
        a_cobrar = total + alq.cargos - debe - sena
        if a_cobrar > 0:
            medio = elegir(r, [("EFECTIVO", 38), ("TARJETA", 32), ("BILLETERA_VIRTUAL", 22), ("TRANSFERENCIA", 8)])
            if medio == "TARJETA" and r.random() < 0.04:
                self.pago(t, alquiler_id=alq.id, tipo="COBRO", monto=a_cobrar, medio="TARJETA", estado="RECHAZADO",
                          referencia=self.referencia("TARJETA"), registrado_por=staff)
                medio = "EFECTIVO"
                t += timedelta(minutes=2)
            self.pago(t, alquiler_id=alq.id, tipo="COBRO", monto=a_cobrar, medio=medio,
                      referencia=self.referencia(medio), registrado_por=staff)
        elif a_cobrar < 0 and rv is not None and rv.sena is not None:
            self.pago(t, reserva_id=rv.id, tipo="REEMBOLSO", monto=min(-a_cobrar, rv.sena_monto),
                      medio=rv.sena_medio, referencia=self.referencia(rv.sena_medio), pago_origen_id=rv.sena,
                      registrado_por=staff)
        self.stats["alquileres_finalizados"] += 1

    # ---------------------------------------------------------- taller
    def abrir_orden(self, t, b, tipo, plan=None, inc=None, sev=None, sistema=None, desc=None):
        r = self.rnd
        oid = self.nid("orden")
        tec = self.tecnico()
        self.ins("orden_mantenimiento", dict(
            id=oid, bicicleta_id=b.id, tipo_id=tipo, estado_id=ORD_ABIERTA, plan_id=plan.id if plan else None,
            incidencia_id=inc, tecnico_id=tec, taller_id=TALLER,
            descripcion=(plan.tarea if plan else desc)[:300], abierta_en=t))
        horas_open = b.horas
        b.estado, b.ubic = "EN_MANTENIMIENTO", TALLER
        b.ordenes += 1
        self.taller_abiertas += 1
        o = Obj(id=oid, bici=b, plan=plan, inc=inc, sev=sev, sistema=sistema, tec=tec, horas_open=horas_open)
        if plan:
            b.en_curso.add(plan.clave)
            espera = timedelta(minutes=r.randint(25, 80))
            ti = max(t + espera, en(t, 8, 10))
            dur = timedelta(hours=plan.trabajo * r.uniform(0.8, 1.4))
            tc = ti + dur
            if tc.hour >= 18:
                tc = sig_laboral(tc)
        else:
            espera = timedelta(hours=r.expovariate(1 / (2.5 + 3.0 * max(0, self.taller_abiertas - 4))))
            ti = sig_laboral(t + espera)
            dur_h = {"LEVE": r.uniform(1.5, 5), "MODERADA": r.uniform(6, 30), "GRAVE": r.uniform(30, 130)}[sev]
            tc = sig_laboral(ti + timedelta(hours=dur_h))
        self.prog(ti, "orden_inicio", o)
        self.prog(max(tc, ti + timedelta(minutes=30)), "orden_cierre", o)
        self.stats["ordenes_" + ("preventivas" if plan else "correctivas")] += 1

    def ev_orden_corr(self, t, b, inc, sev, sistema, desc):
        if b.estado != "FUERA_DE_SERVICIO":
            return
        self.abrir_orden(t, b, MANT_CORRECTIVO, inc=inc, sev=sev, sistema=sistema, desc="Reparación: " + desc)

    def ev_orden_inicio(self, t, o):
        self.w(actualizar("orden_mantenimiento", dict(estado_id=ORD_EN_CURSO, iniciada_en=t), o.id))

    def ev_orden_cierre(self, t, o):
        r = self.rnd
        b = o.bici
        baja = False
        if o.plan:
            self.items_preventiva(o.id, o.plan, t)
        else:
            self.items_correctiva(o.id, o.sistema, o.sev, t)
            edad = (t.date() - b.alta).days / 365.25
            baja = o.sev == "GRAVE" and r.random() < (0.15 if edad > 3.2 else 0.05)
        if baja:
            self.w(f"SELECT fn_bici_cambiar_estado({b.id}, 'BAJA', {TALLER}, {q(t)}, "
                   f"'Irreparable: no conviene reparar', {o.tec});")
            b.estado, b.ubic = "BAJA", TALLER
            self.w(insertar("auditoria_sistema", dict(
                usuario_id=o.tec, accion="BICICLETA_BAJA", entidad="bicicleta", entidad_id=b.id,
                detalle=__import__("json").dumps({"motivo": "Irreparable", "orden": o.id}), creado_en=t)))
            self.stats["bajas"] += 1
            self.prog(t + timedelta(days=r.randint(20, 45)), "compra", b.tipo, b.base)
        self.w(actualizar("orden_mantenimiento", dict(estado_id=ORD_CERRADA, cerrada_en=t), o.id))
        b.ordenes -= 1
        self.taller_abiertas -= 1
        if b.estado == "EN_MANTENIMIENTO" and b.ordenes == 0:
            b.estado, b.ubic = "DISPONIBLE", b.base
        if o.inc:
            self.w(actualizar("incidencia", dict(resuelta_en=t), o.inc))
        if o.plan:
            b.ultimo[o.plan.clave] = (o.horas_open, t.date())
            b.demora[o.plan.clave] = draw_atraso(r)
            b.en_curso.discard(o.plan.clave)

    def ev_taller_dia(self, t):
        if t.weekday() == 6:
            return
        cand = []
        for b in self.bicis.values():
            if b.estado != "DISPONIBLE" or b.ordenes:
                continue
            mejor = None
            for p in self.planes[b.tipo]:
                m = self.medida(b, p, t.date())
                if m >= 1.0 + b.demora[p.clave] and (mejor is None or m > mejor[0]):
                    mejor = (m, p)
            if mejor:
                cand.append((mejor[0], b.id, b, mejor[1]))
        cand.sort(key=lambda x: (-x[0], x[1]))
        for i, (_m, _id, b, p) in enumerate(cand[:6]):
            self.abrir_orden(t + timedelta(minutes=7 * i), b, MANT_PREVENTIVO, plan=p)

    def ev_reubicar(self, t):
        for b in sorted(self.bicis.values(), key=lambda x: x.id):
            if b.estado == "DISPONIBLE" and b.ubic != b.base:
                self.w(f"SELECT fn_bici_cambiar_estado({b.id}, 'DISPONIBLE', {b.base}, {q(t)}, "
                       f"'Reubicación a su estación base', {self.tecnico()});")
                b.ubic = b.base
                self.stats["reubicaciones"] += 1

    def ev_compra(self, t, tid, base):
        b = self.nueva_bici(tid, base, t.date(), t, False)
        self.w(insertar("auditoria_sistema", dict(
            usuario_id=self.admin, accion="BICICLETA_ALTA", entidad="bicicleta", entidad_id=b.id,
            detalle=__import__("json").dumps({"codigo": b.codigo}), creado_en=t)))
        for p in self.planes[tid]:
            b.ultimo[p.clave] = (Decimal(0), t.date())
            b.demora[p.clave] = draw_atraso(self.rnd)
        self.stats["compras"] += 1

    # ---------------------------------------------------------- ejecución
    def correr(self):
        self.iniciar()
        d = self.inicio.date()
        ultimo = self.hasta.date() + timedelta(days=8)
        while d <= ultimo:
            medianoche = datetime(d.year, d.month, d.day, tzinfo=TZ)
            self.prog(max(self.inicio, medianoche - timedelta(days=8)), "planificar", d)
            if d <= self.hasta.date():
                self.prog(en(medianoche, 7, 0), "taller_dia")
                self.prog(en(medianoche, 20, 30), "reubicar")
            d += timedelta(days=1)
        for (fecha, tid, base) in [(date(2025, 11, 3), 3, 1), (date(2025, 11, 3), 3, 2), (date(2025, 11, 3), 2, 2),
                                   (date(2025, 11, 3), 1, 3), (date(2026, 10, 12), 3, 1), (date(2026, 10, 12), 1, 1),
                                   (date(2026, 10, 12), 5, 3)]:
            if self.inicio.date() < fecha <= self.hasta.date():
                self.prog(en(datetime(fecha.year, fecha.month, fecha.day, tzinfo=TZ), 8, 30), "compra", tid, base)
        pasos = 0
        while self.heap:
            t, _s, tipo, datos = heapq.heappop(self.heap)
            if t > self.hasta:
                break
            getattr(self, "ev_" + tipo)(t, *datos)
            pasos += 1
        self.cerrar()

    def cerrar(self):
        for tabla, n in [("usuario", len(PERSONAL)), ("ubicacion", len(UBICACIONES)), ("tipo_bicicleta", len(TIPOS)),
                         ("plan_mantenimiento", self.ids["plan"]), ("bicicleta", self.ids["bici"]),
                         ("cliente", self.ids["cliente"]), ("reserva", self.ids["reserva"]),
                         ("alquiler", self.ids["alquiler"]), ("alquiler_detalle", self.ids["det"]),
                         ("pago", self.ids["pago"]), ("incidencia", self.ids["incidencia"]),
                         ("orden_mantenimiento", self.ids["orden"])]:
            if n:
                self.w(f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), {n}, true);")
        self.w("COMMIT;")
        self.w("ANALYZE;")
        self.f.close()

    def escribir_verdad(self, carpeta):
        import csv
        import os
        os.makedirs(carpeta, exist_ok=True)
        with open(os.path.join(carpeta, "verdad_bicicletas.csv"), "w", newline="", encoding="utf-8") as f:
            c = csv.writer(f)
            c.writerow(["bicicleta_id", "codigo", "fragilidad", "fecha_alta"])
            c.writerows(self.verdad_bici)
        with open(os.path.join(carpeta, "verdad_incidentes.csv"), "w", newline="", encoding="utf-8") as f:
            c = csv.writer(f)
            c.writerow(["incidencia_id", "bicicleta_id", "detalle_id", "tipo", "sistema", "severidad",
                        "tasa_por_hora", "atraso_max", "atraso_del_sistema"])
            c.writerows(self.verdad_inc)
        with gzip.open(os.path.join(carpeta, "verdad_exposicion.csv.gz"), "wt", newline="", encoding="utf-8") as f:
            c = csv.writer(f)
            c.writerow(["detalle_id", "bicicleta_id", "fecha", "horas_efectivas", "tasa_por_hora", "atraso_max",
                        "edad_anios", "prob_falla", "hubo_falla"])
            c.writerows(self.verdad_exp)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", default="2024-10-01T00:00")
    ap.add_argument("--hasta", default=datetime.now(TZ).strftime("%Y-%m-%dT%H:%M"))
    ap.add_argument("--salida", default="data/seed.sql.gz")
    ap.add_argument("--verdad", default="data", help="carpeta para los archivos con la verdad simulada")
    ap.add_argument("--semilla", type=int, default=20260)
    ap.add_argument("--escala", type=float, default=1.0, help="multiplica el volumen de demanda")
    a = ap.parse_args()
    s = Sim(a)
    s.correr()
    s.escribir_verdad(a.verdad)
    print(f"{s.n_sql} sentencias en {a.salida}", file=sys.stderr)
    for k in sorted(s.stats):
        print(f"  {k:32s} {s.stats[k]}", file=sys.stderr)


if __name__ == "__main__":
    main()
