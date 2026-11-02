from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "docs/practica-3/Maqueta_Documentacion_Practica_3.docx"
GREEN, DARK, PALE, GRAY, LINE, WHITE = "1F6B4F", "24332D", "EAF4EF", "F3F5F4", "D9E0DD", "FFFFFF"


def set_font(run, size=12, bold=None, italic=None, color=None):
    run.font.name = "Times New Roman"
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), "Times New Roman")
    rpr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill):
    pr = cell._tc.get_or_add_tcPr()
    node = pr.find(qn("w:shd")) or OxmlElement("w:shd")
    if node.getparent() is None:
        pr.append(node)
    node.set(qn("w:fill"), fill)


def cell_padding(cell, value=120):
    pr = cell._tc.get_or_add_tcPr()
    box = pr.first_child_found_in("w:tcMar") or OxmlElement("w:tcMar")
    if box.getparent() is None:
        pr.append(box)
    for side in ("top", "start", "bottom", "end"):
        node = box.find(qn(f"w:{side}")) or OxmlElement(f"w:{side}")
        if node.getparent() is None:
            box.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def table_borders(tbl, color=LINE, size="6"):
    pr = tbl._tbl.tblPr
    box = pr.first_child_found_in("w:tblBorders") or OxmlElement("w:tblBorders")
    if box.getparent() is None:
        pr.append(box)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = box.find(qn(f"w:{edge}")) or OxmlElement(f"w:{edge}")
        if node.getparent() is None:
            box.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), size)
        node.set(qn("w:color"), color)


def add_body(doc, text, italic=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 2
    p.paragraph_format.space_after = Pt(0)
    set_font(p.add_run(text), italic=italic)


def add_list(doc, items, numbered=False):
    for item in items:
        p = doc.add_paragraph(style="List Number" if numbered else "List Bullet")
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.first_line_indent = Cm(-0.4)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(2)
        set_font(p.add_run(item))


def add_table(doc, headers, rows, widths=None):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    table_borders(tbl)
    trpr = tbl.rows[0]._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    trpr.append(repeat)
    for i, value in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        shade(cell, GREEN)
        cell_padding(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if widths:
            cell.width = Cm(widths[i])
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        set_font(p.add_run(value), 9.5, bold=True, color=WHITE)
    for ri, values in enumerate(rows):
        cells = tbl.add_row().cells
        for i, value in enumerate(values):
            cell = cells[i]
            cell_padding(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            if ri % 2:
                shade(cell, GRAY)
            if widths:
                cell.width = Cm(widths[i])
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1
            p.paragraph_format.space_after = Pt(0)
            set_font(p.add_run(str(value)), 9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_placeholder(doc, number, title, instruction):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(tbl, "9ABCAA", "10")
    cell = tbl.cell(0, 0)
    shade(cell, PALE)
    cell_padding(cell, 180)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(f"ESPACIO PARA FIGURA {number}"), 11, bold=True, color=GREEN)
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(instruction), 10, italic=True, color=DARK)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1
    p.paragraph_format.space_after = Pt(8)
    set_font(p.add_run(f"Figura {number}\n"), 10, bold=True)
    set_font(p.add_run(title), 10, italic=True)


def chapter(doc, title):
    doc.add_page_break()
    doc.add_heading(title, level=1)


def section(doc, title, paragraphs=(), bullets=(), numbered=False):
    doc.add_heading(title, level=2)
    for paragraph in paragraphs:
        add_body(doc, paragraph)
    if bullets:
        add_list(doc, bullets, numbered)


def add_page_field(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    text = OxmlElement("w:instrText")
    text.set(qn("xml:space"), "preserve")
    text.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, text, end])
    set_font(run, 10, color=DARK)


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(2.54)
sec.header_distance, sec.footer_distance = Cm(1.25), Cm(1.25)
sec.different_first_page_header_footer = True

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
normal.font.size = Pt(12)
normal.paragraph_format.line_spacing = 2
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.widow_control = True
for name, size, color in (("Title", 22, GREEN), ("Heading 1", 16, GREEN), ("Heading 2", 13, DARK), ("Heading 3", 12, DARK)):
    style = doc.styles[name]
    style.font.name = "Times New Roman"
    style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor.from_string(color)
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.space_before = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

hp = sec.header.paragraphs[0]
hp.text = "Turismo Sustentable  |  Práctica Profesional 3"
for run in hp.runs:
    set_font(run, 9, bold=True, color=GREEN)
add_page_field(sec.header.add_paragraph())
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(fp.add_run("Documento de trabajo — actualizar durante cada incremento"), 9, italic=True, color="66756F")

# Portada
for _ in range(4):
    doc.add_paragraph()
for text, size, bold, italic, color in (
    ("[NOMBRE DE LA INSTITUCIÓN]", 12, True, False, DARK),
    ("[CARRERA] · [ASIGNATURA]", 11, False, False, DARK),
    ("", 11, False, False, DARK),
    ("SISTEMA DE GESTIÓN DE\nTURISMO SUSTENTABLE", 24, True, False, GREEN),
    ("Análisis, rediseño e implementación del backend", 14, False, True, DARK),
    ("PRÁCTICA PROFESIONAL 3", 13, True, False, GREEN),
):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(text), size, bold, italic, color)
for _ in range(5):
    doc.add_paragraph()
