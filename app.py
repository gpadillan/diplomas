import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar diseño ancho para mejor visualización
st.set_page_config(layout="wide")

# Importar módulos específicos por hoja
from hojas.expedicion_COMPLIANCE_DPO import run as run_compliance
from hojas.expedicion_RRHH import run as run_rrhh
from hojas.expedicion_DFINANCIERA import run as run_dfinanciera
from hojas.expedicion_BIM import run as run_bim
from hojas.expedicion_LOGISTICA import run as run_logistica
from hojas.expedicion_EERR import run as run_eerr
from hojas.expedicion_DF_SAP import run as run_df_sap
from hojas.expedicion_CIBER import run as run_ciber
from hojas.expedicion_PYTHON import run as run_python
from hojas.expedicion_FULLSTACK import run as run_fullstack
from hojas.expedicion_DPO_CIBER import run as run_dpo_ciber  # ✅ NUEVO

# Config SharePoint usando variables del entorno
config = {
    "client_id": os.getenv("CLIENT_ID"),
    "tenant_id": os.getenv("TENANT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "domain": "grupomainjobs.sharepoint.com",
    "site_name": "GrupoMainjobs928",
    "file_path": "/ExpeciciónTitulos/REGISTRO GENERAL DE TÍTULOS (1).xlsx"
}

FILENAME = "REGISTRO_GENERAL_TITULOS.xlsx"

def get_access_token(config):
    authority = f"https://login.microsoftonline.com/{config['tenant_id']}"
    app = ConfidentialClientApplication(
        client_id=config["client_id"],
        client_credential=config["client_secret"],
        authority=authority
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result.get("access_token", None)

def get_site_id(config, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{config['domain']}:/sites/{config['site_name']}"
    res = requests.get(url, headers=headers)
    if res.ok:
        return res.json()["id"]
    else:
        st.error(f"Error al obtener site_id: {res.status_code}, {res.text}")
        return None

def download_excel(config, token, site_id, filename=FILENAME):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:{config['file_path']}:/content"
    res = requests.get(url, headers=headers)
    if res.ok:
        with open(filename, "wb") as f:
            f.write(res.content)
        return filename
    else:
        st.error(f"Error al descargar archivo: {res.status_code}, {res.text}")
        return None

def main():
    st.title("📚 Expedición modular de títulos")

    token = get_access_token(config)
    if not token:
        st.error("No se pudo obtener token de autenticación.")
        return

    site_id = get_site_id(config, token)
    if not site_id:
        st.error("No se pudo obtener ID del sitio.")
        return

    archivo = download_excel(config, token, site_id)
    if not archivo:
        st.error("No se pudo descargar el archivo Excel.")
        return

    all_sheets = pd.read_excel(archivo, sheet_name=None, header=2)
    hoja = st.selectbox("Selecciona una hoja", list(all_sheets.keys()))
    df = all_sheets[hoja]

    # Llamar al módulo específico
    if hoja == "DPO-CIBERCOMPLIANCE":
        run_dpo_ciber(df)
    elif hoja == "COMPLIANCE-DPO":
        run_compliance(df)
    elif hoja == "RRHH":
        run_rrhh(df)
    elif hoja == "DFINANCIERA":
        run_dfinanciera(df)
    elif hoja == "BIM":
        run_bim(df)
    elif hoja == "LOGÍSTICA":
        run_logistica(df)
    elif hoja == "EERR":
        run_eerr(df)
    elif hoja == "DF-SAP":
        run_df_sap(df)
    elif hoja == "CIBER":
        run_ciber(df)
    elif hoja == "PYTHON":
        run_python(df)
    elif hoja == "FULLSTACK":
        run_fullstack(df)
    else:
        st.warning(f"No hay módulo implementado aún para '{hoja}'")
        st.dataframe(df)

if __name__ == "__main__":
    main()
