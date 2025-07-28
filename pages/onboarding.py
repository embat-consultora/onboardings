import streamlit as st
from navigation import make_sidebar_admin
from page_utils import apply_page_config
from sheet_connection import get_worksheet,save_to_google_sheet,upload_documents_to_drive
import data_utils
import file_utils
import variables
from datetime import date
import json
from modulos.secciones import (
    seccion_informacion_personal,
    seccion_informacion_laboral,
    seccion_informacion_remuneracion,
    seccion_informacion_general
)
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "onboarding"
apply_page_config()
make_sidebar_admin()
hotelSede = get_worksheet(variables.sheetId,variables.tabHotelSede)
hotelPais = hotelSede[["Nombre", "Pais"]].dropna()

beneficiosLista = get_worksheet(variables.sheetId,variables.tabBeneficios)
st.markdown(
    f"<h2 style='text-align: center;'>NUEVO ONBOARDING</h2>",
    unsafe_allow_html=True
)

title, dateHeader = st.columns([3,1])
with title:
    st.header("Datos del nuevo ingreso")
    st.write("Completa el siguiente formulario para registrar una nueva incorporación")
with dateHeader:
    fecha_creacion = date.today().strftime("%d/%m/%Y")
    st.text_input("Fecha Formulario", value=str(fecha_creacion), disabled=True)

infoPersonal = st.expander("🦸‍♂️ Información Personal")
with infoPersonal:
  datos_personales = seccion_informacion_personal()

infoLaboral = st.expander("🧳 Puesto Laboral")
with infoLaboral:
    containerBasico =st.container(border=True)
    with containerBasico:
        datos_laborales = seccion_informacion_laboral(hotel_sede_df=hotelPais)
    containerRemuneracion =st.container(border=True)
    with containerRemuneracion:
        datos_remuneracion = seccion_informacion_remuneracion()

infoGeneral = st.expander("💥 Información")
with infoGeneral:
    datos_generales = seccion_informacion_general()  

subirDocs = st.expander("⏫️ Subir Documentos")
with subirDocs:
    cv = st.file_uploader("Subir CV")
    dni_doc = st.file_uploader("Subir DNI")
    ss = st.file_uploader("Seguridad Social")
    cuenta = st.file_uploader("Detalles de cuenta bancaria")


st.subheader("Beneficios")
beneficiosContainer = st.container(height=400)
with beneficiosContainer:
    opciones_beneficios = beneficiosLista["Nombre"].dropna().unique().tolist()
    for beneficio in opciones_beneficios:
        key = f"checkbox_{beneficio}"
        st.checkbox(beneficio,value=True, key=key)

    # Acceso posterior:
    seleccionados = [
        beneficio for beneficio in opciones_beneficios
        if st.session_state.get(f"checkbox_{beneficio}", False)
    ]
nombre_ingreso =datos_personales["Nombre"]
apellido_ingreso = datos_personales["Apellido"]
dni = datos_personales["DNI"]
email_ingreso = datos_personales["Email"]

posicion = datos_laborales["Posición"]
departamento= datos_laborales["Departamento"]
tipo_contrato= datos_laborales["Tipo contrato"]
nombre_manager= datos_laborales["Manager"]
mail_manager= datos_laborales["Mail Manager"]
tipuesto_reportepo= datos_laborales["Puesto reporte"]
tipo= datos_laborales["Tipo"]
puesto_reporte= datos_laborales["Puesto reporte"]
tipo_contrato_custom= datos_laborales["Tipo contrato custom"]
tipoPerfil= datos_laborales["Tipo perfil"]
ubicacion= datos_laborales["Ubicación"]
nombre_superior= datos_laborales["Superior"]
mail_superior= datos_laborales["Mail Superior"]
nombre_secretaria= datos_laborales["Secretaría Dirección"]
mail_secretaria= datos_laborales["Mail Secretaría"]

fecha_incorporacion= datos_remuneracion["Fecha incorporación"]
retribucion_fija= datos_remuneracion["Retribución fija"] 
condiciones= datos_remuneracion["Condiciones"] 
retribucion_variable= datos_remuneracion["Retribución variable"] 
 
nombre_hrbp= datos_generales["HRBP"] 
nombre_recruiter= datos_generales["Recruiter"] 
mail_completa= datos_generales["Mail TA"] 
mail_hrbp= datos_generales["Mail HRBP"] 
nombre_completa= datos_generales["Nombre TA"] 

campos_obligatorios_completos = (
    datos_personales["Nombre"].strip() != "" and
    apellido_ingreso.strip() != "" and
    dni.strip() != "" and
    email_ingreso.strip() != "" and
    data_utils.is_valid_email(email_ingreso)
)
# ---------------------- GUARDAR DATOS ----------------------
if st.button("Guardar", disabled=not campos_obligatorios_completos):
    beneficios_json = {
        beneficio: st.session_state.get(f"checkbox_{beneficio}", False)
        for beneficio in opciones_beneficios
    }
    data = {
        "Fecha creación": fecha_creacion,
        "Nombre": nombre_ingreso,
        "Apellido": apellido_ingreso,
        "DNI": dni,
        "Email": email_ingreso,
        "Posición": posicion,
        "Departamento": departamento,
        "Puesto reporte": puesto_reporte,
        "Ubicación": ubicacion,
        "Fecha incorporación": fecha_incorporacion.strftime("%d/%m/%Y"),
        "Tipo contrato": tipo_contrato,
        "Condiciones": condiciones,
        "Retribución fija": retribucion_fija,
        "Retribución variable": retribucion_variable,
        "Tipo perfil": tipoPerfil,
        "Nombre TA": nombre_completa,
        "Mail TA": mail_completa,
        "Manager": nombre_manager,
        "Mail Manager": mail_manager,
        "Superior": nombre_superior if 'nombre_superior' in locals() else "",
        "Mail Superior": mail_superior if 'mail_superior' in locals() else "",
        "HRBP": nombre_hrbp,
        "Mail HRBP": mail_hrbp,
        "Secretaría Dirección": nombre_secretaria if 'nombre_secretaria' in locals() else "",
        "Mail Secretaría": mail_secretaria if 'mail_secretaria' in locals() else "",
        "Recruiter": nombre_recruiter,
        "Beneficios": json.dumps(beneficios_json, ensure_ascii=False),
        "Estado": "Iniciado",
    }
    files_dict = {
        "CV": cv,
        "DNI": dni_doc,
        "Seguridad Social": ss,
        "Cuenta Bancaria": cuenta
    }
    with st.spinner("Guardando datos y generando carta... puede tardar unos segundos"):
        try:
            links = upload_documents_to_drive(email_ingreso, files_dict)
            for k, v in links.items():
                data[f"Link {k}"] = v
        except Exception as e:
            st.warning(f"No se pudieron subir los archivos a Drive: {e}")

        try:
            save_to_google_sheet(data)
            file_utils.generarCarta(data)
            st.success("✅ Onboarding guardado correctamente.")
            st.switch_page("pages/inprogress.py")
        except Exception as e:
            st.error(f"❌ Error al guardar los datos: {e}")