for text in ("Autor: Karim Homsi", "Docente: [NOMBRE DEL DOCENTE]", "Ciudad: [CIUDAD]", "Año: 2026", "Versión: 0.1 — Maqueta inicial"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(text), 11)

chapter(doc, "Control del documento")
add_table(doc, ["Versión", "Fecha", "Responsable", "Descripción"], [
    ["0.1", "[dd/mm/aaaa]", "Karim Homsi", "Creación de la maqueta documental"],
    ["0.2", "[dd/mm/aaaa]", "[Responsable]", "[Cambios realizados]"],
], [2.2, 3.0, 4.0, 7.0])
section(doc, "Cómo utilizar esta maqueta", ["Este documento funciona como estructura inicial del informe de la Práctica Profesional 3. Los textos entre corchetes deben reemplazarse con información confirmada; los ejemplos no deben presentarse como resultados reales hasta haber sido validados."], [
    "Actualizar el documento después de cada incremento funcional.",
    "Relacionar objetivos, requerimientos, reglas, casos de uso, pruebas y evidencias mediante identificadores.",
    "Mantener figuras y tablas numeradas, tituladas y mencionadas en el texto.",
    "Ubicar capturas extensas y evidencias completas en anexos.",
    "Aplicar la plantilla institucional por encima de esta maqueta cuando corresponda.",
])
section(doc, "Estados documentales")
add_table(doc, ["Estado", "Significado"], [
    ["Borrador", "Contenido inicial sujeto a revisión"], ["Revisado", "Contenido verificado"],
    ["Aprobado", "Contenido validado"], ["Implementado", "Reflejado en el código"],
    ["Probado", "Validado mediante pruebas y evidencias"],
], [4.0, 12.2])

chapter(doc, "Mapa de contenidos")
add_body(doc, "Este mapa reemplaza provisoriamente el índice automático. Cuando el documento esté avanzado, se deberá insertar o actualizar la tabla de contenido desde Microsoft Word.")
add_list(doc, ["Resumen", "1. Introducción", "2. Problema, objetivos y alcance", "3. Metodología y ciclo de vida", "4. Relevamiento y requerimientos", "5. Análisis del sistema", "6. Diseño de datos", "7. Arquitectura y diseño del backend", "8. Implementación por incrementos", "9. Pruebas y evidencias", "10. Manuales de uso y operación", "11. Gestión del proyecto", "12. Resultados, conclusiones y trabajos futuros", "Referencias", "Anexos"], True)

