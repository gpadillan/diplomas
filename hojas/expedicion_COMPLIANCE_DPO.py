import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

# Plantillas disponibles
PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_COMPLIANCEDPO.docx",
    "CUALIFICAN": "hojas/plantillas/TITULO_COMPLIANCEDPO_CUALIFICAN.docx"
}

# Alias legibles para el usuario
ALIAS = {
    "NORMAL": "Sin Cualificam",
    "CUALIFICAN": "Con Cualificam"
}
ALIAS_INVERSO = {v: k for k, v in ALIAS.items()}

def _is_yes_series(s: pd.Series) -> pd.Series:
    """Devuelve True donde el valor equivale a 'sí'."""
    if s is None:
        return pd.Series(False, index=pd.RangeIndex(0))
    ss = s.astype(str).str.strip().str.lower()
    # normalizamos 'sí' -> 'si'
    ss = ss.str.replace("í", "i")
    return ss.isin({"si", "yes", "true", "verdadero", "1"})

def run(df: pd.DataFrame):
    st.header("📜 Expedición título - Compliance y Protección de Datos")

    # Limpieza básica de cabeceras
    df.columns = df.columns.str.strip()

    columnas_necesarias = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO",
        "NOMBRE CURSO EXACTO EN TITULO",
        "PROMOCION EN LA QUE FINALIZA",
        "FECHA", "FECHA EXPEDICIÓN", "Nº TITULO"
    ]
    # La columna de filtro no es "necesaria" para generar título, pero si existe, filtramos
    col_entregado = "ENTREGADO AL ALUMNO/A"

    if not all(col in df.columns for col in columnas_necesarias):
        st.error("❌ Faltan columnas necesarias en el Excel.")
        st.write("Se esperaban:", columnas_necesarias)
        st.write("Se encontraron:", list(df.columns))
        return

    # ⛔️ EXCLUIR los que ya están entregados al alumno
    if col_entregado in df.columns:
        mask_entregado = _is_yes_series(df[col_entregado])
        df = df[~mask_entregado].copy()
    else:
        st.info("ℹ️ No se encontró la columna 'ENTREGADO AL ALUMNO/A'. No se aplicó filtro de entregados.")

    if df.empty:
        st.warning("No hay registros pendientes de expedición (todos marcados como entregados o no hay datos).")
        return

    # Nombre completo para selector
    df["NOMBRE_COMPLETO"] = (
        df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()
    )

    seleccionado = st.selectbox(
        "Selecciona un alumno",
        sorted(df["NOMBRE_COMPLETO"].dropna().unique())
    )

    tipo_visible = st.radio("Selecciona tipo de plantilla", list(ALIAS.values()))
    tipo_plantilla = ALIAS_INVERSO[tipo_visible]
    plantilla_path = os.path.join(os.path.dirname(__file__), "..", PLANTILLAS[tipo_plantilla])

    if seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar Documento"):
            try:
                pdf_path = generar_documento(alumno, plantilla_path, sufijo_tipo=tipo_plantilla)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar",
                        f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
