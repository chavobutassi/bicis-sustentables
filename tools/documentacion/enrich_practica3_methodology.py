from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph


PROJECT_ROOT = Path(__file__).resolve().parents[2]
path = PROJECT_ROOT / "docs/practica-3/Maqueta_Documentacion_Practica_3.docx"
doc = Document(path)


def set_font(run, size=12, bold=None, color=None):
    run.font.name = "Times New Roman"
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), "Times New Roman")
    rpr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def insert_after(anchor, text, style=None, bullet=False):
    node = OxmlElement("w:p")
    anchor._p.addnext(node)
    paragraph = Paragraph(node, anchor._parent)
    if style:
        paragraph.style = doc.styles[style]
    paragraph.paragraph_format.line_spacing = 1.5 if bullet else 2
    paragraph.paragraph_format.space_after = Pt(2 if bullet else 0)
    if bullet:
        paragraph.paragraph_format.left_indent = Cm(0.8)
        paragraph.paragraph_format.first_line_indent = Cm(-0.4)
        text = "• " + text
    set_font(paragraph.add_run(text), 12)
    return paragraph


definition = next(p for p in doc.paragraphs if p.text.startswith("Una funcionalidad se considerará terminada"))
anchor = insert_after(definition, "3.5 Gestión de cambios", "Heading 2")
anchor = insert_after(anchor, "Todo cambio de alcance o diseño deberá quedar registrado antes de implementarse. El registro permitirá conocer su causa, impacto y relación con la versión entregada.")
for item in (
    "Descripción y motivo del cambio.",
    "Requerimientos, tablas y endpoints afectados.",
    "Impacto sobre pruebas, documentación y cronograma.",
    "Decisión adoptada y responsable de su validación.",
):
    anchor = insert_after(anchor, item, bullet=True)
anchor = insert_after(anchor, "3.6 Entregables de cada incremento", "Heading 2")
insert_after(anchor, "Cada incremento deberá producir código integrado, migraciones reproducibles, pruebas, evidencias, actualización de la matriz de trazabilidad y una breve descripción de uso.")

doc.save(path)
print(path.resolve())