chapter(doc, "Resumen")
add_body(doc, "El presente proyecto propone la refactorización y ampliación de una plataforma web orientada a la gestión del alquiler de bicicletas. La solución permitirá administrar usuarios, estaciones, bicicletas, tarifas, alquileres, devoluciones, mantenimiento y notificaciones. Se aplicará un ciclo de vida incremental e iterativo utilizando Java, Spring Boot y una base de datos relacional. [Completar con los resultados alcanzados al finalizar el proyecto].")
p = doc.add_paragraph()
p.paragraph_format.line_spacing = 2
set_font(p.add_run("Palabras clave: "), bold=True, italic=True)
set_font(p.add_run("turismo sustentable, alquiler de bicicletas, Spring Boot, ingeniería de software, base de datos."), italic=True)
section(doc, "Abstract", ["[Incorporar una traducción fiel del resumen y de las palabras clave si la institución lo solicita]."])

chapter(doc, "1. Introducción")
section(doc, "1.1 Contexto", ["El proyecto se ubica en el ámbito del turismo sustentable y la movilidad urbana. El uso compartido de bicicletas requiere conocer su disponibilidad, controlar su ubicación, administrar estaciones y registrar correctamente el ciclo completo de cada alquiler."])
section(doc, "1.2 Antecedentes", ["Durante la Práctica Profesional 2 se desarrolló una primera versión funcional con registro, autenticación, roles, estaciones, bicicletas, alquileres, devoluciones, correo y recuperación de contraseña.", "La nueva etapa parte de esa base aprobada, pero amplía el modelo de datos y revisa su arquitectura. Se conservarán las reglas ya validadas y se corregirán las limitaciones detectadas."])
section(doc, "1.3 Propósito del documento", ["Registrar el relevamiento, análisis, rediseño, implementación y validación de la Práctica Profesional 3, incluyendo requerimientos, reglas, modelos, decisiones, pruebas, evidencias y manuales."])
section(doc, "1.4 Organización", ["[Describir brevemente el contenido de cada capítulo cuando la estructura definitiva haya sido aprobada]."])

chapter(doc, "2. Problema, objetivos y alcance")
section(doc, "2.1 Planteamiento del problema", ["[Explicar qué necesitan los usuarios y la organización, qué inconsistencias pueden producirse y por qué la versión anterior es insuficiente, sin describir todavía la solución técnica]."])
section(doc, "2.2 Justificación", bullets=["Contribución al turismo sustentable.", "Centralización de la administración de la flota.", "Reducción de inconsistencias.", "Información para la toma de decisiones.", "Mejora de seguridad y mantenibilidad."])
section(doc, "2.3 Objetivo general", ["Desarrollar una plataforma web robusta para gestionar el alquiler de bicicletas, usuarios, estaciones, tarifas y operaciones asociadas a la movilidad sustentable."])
section(doc, "2.4 Objetivos específicos")
add_table(doc, ["Código", "Objetivo"], [["OE-01", "Rediseñar el modelo de datos."], ["OE-02", "Gestionar el ciclo completo de los alquileres."], ["OE-03", "Controlar disponibilidad y ubicación de bicicletas."], ["OE-04", "Incorporar seguridad y trazabilidad."], ["OE-05", "Validar reglas mediante pruebas."], ["OE-06", "Proporcionar herramientas administrativas."]], [2.5, 13.7])
section(doc, "2.5 Alcance incluido", bullets=["Usuarios, roles y autenticación.", "Bicicletas, estaciones y disponibilidad.", "Alquileres, devoluciones, tarifas e importes.", "Mantenimiento, notificaciones y administración.", "Reportes definidos por los requerimientos aprobados."])
section(doc, "2.6 Fuera de alcance", ["[Enumerar expresamente funcionalidades no comprometidas, como aplicación móvil, telemetría IoT, GPS en tiempo real o procesamiento bancario real, si efectivamente quedan excluidas]."])
section(doc, "2.7 Restricciones y supuestos", ["[Registrar restricciones de tiempo, recursos, tecnologías y servicios externos, y validar los supuestos de diseño con el docente]."])

