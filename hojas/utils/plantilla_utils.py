import os
import tempfile
import pandas as pd
from docx import Document
from docx.shared import Pt

def limpiar(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()

def reemplazar_campos_en_docx(doc: Document, campos: dict):
    for p in doc.paragraphs:
        for campo, valor in campos.items():
            if campo in p.text:
                for run in p.runs:
                    if campo in run.text:
                        run.text = run.text.replace(campo, valor)
                        if campo in ("{{NOMBRE}}", "{{APELLIDOS}}"):
                            run.font.size = Pt(37)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                reemplazar_campos_en_docx(cell, campos)

def generar_documento(alumno, plantilla_path: str, sufijo_tipo: str = "") -> str:
    doc = Document(plantilla_path)

    fecha = alumno.get("FECHA")
    fecha_exp = alumno.get("FECHA EXPEDICIÓN")

    fecha_str = pd.to_datetime(fecha).strftime("%d/%m/%Y") if pd.notna(fecha) else ""
    fecha_exp_str = pd.to_datetime(fecha_exp).strftime("%d/%m/%Y") if pd.notna(fecha_exp) else ""

    campos = {
        "{{NOMBRE}}": limpiar(alumno.get("NOMBRE")),
        "{{APELLIDOS}}": limpiar(alumno.get("APELLIDOS")),
        "{{DNI}}": limpiar(alumno.get("DNI ALUMNO")),
        "{{TITULO}}": limpiar(alumno.get("NOMBRE CURSO EXACTO EN TITULO")),
        "{{PROMOCION}}": limpiar(alumno.get("PROMOCION EN LA QUE FINALIZA")),
        "{{FECHA EXPEDICIÓN}}": fecha_exp_str,
        "{{FECHA}}": fecha_str,
        "{{NºTITULO}}": limpiar(alumno.get("Nº TITULO")),
    }

    reemplazar_campos_en_docx(doc, campos)

    temp_docx = tempfile.mktemp(suffix=".docx")
    output_name = f"TITULO_{sufijo_tipo.upper() or 'SIN_TIPO'}_{campos['{{DNI}}'] or 'sin_dni'}.docx"
    final_path = os.path.join(os.path.dirname(temp_docx), output_name)
    doc.save(final_path)

    return final_path
