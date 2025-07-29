import streamlit as st
from datetime import datetime
import variables
import sheet_connection
st.title("📝 Formulario")

with st.form("form_buddy", clear_on_submit=True):
    st.subheader("👤 Información Manager")
    email_manager = st.text_input("Email del Manager*", placeholder="manager@empresa.com")

    st.subheader("🤝 Asignación de Buddy")
    buddy_nombre = st.text_input("Nombre del Buddy*")
    buddy_email = st.text_input("Email del Buddy*", placeholder="buddy@empresa.com")

    st.subheader("🔑 Personas Clave")
    personas_clave = st.text_area(
        "¿Qué personas debería conocer el nuevo ingreso durante la primera semana?",
        placeholder="Ej: Juan Pérez (IT), María López (RRHH)..."
    )

    st.subheader("📅 Reuniones Esenciales")
    reuniones = st.text_area(
        "Reuniones importantes que deberían agendarse",
        placeholder="Ej: Inducción con RRHH, tour por la sede..."
    )

    st.subheader("📝 Observaciones")
    observaciones = st.text_area("Observaciones específicas o recomendaciones adicionales")

    submitted = st.form_submit_button("Enviar")

# ---- Guardar en Google Sheets ----
if submitted:
    if not email_manager or not buddy_nombre or not buddy_email:
        st.warning("Por favor completa los campos obligatorios marcados con *")
    else:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        data = {
            "Fecha" : timestamp,
            "Email Manager" : email_manager,
            "Email" : buddy_email,
            "Nombre Buddy": buddy_nombre,
            "Personas Claves" : personas_clave,
            "Reuniones": reuniones,
            "Observaciones": observaciones
        }
           
        try:
            sheet_connection.save_to_google_sheet(data, variables.connectionformBuddy)
            st.success("✅ Datos guardados correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar los datos: {e}")