chapter(doc, "3. Metodología y ciclo de vida")
section(doc, "3.1 Modelo incremental e iterativo", ["Cada incremento incluirá relevamiento, análisis, diseño, implementación, pruebas y actualización documental. Esto permite validar progresivamente las funcionalidades y corregir el diseño antes de incorporar nuevos módulos."])
add_placeholder(doc, 1, "Ciclo de vida incremental e iterativo", "Necesidad → requerimientos → análisis → diseño → implementación → pruebas → evaluación → documentación.")
section(doc, "3.2 Etapas", bullets=["Relevar la necesidad.", "Definir requerimientos y aceptación.", "Modelar procesos y datos.", "Diseñar y registrar decisiones.", "Implementar el incremento.", "Probar y conservar evidencias.", "Actualizar documentación y trazabilidad."], numbered=True)
section(doc, "3.3 Incrementos previstos")
add_table(doc, ["Incremento", "Contenido"], [["0", "Arquitectura y migraciones"], ["1", "Usuarios y seguridad"], ["2", "Estaciones"], ["3", "Bicicletas y mantenimiento"], ["4", "Tarifas y alquileres"], ["5", "Pagos o suscripciones"], ["6", "Notificaciones y reportes"], ["7", "Pruebas integrales y cierre"]], [2.8, 13.4])
section(doc, "3.4 Definición de terminado", ["Una funcionalidad se considerará terminada cuando el requerimiento esté aprobado, el código integrado, las reglas probadas, las evidencias registradas y la documentación actualizada."])

chapter(doc, "4. Relevamiento y requerimientos")
section(doc, "4.1 Actores")
add_table(doc, ["Código", "Actor", "Descripción"], [["ACT-01", "Visitante", "Persona sin sesión iniciada."], ["ACT-02", "Cliente", "Usuario registrado."], ["ACT-03", "Administrador", "Gestiona el sistema."], ["ACT-04", "Servicio de correo", "Envía notificaciones."]], [2.3, 4.0, 9.9])
section(doc, "4.2 Requerimiento funcional — plantilla")
add_table(doc, ["Campo", "Ejemplo"], [["Código", "RF-ALQ-01"], ["Nombre", "Iniciar alquiler"], ["Descripción", "El cliente inicia el alquiler de una bicicleta disponible."], ["Actor", "Cliente"], ["Prioridad", "Alta"], ["Precondiciones", "Usuario activo y bicicleta disponible."], ["Resultado", "Alquiler iniciado."], ["Aceptación", "No existe otro alquiler activo para la bicicleta."], ["Estado", "Propuesto / aprobado / implementado / probado"]], [4.2, 12.0])
section(doc, "4.3 Requerimientos no funcionales")
add_table(doc, ["Código", "Categoría", "Requerimiento"], [["RNF-SEG-01", "Seguridad", "Contraseñas almacenadas mediante hash seguro."], ["RNF-SEG-02", "Seguridad", "Un cliente no consulta datos privados ajenos."], ["RNF-REN-01", "Rendimiento", "Listados extensos paginados."], ["RNF-INT-01", "Integridad", "Una bicicleta no tiene dos alquileres activos."], ["RNF-USA-01", "Usabilidad", "Errores claros y accionables."]], [3.0, 3.5, 9.7])
section(doc, "4.4 Reglas de negocio")
add_table(doc, ["Código", "Regla"], [["RN-ALQ-01", "Una bicicleta solo puede tener un alquiler activo."], ["RN-ALQ-02", "El precio queda congelado al iniciar."], ["RN-EST-01", "Una estación no supera su capacidad."], ["RN-BIC-01", "Una bicicleta alquilada no cambia manualmente de estación."], ["RN-USU-01", "Un usuario inactivo no inicia sesión."]], [3.2, 13.0])
section(doc, "4.5 Matriz de trazabilidad")
add_table(doc, ["Objetivo", "Requisito", "Caso", "Regla", "Prueba", "Estado"], [["OE-02", "RF-ALQ-01", "CU-ALQ-01", "RN-ALQ-01", "CP-ALQ-01", "Pendiente"], ["OE-03", "RF-EST-04", "CU-EST-03", "RN-EST-01", "CP-EST-05", "Pendiente"]], [2.2, 2.8, 3.0, 2.8, 2.8, 2.6])

