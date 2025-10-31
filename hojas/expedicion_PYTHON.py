import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_PYTHON.docx"
}

ALIAS = {
    "NORMAL": "Sin Cualificam"
}
ALIAS_INVERSO = {v: k for k, v in ALIAS.items()}

def _is_yes(s: pd.Series) -> pd.Series:
    """True cuando el valor equivale a 'sí' (robusto a variantes)."""
    ss = s.astype(str).str.strip().str.lower()
    ss = ss.str.replace("í", "i")  # normaliza 'sí' -> 'si'
    return ss.isin({"si", "yes", "true", "1", "verdadero"})

def run(df: pd.DataFrame):
    st.header("🐍 Expedición título - Máster Python")

    df.columns = df.columns.str.strip()

    columnas_requeridas = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO", "Nº TITULO",
        "NOMBRE CURSO EXACTO EN TITULO", "PROMOCION EN LA QUE FINALIZA",
        "FECHA EXPEDICIÓN", "FECHA"
    ]

    col_entregado = "ENTREGADO AL ALUMNO/A"

    # Revisar columnas
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        st.error("❌ Faltan columnas requeridas en el Excel.")
        st.write("Esperadas:", columnas_requeridas)
        st.write("Encontradas:", list(df.columns))
        return

    # ✅ Filtrar alumnos ya entregados
    if col_entregado in df.columns:
        df = df[~_is_yes(df[col_entregado])].copy()
    else:
        st.info("ℹ️ No se encontró la columna 'ENTREGADO AL ALUMNO/A'. No se aplicó filtro.")

    if df.empty:
        st.success("✅ No hay títulos de Python pendientes (todos entregados).")
        return

    df["NOMBRE_COMPLETO"] = df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()

    seleccionado = st.selectbox("Selecciona un alumno", sorted(df["NOMBRE_COMPLETO"].unique()))
    tipo_visible = st.radio("Selecciona tipo de plantilla", list(ALIAS.values()))
    tipo_plantilla = ALIAS_INVERSO[tipo_visible]
    plantilla_path = PLANTILLAS[tipo_plantilla]

    if seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar Documento"):
            try:
                pdf_path = generar_documento(alumno, plantilla_path, prefijo="TITULO_PYTHON")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar",
                        f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
