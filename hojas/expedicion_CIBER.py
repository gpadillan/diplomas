import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

# Rutas relativas a las plantillas de Word
PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_CIBER_NORMAL.docx",
    "CUALIFICAN": "hojas/plantillas/TITULO_CIBER_CUALIFICAN.docx"
}

def run(df: pd.DataFrame):
    st.header("🔐 Expedición título - CIBERSEGURIDAD")

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # Validación de columnas obligatorias
    columnas_necesarias = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO",
        "NOMBRE CURSO EXACTO EN TITULO",
        "PROMOCION EN LA QUE FINALIZA",
        "FECHA", "FECHA EXPEDICIÓN", "Nº TITULO"
    ]
    if not all(col in df.columns for col in columnas_necesarias):
        st.error("❌ Faltan columnas necesarias en el Excel.")
        st.write("Se esperaban:", columnas_necesarias)
        st.write("Se encontraron:", list(df.columns))
        return

    # Combinar nombre completo
    df["NOMBRE_COMPLETO"] = df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()

    seleccionado = st.selectbox("Selecciona un alumno", df["NOMBRE_COMPLETO"].unique())
    plantilla_opcion = st.radio("Selecciona tipo de plantilla", list(PLANTILLAS.keys()))
    plantilla_path = os.path.join(os.path.dirname(__file__), "..", PLANTILLAS[plantilla_opcion])

    if seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar PDF protegido"):
            try:
                pdf_path = generar_documento(alumno, plantilla_path, sufijo_tipo=plantilla_opcion)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar PDF",
                        f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