chapter(doc, "5. Análisis del sistema")
section(doc, "5.1 Diagrama de contexto", ["Mostrará el sistema como una unidad y su relación con actores y servicios externos."])
add_placeholder(doc, 2, "Diagrama de contexto", "Insertar actores y sistemas externos; no representar clases o tablas internas.")
section(doc, "5.2 Casos de uso")
add_placeholder(doc, 3, "Diagrama general de casos de uso", "Incluir registro, autenticación, recuperación, consulta, alquiler, devolución y administración.")
section(doc, "5.3 Especificación de caso de uso")
add_table(doc, ["Campo", "CU-ALQ-02 — Finalizar alquiler"], [["Actor", "Cliente"], ["Precondición", "Posee un alquiler iniciado."], ["Disparador", "Selecciona Finalizar alquiler."], ["Flujo principal", "Selecciona estación; se valida capacidad, calcula importe y registra devolución."], ["Alternativa", "La estación no tiene capacidad."], ["Postcondición", "La bicicleta queda disponible."], ["Trazabilidad", "RF-ALQ-04; RF-EST-03; RN-EST-01"]], [4.0, 12.2])
section(doc, "5.4 Actividades y secuencias", ["Se priorizarán procesos con decisiones o interacción entre componentes: registro, recuperación, inicio, devolución y mantenimiento."])
add_placeholder(doc, 4, "Actividad: finalizar alquiler", "Representar autorización, alquiler válido, estación activa y capacidad.")
add_placeholder(doc, 5, "Secuencia: finalizar alquiler", "Cliente → Controller → Service → Repositories → Correo.")
section(doc, "5.5 Estados", ["Documentar estados válidos y transiciones para bicicletas, alquileres, mantenimientos y usuarios."])

chapter(doc, "6. Diseño de datos")
section(doc, "6.1 Evolución desde la Práctica 2", ["[Describir entidades existentes, limitaciones, nuevas necesidades y decisiones de conservación o reemplazo]."])
section(doc, "6.2 DER conceptual y lógico")
add_placeholder(doc, 6, "DER conceptual", "Entidades y relaciones principales sin tipos de datos.")
add_placeholder(doc, 7, "DER lógico", "Claves, atributos relevantes y cardinalidades.")
section(doc, "6.3 Modelo físico", ["Incluir nombres reales, tipos, nulabilidad, restricciones, índices y valores predeterminados."])
section(doc, "6.4 Diccionario de datos")
add_table(doc, ["Columna", "Tipo", "Nulo", "Restricción", "Descripción"], [["id", "BIGINT", "No", "PK", "Identificador"], ["usuario_id", "BIGINT", "No", "FK", "Usuario del alquiler"], ["bicicleta_id", "BIGINT", "No", "FK", "Bicicleta utilizada"], ["fecha_inicio", "TIMESTAMP", "No", "—", "Instante de inicio"], ["fecha_fin", "TIMESTAMP", "Sí", "—", "Instante de finalización"], ["precio_aplicado", "DECIMAL", "No", ">= 0", "Tarifa congelada"]], [3.0, 2.6, 1.8, 3.0, 5.8])
section(doc, "6.5 Restricciones e índices", bullets=["Unicidad de emails y códigos.", "Índices sobre claves, estados y fechas.", "Restricciones de importes y capacidades.", "Protección frente a alquileres activos duplicados.", "Integridad referencial y estrategia de bajas."])
section(doc, "6.6 Migraciones")
add_table(doc, ["Migración", "Descripción", "Fecha", "Estado"], [["V1", "Esquema base P3", "[fecha]", "Pendiente"], ["V2", "Usuarios", "[fecha]", "Pendiente"], ["V3", "Estaciones y bicicletas", "[fecha]", "Pendiente"]], [2.5, 8.0, 3.0, 2.7])

