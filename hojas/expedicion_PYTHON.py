import os
import streamlit as st
import pandas as pd
from hojas.plantilla_streamlit import generar_documento  # ✅ CORREGIDO

PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_PYTHON.docx"
}

def run(df: pd.DataFrame):
    st.header("🐍 Expedición título - Máster Python")

    df.columns = df.columns.str.strip()

    columnas_requeridas = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO", "Nº TITULO",
        "NOMBRE CURSO EXACTO EN TITULO", "PROMOCION EN LA QUE FINALIZA",
        "FECHA EXPEDICIÓN", "FECHA"
    ]
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        st.error("❌ Faltan columnas requeridas en el Excel.")
        st.write("Esperadas:", columnas_requeridas)
        st.write("Encontradas:", list(df.columns))
        return

    df["NOMBRE_COMPLETO"] = df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()

    seleccionado = st.selectbox("Selecciona un alumno", df["NOMBRE_COMPLETO"].unique())

    plantilla_opcion = st.radio("Selecciona tipo de plantilla", list(PLANTILLAS.keys()))
    plantilla_path = PLANTILLAS[plantilla_opcion]

    if seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar PDF protegido"):
            try:
                pdf_path = generar_documento(alumno, plantilla_path, prefijo="TITULO_PYTHON")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar PDF",
                        f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
