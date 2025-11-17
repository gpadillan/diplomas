import streamlit as st
import pandas as pd
import requests
from msal import ConfidentialClientApplication

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

# ==============================
# 🔐 Configuración desde st.secrets
# ==============================
config = {
    "client_id": st.secrets["CLIENT_ID"],
    "tenant_id": st.secrets["TENANT_ID"],
    "client_secret": st.secrets["CLIENT_SECRET"],
    "domain": "grupomainjobs.sharepoint.com",
    "site_name": "EIP",  # 👈 sitio nuevo
    "file_name": "REGISTRO GENERAL DE TÍTULOS.xlsx",  # 👈 nombre del fichero
}

FILENAME = "REGISTRO_GENERAL_TITULOS.xlsx"


def get_access_token(config):
    authority = f"https://login.microsoftonline.com/{config['tenant_id']}"
    app = ConfidentialClientApplication(
        client_id=config["client_id"],
        client_credential=config["client_secret"],
        authority=authority,
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    return result.get("access_token", None)


def get_site_id(config, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = (
        f"https://graph.microsoft.com/v1.0/sites/"
        f"{config['domain']}:/sites/{config['site_name']}"
    )
    res = requests.get(url, headers=headers)
    if res.ok:
        return res.json()["id"]
    else:
        st.error(f"Error al obtener site_id: {res.status_code}, {res.text}")
        return None


def get_drive_id(site_id, token):
    """Obtiene el drive (biblioteca de Documentos) por defecto del sitio."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
    res = requests.get(url, headers=headers)
    if res.ok:
        return res.json()["id"]
    else:
        st.error(f"Error al obtener drive_id: {res.status_code}, {res.text}")
        return None


def find_file_in_drive(drive_id, file_name, token):
    """
    Busca el archivo por nombre dentro del drive.
    Devuelve el item_id del primer archivo que coincida.
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root/search(q='{file_name}')"
    )
    res = requests.get(url, headers=headers)
    if not res.ok:
        st.error(f"Error al buscar el archivo: {res.status_code}, {res.text}")
        return None

    data = res.json()
    items = data.get("value", [])
    if not items:
        st.error(f"No se ha encontrado ningún archivo llamado '{file_name}' en el sitio.")
        return None

    # Intentar coincidencia exacta por nombre
    for item in items:
        if item.get("name") == file_name:
            return item.get("id")

    # Si no hay exacta, coger el primero
    return items[0].get("id")


def download_excel(drive_id, item_id, token, filename=FILENAME):
    """Descarga el archivo dado su item_id dentro del drive."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
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

    # 1️⃣ Token
    token = get_access_token(config)
    if not token:
        st.error("No se pudo obtener token de autenticación.")
        return

    # 2️⃣ ID del sitio EIP
    site_id = get_site_id(config, token)
    if not site_id:
        st.error("No se pudo obtener ID del sitio.")
        return

    # 3️⃣ Drive (Documentos) del sitio
    drive_id = get_drive_id(site_id, token)
    if not drive_id:
        st.error("No se pudo obtener el drive del sitio.")
        return

    # 4️⃣ Buscar archivo por nombre
    item_id = find_file_in_drive(drive_id, config["file_name"], token)
    if not item_id:
        return  # ya se ha mostrado el error correspondiente

    # 5️⃣ Descargar Excel
    archivo = download_excel(drive_id, item_id, token)
    if not archivo:
        st.error("No se pudo descargar el archivo Excel.")
        return

    # 6️⃣ Cargar hojas del Excel
    all_sheets = pd.read_excel(archivo, sheet_name=None, header=2)

    hoja = st.selectbox("Selecciona una hoja", list(all_sheets.keys()))
    df = all_sheets[hoja]

    # 7️⃣ Llamar al módulo específico según la hoja
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
