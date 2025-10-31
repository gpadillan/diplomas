import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

# Plantillas reales
PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_CIBER_NORMAL.docx",
    "CUALIFICAN": "hojas/plantillas/TITULO_CIBER_CUALIFICAN.docx"
}

# Alias para mostrar en interfaz
ALIAS = {
    "NORMAL": "Sin Cualificam",
    "CUALIFICAN": "Con Cualificam"
}
ALIAS_INVERSO = {v: k for k, v in ALIAS.items()}


def _is_yes(s: pd.Series) -> pd.Series:
    """Detecta si equivale a 'sí'"""
    ss = s.astype(str).str.strip().str.lower()
    ss = ss.str.replace("í", "i")  # normalizar SÍ -> SI
    return ss.isin({"si", "yes", "true", "verdadero", "1"})


def run(df: pd.DataFrame):
    st.header("🔐 Expedición título - CIBERSEGURIDAD")

    df.columns = df.columns.str.strip()

    columnas_necesarias = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO",
        "NOMBRE CURSO EXACTO EN TITULO",
        "PROMOCION EN LA QUE FINALIZA",
        "FECHA", "FECHA EXPEDICIÓN", "Nº TITULO"
    ]
    col_entregado = "ENTREGADO AL ALUMNO/A"

    # Validación columnas básicas
    if not all(col in df.columns for col in columnas_necesarias):
        st.error("❌ Faltan columnas necesarias en el Excel.")
        st.write("Se esperaban:", columnas_necesarias)
        st.write("Se encontraron:", list(df.columns))
        return

    # ✅ Filtrar registros ya entregados
    if col_entregado in df.columns:
        df = df[~_is_yes(df[col_entregado])].copy()
    else:
        st.info("ℹ️ No se encontró la columna 'ENTREGADO AL ALUMNO/A'. No se filtró por entregados.")

    # Si ya no queda nadie por título
    if df.empty:
        st.warning("✅ Todos los títulos de Ciberseguridad ya han sido entregados.")
        return

    # Nombre completo
    df["NOMBRE_COMPLETO"] = df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()

    seleccionado = st.selectbox(
        "Selecciona un alumno",
        sorted(df["NOMBRE_COMPLETO"].unique())
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
