# descargar_excel_sharepoint.py

import requests
from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv

# =====================================================
# 🔐 Cargar variables desde .env
# =====================================================
load_dotenv()

config = {
    "client_id": os.getenv("CLIENT_ID"),
    "tenant_id": os.getenv("TENANT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),

    # Dominio de SharePoint
    "domain": "grupomainjobs.sharepoint.com",

    # Nombre del sitio → viene del enlace /sites/EIP
    "site_name": "EIP",

    # 📌 Ruta EXACTA dentro de Documentos compartidos
    # Sin "Documentos compartidos" al inicio, Graph ya lo asume
    "file_path": "/FORMACIÓN Y EMPLEO SHAREPOINT/Gestión Integral de empresas/19. DG Excelencia Educativa/REGISTROS/REGISTRO GENERAL DE TÍTULOS.xlsx"
}

# =====================================================
# 🔑 Obtener token (Azure AD / MSAL)
# =====================================================
def get_access_token(config):
    authority = f"https://login.microsoftonline.com/{config['tenant_id']}"
    app = ConfidentialClientApplication(
        client_id=config["client_id"],
        client_credential=config["client_secret"],
        authority=authority
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    return result.get("access_token", None)

# =====================================================
# 🔍 Obtener ID del sitio SharePoint
# =====================================================
def get_site_id(config, token):
    headers = {"Authorization": f"Bearer {token}"}

    # /sites/EIP
    url = f"https://graph.microsoft.com/v1.0/sites/{config['domain']}:/sites/{config['site_name']}"

    res = requests.get(url, headers=headers)

    if res.ok:
        return res.json()["id"]
    else:
        print(f"❌ Error al obtener site_id: {res.status_code}\n{res.text}")
        return None

# =====================================================
# 📥 Descargar el archivo Excel
# =====================================================
def download_excel(config, token, site_id, filename="REGISTRO_GENERAL_TITULOS.xlsx"):
    headers = {"Authorization": f"Bearer {token}"}

    # Ruta GRAPH definitiva
    url = (
        f"https://graph.microsoft.com/v1.0/sites/{site_id}"
        f"/drive/root:{config['file_path']}:/content"
    )

    res = requests.get(url, headers=headers)

    if res.ok:
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"✅ Archivo descargado correctamente: {filename}")
        return filename

    else:
        print(f"❌ Error al descargar archivo: {res.status_code}\n{res.text}")
        return None

# =====================================================
# ▶️ MAIN
# =====================================================
if __name__ == "__main__":
    print("🔑 Obteniendo token...")
    token = get_access_token(config)

    if token:
        print("✅ Token obtenido correctamente.")

        print("\n🔍 Obteniendo ID del sitio SharePoint...")
        site_id = get_site_id(config, token)

        if site_id:
            print(f"✅ ID del sitio obtenido: {site_id}")

            print("\n📥 Descargando archivo Excel...")
            file = download_excel(config, token, site_id)

            if file:
                print(f"🎉 Proceso finalizado: {file}")
            else:
                print("❌ No se pudo descargar el archivo.")
        else:
            print("❌ No se pudo obtener el ID del sitio.")

    else:
        print("❌ Error al generar el token.")
