import logging
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile
import os
import variables

logging.basicConfig(level=logging.DEBUG)
@st.cache_resource(show_spinner=True)
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets[variables.connectionOnboarding]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client
@st.cache_data(ttl=3600)
def get_worksheet(sheet_id, worksheet_name):
    client = get_gspread_client()
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

def get_all_worksheets(connection):
    try:
        conn = st.connection(connection, type=GSheetsConnection,ttl=0)
        return conn

    except FileNotFoundError as e:
        logging.error(f"Service account file not found: {e}")
        return None
    except gspread.exceptions.APIError as e:
        logging.error(f"Google Sheets API error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    
def create_gsheets_connection():
    try:
        connOnboarding = get_all_worksheets('nuevoOnboarding')
        return connOnboarding
    except Exception as e:
        st.error(f"Unable to connect to storage: {e}")
        logging.error(e, stack_info=True, exc_info=True)
        return None
@st.cache_data(ttl=3600)  
def getOnboardings():
    logging.info("Submitting records")
    conn = create_gsheets_connection()

    if conn is None or not hasattr(conn, "read"):
        raise ValueError("❌ Conexión inválida. No se puede leer la hoja.")

    try:
        existing_data = conn.read(worksheet="onboarding", ttl=0)
        if existing_data is None:
            raise ValueError("❌ No se pudo leer la hoja 'onboarding'")
        else:
            return existing_data
    except Exception as e:
        logging.error(f"Error al leer la hoja: {e}", exc_info=True)
        raise

def save_to_google_sheet(data, sheet):
    logging.info("Submitting records")
    conn = create_gsheets_connection()

    if conn is None or not hasattr(conn, "read"):
        raise ValueError("❌ Conexión inválida. No se puede leer la hoja.")

    try:
        existing_data = conn.read(worksheet=sheet, ttl=0)
        if existing_data is None:
            raise ValueError("❌ No se pudo leer la hoja 'onboarding'")
    except Exception as e:
        logging.error(f"Error al leer la hoja: {e}", exc_info=True)
        raise
    email_col = "Email" 

    # Asegurar que la columna existe en la hoja
    if email_col not in existing_data.columns:
        raise ValueError(f"❌ La hoja no contiene la columna '{email_col}'")

    # Buscar si ya existe una fila con ese mail
    index_match = existing_data[existing_data[email_col] == data[email_col]].index

    if len(index_match) > 0:
        # ✅ Si existe, actualizamos esa fila
        row_index = index_match[0]
        for col in existing_data.columns:
            existing_data.at[row_index, col] = data.get(col, "")
        logging.info(f"Actualizando fila existente para {data[email_col]}")
    else:
        # ➕ Si no existe, agregamos nueva fila
        new_row = pd.DataFrame([data], columns=existing_data.columns)
        existing_data = pd.concat([existing_data, new_row], ignore_index=True)
        logging.info(f"Agregando nueva fila para {data[email_col]}")

    # Subir los datos actualizados
    try:
        conn.update(worksheet=sheet, data=existing_data)
        logging.info("Submitting successfully")
    except Exception as e:
        logging.error(f"Error al actualizar la hoja: {e}", exc_info=True)
        raise


    
def update_google_sheet(connection, sheet_id, worksheet_name, dataframe):
    try:
        # Authenticate with the connection
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing"
        conn = st.connection(connection, type=GSheetsConnection)
        
        # Write the updated data to the specific worksheet
        conn.write(dataframe, spreadsheet=url, worksheet=worksheet_name)
        
        st.success(f"Data successfully updated in worksheet: {worksheet_name}")
    except FileNotFoundError as e:
        logging.error(f"Service account file not found: {e}")
        st.error("Service account file not found.")
    except gspread.exceptions.APIError as e:
        logging.error(f"Google Sheets API error: {e}")
        st.error("Failed to update data due to Google Sheets API error.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        st.error("An unexpected error occurred while updating the data.")

def convert_attrdict_to_dict(obj):
    import collections
    if isinstance(obj, collections.abc.Mapping):
        return {k: convert_attrdict_to_dict(v) for k, v in dict(obj).items()}
    elif isinstance(obj, list):
        return [convert_attrdict_to_dict(item) for item in obj]
    else:
        return obj

def create_drive_instance_from_secrets():
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        info = convert_attrdict_to_dict(st.secrets["onboarding"])

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        gauth = GoogleAuth()
        gauth.credentials = credentials

        drive = GoogleDrive(gauth)
        return drive

    except Exception as e:
        st.error(f"❌ Error al autenticar con Google Drive: {e}")
        raise

def upload_documents_to_drive(email, files_dict):
    drive = create_drive_instance_from_secrets()

    # Buscar carpeta por nombre y carpeta padre
    query = f"title = '{email}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if variables.driveFolderId:
        query += f" and '{variables.driveFolderId}' in parents"

    folder_list = drive.ListFile({'q': query}).GetList()

    if folder_list:
        folder = folder_list[0]
        folder_id = folder['id']
        st.info(f"📁 Carpeta ya existente para {email}")
    else:
        folder_metadata = {
            'title': email,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if variables.driveFolderId:
            folder_metadata['parents'] = [{'id': variables.driveFolderId}]
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']
        st.success(f"✅ Carpeta creada para {email}")

    uploaded_links = {}

    for doc_name, file_obj in files_dict.items():
        try:
            # Buscar archivo existente
            query_file = f"title = '{doc_name}' and '{folder_id}' in parents and trashed = false"
            existing_files = drive.ListFile({'q': query_file}).GetList()

            if existing_files:
                # Si existe, sobreescribir (usamos el ID directamente)
                existing_file = existing_files[0]
                file_drive = drive.CreateFile({'id': existing_file['id']})
                st.info(f"🔄 Reemplazando archivo existente: {doc_name}")
            else:
                file_drive = drive.CreateFile({'title': doc_name, 'parents': [{'id': folder_id}]})
                st.info(f"⬆️ Subiendo nuevo archivo: {doc_name}")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(file_obj.getvalue())
                tmp.flush()
                file_drive.SetContentFile(tmp.name)
                file_drive.Upload()
            os.remove(tmp.name)

            uploaded_links[doc_name] = file_drive['alternateLink']

        except Exception as e:
            st.warning(f"⚠️ No se pudo subir/reemplazar {doc_name}: {e}")

    return uploaded_links