import os
import streamlit as st
import pandas as pd
from hojas.utils.plantilla_utils import generar_documento

# Rutas de plantillas
PLANTILLAS = {
    "NORMAL": "hojas/plantillas/TITULO_RRHH_NORMAL.docx",
    "CUALIFICAM (31-32)": "hojas/plantillas/TITULO_RRHH_CUALIFICAM(31-32).docx",
    "CUALIFICAM (33 en adelante)": "hojas/plantillas/TITULO_RRHH_CUALIFICAM(33-EN ADELANTE).docx"
}

# Alias para visibilidad en interfaz
ALIAS = {
    "NORMAL": "Sin Cualificam",
    "CUALIFICAM (31-32)": "Con Cualificam (31-32)",
    "CUALIFICAM (33 en adelante)": "Con Cualificam (33 en adelante)"
}
ALIAS_INVERSO = {v: k for k, v in ALIAS.items()}


def _is_yes(s: pd.Series) -> pd.Series:
    """True cuando el valor equivale a 'sí' (robusto a variantes)."""
    ss = s.astype(str).str.strip().str.lower()
    ss = ss.str.replace("í", "i")  # normaliza 'sí' -> 'si'
    return ss.isin({"si", "yes", "true", "1", "verdadero"})


def run(df: pd.DataFrame):
    st.header("🧠 Expedición título - Recursos Humanos")

    df.columns = df.columns.str.strip()

    columnas_requeridas = [
        "NOMBRE", "APELLIDOS", "DNI ALUMNO", "Nº TITULO",
        "FECHA", "FECHA EXPEDICIÓN", "NOMBRE CURSO EXACTO EN TITULO",
        "PROMOCION EN LA QUE FINALIZA"
    ]
    col_entregado = "ENTREGADO AL ALUMNO/A"

    if not all(col in df.columns for col in columnas_requeridas):
        st.error("❌ Faltan columnas requeridas.")
        st.write("Esperadas:", columnas_requeridas)
        st.write("Encontradas:", list(df.columns))
        return

    # ✅ Filtrar los alumnos que ya tienen el título entregado
    if col_entregado in df.columns:
        df = df[~_is_yes(df[col_entregado])].copy()
    else:
        st.info("ℹ️ No se encontró la columna 'ENTREGADO AL ALUMNO/A'. No se aplicó filtro.")

    if df.empty:
        st.success("✅ No hay títulos de RRHH pendientes (todos entregados).")
        return

    df["NOMBRE_COMPLETO"] = (
        df["NOMBRE"].astype(str).str.strip() + " " + df["APELLIDOS"].astype(str).str.strip()
    )

    alumno_seleccionado = st.selectbox("Selecciona un alumno", sorted(df["NOMBRE_COMPLETO"].unique()))

    tipo_visible = st.radio("Selecciona tipo de plantilla", list(ALIAS.values()))
    tipo_plantilla = ALIAS_INVERSO[tipo_visible]
    plantilla_path = PLANTILLAS[tipo_plantilla]

    if alumno_seleccionado:
        alumno = df[df["NOMBRE_COMPLETO"] == alumno_seleccionado].iloc[0]
        st.subheader("📋 Datos del alumno")
        st.write(alumno.astype(str))

        if st.button("🖨️ Generar Documento"):
            try:
                docx_path = generar_documento(alumno, plantilla_path, sufijo_tipo=tipo_plantilla)
                with open(docx_path, "rb") as f:
                    st.download_button(
                        "📥 Descargar",
                        f,
                        file_name=os.path.basename(docx_path),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