chapter(doc, "7. Arquitectura y diseño del backend")
section(doc, "7.1 Tecnologías")
add_table(doc, ["Tecnología", "Versión", "Uso"], [["Java", "[versión]", "Lenguaje"], ["Spring Boot", "[versión]", "Backend"], ["Spring Security", "[versión]", "Seguridad"], ["Base de datos", "[motor]", "Persistencia"], ["Gradle", "[versión]", "Construcción"], ["Flyway", "[versión]", "Migraciones"]], [4.0, 4.0, 8.2])
section(doc, "7.2 Vista general")
add_placeholder(doc, 8, "Arquitectura general", "Frontend → API/DTO → servicios → repositorios → base; incluir integraciones.")
section(doc, "7.3 Módulos")
add_table(doc, ["Módulo", "Responsabilidad"], [["usuarios", "Perfiles y seguridad"], ["flota", "Bicicletas y disponibilidad"], ["estaciones", "Ubicaciones y capacidad"], ["alquileres", "Inicio, devolución e historial"], ["tarifas", "Precios y monedas"], ["mantenimiento", "Incidentes y órdenes"], ["notificaciones", "Correos y eventos"], ["reportes", "Indicadores administrativos"]], [4.0, 12.2])
section(doc, "7.4 Convenciones", bullets=["DTO en los límites HTTP.", "Reglas en servicios transaccionales.", "Errores uniformes.", "Importes decimales con moneda explícita.", "Secretos mediante variables de entorno.", "Esquema mediante migraciones."])
section(doc, "7.5 Seguridad", ["[Documentar autenticación, autorización, sesiones o tokens, hash, recuperación, CSRF, datos sensibles y secretos]."])
section(doc, "7.6 Concurrencia", ["[Explicar solicitudes simultáneas sobre una bicicleta o el último espacio de una estación y el comportamiento ante fallos]."])
section(doc, "7.7 Contrato de API")
add_table(doc, ["Elemento", "Ejemplo"], [["Ruta", "PATCH /api/alquileres/{id}/finalizar"], ["Solicitud", "{ \"estacionDestinoId\": 3 }"], ["Respuesta", "Alquiler finalizado con importe"], ["Error", "ESTACION_SIN_CAPACIDAD — HTTP 409"]], [4.2, 12.0])

chapter(doc, "8. Implementación por incrementos")
section(doc, "8.1 Incremento 0", bullets=["Conservar la P2 aprobada.", "Crear rama de refactorización.", "Preparar base local independiente.", "Incorporar perfiles, migraciones y pruebas.", "Definir módulos."])
section(doc, "8.2 Plantilla de incremento")
add_table(doc, ["Campo", "Contenido"], [["Nombre", "Incremento y módulo"], ["Objetivo", "Resultado esperado"], ["Requerimientos", "Identificadores atendidos"], ["Modelo", "Tablas afectadas"], ["API", "Endpoints"], ["Reglas", "Validaciones implementadas"], ["Pruebas", "Casos y resultados"], ["Decisiones", "Alternativas y elección"], ["Estado", "Planificado / implementado / probado"]], [4.0, 12.2])
section(doc, "8.3 Decisiones arquitectónicas")
add_table(doc, ["Campo", "ADR-001 — Migraciones"], [["Contexto", "El modelo necesita cambios reproducibles."], ["Decisión", "Versionar el esquema mediante Flyway."], ["Alternativas", "ddl-auto o scripts manuales."], ["Consecuencias", "Mayor control y mantenimiento explícito."], ["Estado", "Propuesta"]], [4.0, 12.2])
section(doc, "8.4 Registro de cambios", ["Cada modificación relevante indicará razón, requerimientos afectados, migraciones, pruebas y versión."])

