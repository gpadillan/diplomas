import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_RRHH_NORMAL.docx",
    "CUALIFICAM (31-32)": "hojas/plantillas/TITULO_RRHH_CUALIFICAM(31-32).docx",
    "CUALIFICAM (33 en adelante)": "hojas/plantillas/TITULO_RRHH_CUALIFICAM(33-EN ADELANTE).docx"
}

def run(df: pd.DataFrame):
    st.header("🧠 Expedición título - Recursos Humanos")

    df.columns = df.columns.str.strip()

    columnas_requeridas = ["NOMBRE", "APELLIDOS", "DNI ALUMNO", "Nº TITULO", "FECHA", "FECHA EXPEDICIÓN", "NOMBRE CURSO EXACTO EN TITULO", "PROMOCION EN LA QUE FINALIZA"]
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("❌ Faltan columnas requeridas.")
        st.write("Esperadas:", columnas_requeridas)
        st.write("Encontradas:", list(df.columns))
        return

    df["NOMBRE_COMPLETO"] = df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()

    alumno_seleccionado = st.selectbox("Selecciona un alumno", df["NOMBRE_COMPLETO"].unique())
    tipo_plantilla = st.radio("Selecciona tipo de plantilla", list(PLANTILLAS.keys()))
    plantilla_path = PLANTILLAS[tipo_plantilla]

    if alumno_seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == alumno_seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar PDF"):
            try:
                pdf_path = generar_documento(alumno, plantilla_path)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar PDF",
                        f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
