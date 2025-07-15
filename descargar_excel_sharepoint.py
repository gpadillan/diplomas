import requests
from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde .env
load_dotenv()

config = {
    "client_id": os.getenv("CLIENT_ID"),
    "tenant_id": os.getenv("TENANT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "domain": "grupomainjobs.sharepoint.com",
    "site_name": "GrupoMainjobs928",
    "file_path": "/ExpeciciónTitulos/REGISTRO GENERAL DE TÍTULOS (1).xlsx"
}

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
        print(f"❌ Error al obtener site_id: {res.status_code}, {res.text}")
        return None

def download_excel(config, token, site_id, filename="REGISTRO_GENERAL_TITULOS.xlsx"):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:{config['file_path']}:/content"
    res = requests.get(url, headers=headers)
    if res.ok:
        with open(filename, "wb") as f:
            f.write(res.content)
        return filename
    else:
        print(f"❌ Error al descargar archivo: {res.status_code}, {res.text}")
    return None

if __name__ == "__main__":
    print("🔑 Obteniendo token...")
    token = get_access_token(config)
    if token:
        print("✅ Token obtenido correctamente.")
        print("🔍 Obteniendo ID del sitio SharePoint...")
        site_id = get_site_id(config, token)
        if site_id:
            print(f"✅ ID del sitio obtenido: {site_id}")
            print("📥 Descargando archivo Excel...")
            file = download_excel(config, token, site_id)
            if file:
                print(f"✅ Archivo descargado correctamente: {file}")
            else:
                print("❌ Error al descargar el archivo.")
        else:
            print("❌ Error al obtener el ID del sitio.")
    else:
        print("❌ Error al obtener el token.")
