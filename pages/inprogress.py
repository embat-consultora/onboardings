import streamlit as st
from navigation import make_sidebar_admin
from page_utils import apply_page_config
import pandas as pd
import variables
from sheet_connection import getOnboardings,save_to_google_sheet, get_worksheet, upload_documents_to_drive
import data_utils
import json
import file_utils
from modulos.secciones import (
    seccion_informacion_personal,
    seccion_informacion_laboral,
    seccion_informacion_remuneracion,
    seccion_informacion_general
)
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "onboarding_list"
apply_page_config()
make_sidebar_admin()

st.markdown(
    f"<h2 style='text-align: center;'>ONBOARDINGS</h2>",
    unsafe_allow_html=True
)
st.markdown("""
Aquí encontrarás los **onboardings que están iniciados**.Puedes **modificarlos** y **agregar información**.

📝 Recuerda presionar el botón **Guardar** para que los datos se reflejen en la *carta*.

📧 Si no encuentras el **email de la persona que acabas de cargar**, clickea el botón **Refrescar**.

📄 También podrás **descargar la carta de oferta**.
""")
st.set_page_config(page_title="Onboardings en progreso", layout="wide")

# Leer datos del sheet
with st.spinner("Cargando datos, puede que tarde unos segundos"):
    df = getOnboardings()
if df.empty or "Estado" not in df.columns:
    st.warning("No se encontraron datos o falta la columna 'Estado'")
    st.stop()
df_in_progress = df[df["Estado"].isin([variables.estados[0], variables.estados[1],variables.estados[2]])]

if df_in_progress.empty:
    st.info("No hay onboardings en progreso.")
    st.stop()

# Mostrar selectbox con emails
emails_disponibles = df_in_progress["Email"].dropna().unique().tolist()
st.header("")
colSelector ,colSpace,  colCarta, colRefresh = st.columns(4)
with colSelector:
    email_seleccionado = st.selectbox("Seleccioná un onboarding", emails_disponibles)
    onboarding = df_in_progress[df_in_progress["Email"] == email_seleccionado].iloc[0]
    data_inicial = onboarding.to_dict()
with colCarta:
    st.write("")
    file_utils.generarCarta(data_inicial)
with colSpace:
    st.write("")
    if st.button("🔄"):
        getOnboardings.clear()
        df = getOnboardings()

colTitle, colFecha, colEstado,  = st.columns(3)
with colTitle:
    st.subheader("📋 Detalles del onboarding")
with colFecha:
    st.text_input("Fecha Onboarding",value=data_inicial.get("Fecha creación"), disabled=True)
with colEstado:
    valor_actual = data_inicial.get("Estado", "Iniciado")  # valor por defecto
    try:
        index_estado = variables.estados.index(valor_actual)
    except ValueError:
        index_estado = 0  # fallback si el valor no está en la lista
    estado = st.selectbox("Estado", variables.estados, index=index_estado)


hotelSede = get_worksheet(variables.sheetId,variables.tabHotelSede)
hotelPais = hotelSede[["Nombre", "Pais"]].dropna()

beneficiosLista = get_worksheet(variables.sheetId,variables.tabBeneficios)


infoPersonal = st.expander("🦸‍♂️ Información Personal", expanded=True)
with infoPersonal:
  datos_personales = seccion_informacion_personal(data_inicial)

infoLaboral = st.expander("🧳 Puesto Laboral")
with infoLaboral:
    containerBasico =st.container(border=True)
    with containerBasico:
        datos_laborales = seccion_informacion_laboral(data_inicial, hotel_sede_df=hotelPais)
    containerRemuneracion =st.container(border=True)
    with containerRemuneracion:
        datos_remuneracion = seccion_informacion_remuneracion(data_inicial)

infoGeneral = st.expander("💥 Información")
with infoGeneral:
    datos_generales = seccion_informacion_general(data_inicial)  

subirDocs = st.expander("⏫️ Subir Documentos")
with subirDocs:
    st.write("Documentos Subidos:")

    for key, url in data_inicial.items():
        if key.startswith("Link ") and pd.notna(url) and str(url).strip():
            nombre = key.replace("Link ", "")
            st.markdown(f"{nombre}: [{nombre}]({url})")

    cv = st.file_uploader("Subir CV")
    dni_doc = st.file_uploader("Subir DNI")
    ss = st.file_uploader("Seguridad Social")
    cuenta = st.file_uploader("Detalles de cuenta bancaria")


st.subheader("Beneficios")

# Guardar el último email seleccionado
if "last_email_selected" not in st.session_state:
    st.session_state.last_email_selected = None

# Actualizar checkboxes si cambia el email seleccionado
if st.session_state.last_email_selected != email_seleccionado:
    # Borrar todos los checkboxes anteriores
    for key in list(st.session_state.keys()):
        if key.startswith("checkbox_"):
            del st.session_state[key]

    # Cargar beneficios guardados del onboarding actual
    beneficios_guardados = {}
    if isinstance(data_inicial.get("Beneficios"), str):
        try:
            beneficios_guardados = json.loads(data_inicial["Beneficios"])
        except Exception:
            beneficios_guardados = {}

    # Setear nuevos valores de los checkboxes
    for beneficio in beneficiosLista["Nombre"].dropna().unique().tolist():
        key = f"checkbox_{beneficio}"
        st.session_state[key] = beneficios_guardados.get(beneficio, False)

    st.session_state.last_email_selected = email_seleccionado


beneficiosContainer = st.container(height=400)
with beneficiosContainer:
    opciones_beneficios = beneficiosLista["Nombre"].dropna().unique().tolist()
    for beneficio in opciones_beneficios:
        key = f"checkbox_{beneficio}"
        st.checkbox(beneficio, key=key)

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
estado = estado
campos_obligatorios_completos = (
    datos_personales["Nombre"].strip() != "" and
    apellido_ingreso.strip() != "" and
    dni.strip() != "" and
    email_ingreso.strip() != "" and
    data_utils.is_valid_email(email_ingreso)
)
# ---------------------- GUARDAR DATOS ----------------------
fecha_creacion = data_inicial["Fecha creación"]
if st.button("Guardar", disabled=not campos_obligatorios_completos):
    beneficios_json = {
        beneficio: st.session_state.get(f"checkbox_{beneficio}", False)
        for beneficio in opciones_beneficios
    }
    
    data = {
        "Fecha creación":fecha_creacion,
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
        "Estado": estado
    }
    files_dict = {
        "CV": cv,
        "DNI": dni_doc,
        "Seguridad Social": ss,
        "Cuenta Bancaria": cuenta
    }
    with st.spinner("Guardando datos y archivos."):
        try:
            archivos_a_subir = {k: v for k, v in files_dict.items() if v is not None}

            # Mantener links existentes
            for key, val in data_inicial.items():
                if key.startswith("Link ") and key not in data:
                    data[key] = val

            # Subir nuevos archivos
            if archivos_a_subir:
                try:
                    links = upload_documents_to_drive(email_ingreso, archivos_a_subir)
                    for k, v in links.items():
                        data[f"Link {k}"] = v
                except Exception as e:
                    st.warning(f"⚠️ No se pudieron subir algunos archivos a Drive: {e}")

        except Exception as e:
            st.warning(f"No se pudieron subir los archivos a Drive: {e}")
        
        try:
            save_to_google_sheet(data)
            st.success("✅ Onboarding guardado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar los datos: {e}")
