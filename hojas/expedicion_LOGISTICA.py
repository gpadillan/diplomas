import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

# Rutas relativas a las plantillas
PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_LOGISTICA_NORMAL.docx",
}

# Alias para mostrar nombres más legibles
ALIAS = {
    "NORMAL": "Sin Cualificam",
}
ALIAS_INVERSO = {v: k for k, v in ALIAS.items()}

def run(df: pd.DataFrame):
    st.header("🚛 Expedición título - LOGÍSTICA")

    df.columns = df.columns.str.strip()

    columnas_requeridas = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO", "Nº TITULO",
        "FECHA", "FECHA EXPEDICIÓN", "NOMBRE CURSO EXACTO EN TITULO",
        "PROMOCION EN LA QUE FINALIZA"
    ]

    if not all(col in df.columns for col in columnas_requeridas):
        st.error("❌ Faltan columnas requeridas en el Excel.")
        st.write("Esperadas:", columnas_requeridas)
        st.write("Encontradas:", list(df.columns))
        return

    df["NOMBRE_COMPLETO"] = df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()

    seleccionado = st.selectbox("Selecciona un alumno", df["NOMBRE_COMPLETO"].unique())

    tipo_visible = st.radio("Selecciona tipo de plantilla", list(ALIAS.values()))
    tipo_plantilla = ALIAS_INVERSO[tipo_visible]
    plantilla_path = PLANTILLAS[tipo_plantilla]

    if seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar Documento"):
            try:
                docx_path = generar_documento(alumno, plantilla_path, sufijo_tipo=tipo_plantilla)
                with open(docx_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar DOCX",
                        f,
                        file_name=os.path.basename(docx_path),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
