from pathlib import Path

from docx import Document
from docx.shared import Cm, Pt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
path = PROJECT_ROOT / "docs/practica-3/Maqueta_Documentacion_Practica_3.docx"
doc = Document(path)
numbered = [p for p in doc.paragraphs if p.style.name == "List Number"]

for index, paragraph in enumerate(numbered):
    original = paragraph.text
    paragraph.style = doc.styles["Normal"]
    paragraph.paragraph_format.left_indent = Cm(0.6)
    paragraph.paragraph_format.first_line_indent = Cm(-0.3)
    paragraph.paragraph_format.line_spacing = 1.3
    paragraph.paragraph_format.space_after = Pt(2)
    if index < 15:
        paragraph.text = f"• {original}"
    else:
        paragraph.text = f"{index - 14}. {original}"

doc.save(path)
print(path.resolve())
