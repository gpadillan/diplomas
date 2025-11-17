import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

# Plantillas
PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_EERR_NORMAL.docx",
    "CUALIFICAN": "hojas/plantillas/TITULO_EERR_CUALIFICAN.docx"
}

# Alias visibles para el usuario
ALIAS = {
    "NORMAL": "Sin Cualificam",
    "CUALIFICAN": "Con Cualificam"
}
ALIAS_INVERSO = {v: k for k, v in ALIAS.items()}


def run(df: pd.DataFrame):
    st.header("🎓 Expedición título - Energías Renovables")

    df = df.copy()
    df.columns = df.columns.str.strip()

    # 👉 Si no existe FECHA pero sí FECHA EXPEDICIÓN, la creamos
    if "FECHA" not in df.columns and "FECHA EXPEDICIÓN" in df.columns:
        df["FECHA"] = df["FECHA EXPEDICIÓN"]

    columnas_requeridas = [
        "NOMBRE",
        "APELLIDOS",
        "DNI ALUMNO",
        "Nº TITULO",
        "NOMBRE CURSO EXACTO EN TITULO",
        "PROMOCION EN LA QUE FINALIZA",
        "FECHA EXPEDICIÓN",
        "FECHA",
    ]

    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        st.error("❌ Faltan columnas requeridas en el Excel.")
        st.write("Esperadas:", columnas_requeridas)
        st.write("Faltan:", faltantes)
        st.write("Encontradas:", list(df.columns))
        return

    # Limpieza básica de filas
    df = df.dropna(how="all")
    df = df[~df["Nº TITULO"].isna() & ~df["DNI ALUMNO"].isna()]

    if df.empty:
        st.warning("No hay registros válidos para mostrar.")
        return

    # Nombre completo para el selector
    df["NOMBRE_COMPLETO"] = (
        df["NOMBRE"].astype(str).str.strip()
        + " "
        + df["APELLIDOS"].astype(str).str.strip()
    )

    seleccionado = st.selectbox(
        "Selecciona un alumno",
        df["NOMBRE_COMPLETO"].unique()
    )

    tipo_visible = st.radio(
        "Selecciona tipo de plantilla",
        list(ALIAS.values())
    )
    tipo_plantilla = ALIAS_INVERSO[tipo_visible]
    plantilla_path = PLANTILLAS[tipo_plantilla]

    if seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == seleccionado].iloc[0]

        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar Documento"):
            try:
                docx_path = generar_documento(
                    alumno,
                    plantilla_path,
                    sufijo_tipo=tipo_plantilla
                )
                with open(docx_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar DOCX",
                        f,
                        file_name=os.path.basename(docx_path),
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