chapter(doc, "9. Pruebas y evidencias")
section(doc, "9.1 Estrategia", bullets=["Pruebas unitarias.", "Integración de persistencia y transacciones.", "Seguridad y permisos.", "API.", "Aceptación de interfaz."])
section(doc, "9.2 Ambiente")
add_table(doc, ["Elemento", "Valor"], [["Java", "[versión]"], ["Perfil", "test"], ["Base", "[motor o contenedor]"], ["Datos", "[conjunto controlado]"], ["Fecha", "[dd/mm/aaaa]"]], [5.0, 11.2])
section(doc, "9.3 Caso de prueba — plantilla")
add_table(doc, ["Campo", "CP-ALQ-03 — Impedir alquiler simultáneo"], [["Requerimiento", "RF-ALQ-01"], ["Regla", "RN-ALQ-01"], ["Precondición", "Bicicleta disponible"], ["Entrada", "Dos solicitudes simultáneas"], ["Esperado", "Solo una solicitud aceptada"], ["Obtenido", "[Completar]"], ["Estado", "Pendiente"], ["Evidencia", "EV-ALQ-03"]], [4.2, 12.0])
section(doc, "9.4 Evidencias", ["Usar nombres como EV-USU-001_registro-exitoso.png y EV-EST-001_estacion-llena.png."])
add_placeholder(doc, 9, "Evidencia de prueba", "Insertar captura, respuesta HTTP, log o informe; indicar fecha, datos y resultado.")
section(doc, "9.5 Resumen")
add_table(doc, ["Módulo", "Ejecutadas", "Exitosas", "Fallidas", "Observaciones"], [["Usuarios", "—", "—", "—", "Pendiente"], ["Alquileres", "—", "—", "—", "Pendiente"], ["Estaciones", "—", "—", "—", "Pendiente"]], [3.7, 2.7, 2.5, 2.3, 5.0])

chapter(doc, "10. Manuales de uso y operación")
section(doc, "10.1 Visitante", bullets=["Consultar información pública.", "Registrarse e iniciar sesión.", "Recuperar contraseña."])
section(doc, "10.2 Cliente", bullets=["Consultar bicicletas.", "Iniciar y finalizar alquileres.", "Elegir estación de devolución.", "Consultar historial y comprobantes."])
section(doc, "10.3 Administrador", bullets=["Gestionar usuarios.", "Administrar estaciones y bicicletas.", "Supervisar alquileres y mantenimiento.", "Consultar reportes."])
section(doc, "10.4 Procedimiento — plantilla")
add_table(doc, ["Campo", "Descripción"], [["Objetivo", "Operación a realizar"], ["Requisitos", "Rol o datos necesarios"], ["Pasos", "Secuencia numerada"], ["Resultado", "Comportamiento esperado"], ["Errores", "Mensaje y solución"], ["Evidencia", "Captura"]], [4.5, 11.7])
section(doc, "10.5 Manual técnico", bullets=["Instalación y herramientas.", "Variables y perfiles.", "Base y migraciones.", "Ejecución y pruebas.", "Datos demo, respaldo y restauración."])

chapter(doc, "11. Gestión del proyecto")
section(doc, "11.1 Plan de trabajo", ["[Incorporar cronograma definitivo con módulos, dependencias, fechas y entregables]."])
section(doc, "11.2 Backlog")
add_table(doc, ["Código", "Tarea", "Prioridad", "Estado", "Requisito"], [["T-001", "Preparar migraciones", "Alta", "Pendiente", "RNF-MAN-01"], ["T-002", "Rediseñar usuarios", "Alta", "Pendiente", "RF-USU-01"], ["T-003", "Crear pruebas de alquiler", "Alta", "Pendiente", "RF-ALQ-01"]], [2.2, 6.2, 2.7, 2.8, 3.0])
section(doc, "11.3 Riesgos")
add_table(doc, ["Riesgo", "Prob.", "Impacto", "Mitigación"], [["Cambios tardíos del DER", "Alta", "Alto", "Validar antes de implementar"], ["Crecimiento del alcance", "Alta", "Alto", "Separar obligatorio y opcional"], ["Falta de pruebas", "Media", "Alto", "Probar cada incremento"], ["Servicios externos", "Media", "Medio", "Manejar fallos y configuración local"]], [6.0, 2.0, 2.3, 5.9])
section(doc, "11.4 Versiones")
add_table(doc, ["Versión", "Fecha", "Descripción"], [["P2", "[fecha]", "Versión aprobada"], ["P3.0.1", "[fecha]", "Preparación arquitectónica"], ["P3.1.0", "[fecha]", "Primer incremento"]], [3.0, 3.5, 9.7])

chapter(doc, "12. Resultados, conclusiones y trabajos futuros")
section(doc, "12.1 Resultados", ["[Comparar estado inicial y final. Informar requerimientos cumplidos, pruebas, seguridad, mantenibilidad, rendimiento y limitaciones]."])
section(doc, "12.2 Evaluación de objetivos")
add_table(doc, ["Objetivo", "Resultado", "Evidencia", "Cumplimiento"], [["OE-01", "[Completar]", "[Referencia]", "Pendiente"], ["OE-02", "[Completar]", "[Referencia]", "Pendiente"], ["OE-03", "[Completar]", "[Referencia]", "Pendiente"]], [3.0, 6.3, 3.7, 3.2])
section(doc, "12.3 Conclusiones", ["[Indicar si se alcanzó el objetivo general, qué objetivos se cumplieron, conocimientos aplicados, dificultades y soluciones]."])
section(doc, "12.4 Trabajos futuros", ["[Incluir solamente mejoras justificadamente fuera del alcance; no ocultar aquí requerimientos obligatorios incompletos]."])

chapter(doc, "Referencias")
add_body(doc, "[Incorporar únicamente las fuentes realmente utilizadas y ordenarlas alfabéticamente según APA y las exigencias institucionales].")
add_list(doc, ["Ingeniería de software y ciclo de vida.", "UML y modelado de datos.", "Documentación oficial de Java, Spring y herramientas.", "Estándares de seguridad.", "Servicios externos."])
section(doc, "Ejemplo", ["Autor u organización. (Año). Título de la página o documento. Sitio o publicación. URL"])

chapter(doc, "Anexos")
add_table(doc, ["Anexo", "Contenido"], [["A", "Catálogo de requerimientos"], ["B", "Casos de uso"], ["C", "Diagramas y DER"], ["D", "Diccionario de datos"], ["E", "Contrato de API"], ["F", "Casos de prueba"], ["G", "Evidencias"], ["H", "Manuales"], ["I", "Decisiones arquitectónicas"]], [2.5, 13.7])
section(doc, "Trazabilidad completa — ejemplo")
add_table(doc, ["Nivel", "Elemento"], [["Objetivo", "OE-02 — Gestionar alquileres"], ["Requisito", "RF-ALQ-04 — Devolver bicicleta"], ["Regla", "RN-EST-01 — Capacidad disponible"], ["Caso", "CU-ALQ-02 — Finalizar alquiler"], ["Datos", "alquiler → bicicleta → estación"], ["API", "PATCH /api/alquileres/{id}/finalizar"], ["Pruebas", "CP-ALQ-06 y CP-ALQ-07"], ["Evidencias", "EV-ALQ-04 y EV-ALQ-05"]], [4.0, 12.2])
section(doc, "Lista de verificación", bullets=["Requerimientos con aceptación y estado.", "DER consistente con migraciones y entidades.", "Figuras y tablas numeradas.", "Pruebas con resultados y evidencias.", "Manuales de la versión entregada.", "Referencias citadas.", "Ejemplos y notas internas eliminados al finalizar."])

props = doc.core_properties
props.title = "Maqueta de documentación — Práctica Profesional 3"
props.subject = "Ingeniería de software aplicada a Turismo Sustentable"
props.author = "Karim Homsi"
props.keywords = "Turismo Sustentable, Práctica Profesional 3, ingeniería de software"
settings = doc.settings._element
update = OxmlElement("w:updateFields")
update.set(qn("w:val"), "true")
settings.append(update)
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print(OUT.resolve())
