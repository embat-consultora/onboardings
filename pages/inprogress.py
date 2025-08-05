import streamlit as st
from navigation import make_sidebar_admin
from page_utils import apply_page_config
import pandas as pd
import variables
from sheet_connection import getOnboardings,save_to_google_sheet, get_worksheet, upload_documents_to_drive
import data_utils
import json
import file_utils
from datetime import date
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
tipo =st.session_state["tipo"] 
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
tipo =st.session_state["tipo"] 

# Leer datos del sheet
with st.spinner("Cargando datos, puede que tarde unos segundos"):
    df = getOnboardings()
if df.empty or "Estado" not in df.columns:
    st.warning("No se encontraron datos o falta la columna 'Estado'")
    st.stop()
df_in_progress = df[df["Estado"].isin([variables.estados[0], variables.estados[1],variables.estados[2]])]
df_in_progress = df_in_progress[df_in_progress["Tipo"] == tipo]
if df_in_progress.empty:
    st.info("No hay onboardings en progreso.")
    if st.button("Traer últimos onboardings 🔄"):
        getOnboardings.clear()
        df = getOnboardings()
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
    file_utils.generarCarta(data_inicial, tipo)
with colSpace:
    st.write("")
    if st.button("🔄"):
        getOnboardings.clear()
        df = getOnboardings()
        df_in_progress = df[df["Estado"].isin([variables.estados[0], variables.estados[1],variables.estados[2]])]
        df_in_progress = df_in_progress[df_in_progress["Tipo"] == tipo]

if "last_email_selected" not in st.session_state:
    st.session_state.last_email_selected = None

if st.session_state.last_email_selected is None:
    st.session_state.last_email_selected = email_seleccionado
colTitle, colFecha, colEstado,  = st.columns(3)
with colTitle:
    st.subheader("📋 Detalles del onboarding")
with colEstado:
    st.text_input("Fecha Inicio Onboarding",value=data_inicial.get("Fecha creación"), disabled=True)

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
    contrato = st.file_uploader("Contrato Firmado")

opciones_beneficios=''
if(tipo!="Hotel"):
    st.subheader("Beneficios")
    if "last_email_selected" not in st.session_state:
        st.session_state.last_email_selected = None

    # Inicializar beneficios si nunca se cargaron o si cambió el email
    email_cambio = st.session_state.last_email_selected != email_seleccionado
    beneficios_inicializados = any(k.startswith("checkbox_") for k in st.session_state)

    if email_cambio or not beneficios_inicializados:
        # Limpiar anteriores
        for key in list(st.session_state.keys()):
            if key.startswith("checkbox_"):
                del st.session_state[key]

        # Obtener beneficios guardados (si los hay)
        beneficios_guardados = {}
        if isinstance(data_inicial.get("Beneficios"), str):
            try:
                beneficios_guardados = json.loads(data_inicial["Beneficios"])
            except Exception:
                beneficios_guardados = {}

        # Guardar en session_state
        for beneficio in beneficiosLista["Nombre"].dropna().unique().tolist():
            key = f"checkbox_{beneficio}"
            st.session_state[key] = beneficios_guardados.get(beneficio, False)

        # Actualizar email actual
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
pais=datos_laborales["Pais"]

fecha_incorporacion= datos_remuneracion["Fecha incorporación"] 
retribucion_fija= datos_remuneracion["Retribución fija"] 
condiciones= datos_remuneracion["Condiciones"] 
retribucion_variable= datos_remuneracion["Retribución variable"] 
 
nombre_hrbp= datos_laborales["HRBP"] 
nombre_recruiter= datos_laborales["Recruiter"] 
mail_completa= datos_laborales["Mail TA"] 
mail_hrbp= datos_laborales["Mail HRBP"] 
nombre_completa= datos_laborales["Nombre TA"] 
campos_obligatorios_completos = (
    datos_personales["Nombre"].strip() != "" and
    apellido_ingreso.strip() != "" and
    dni.strip() != "" and
    email_ingreso.strip() != "" 
)
campos_obligatorios_finalizar = (
    datos_personales["Nombre"].strip() != "" and
    apellido_ingreso.strip() != "" and
    dni.strip() != "" and
    email_ingreso.strip() != "" and
    data_utils.is_valid_email(email_ingreso) and
    mail_manager.strip() != "" and
    nombre_manager.strip() != "" 
)

estadoContainer = st.expander("Estado")
with estadoContainer:
    col1, col2 = st.columns(2)
    valor_actual = data_inicial.get("Estado", "Iniciado")
    try:
        index_estado = variables.estados.index(valor_actual)
    except ValueError:
        index_estado = 0
    if not campos_obligatorios_finalizar:
            st.caption("⚠️ Completa primero todos los campos obligatorios para habilitar esta opción.")
    st.warning("Recordá que una vez que cambies el estado a Finalizado, automaticamente se enviará la información a managers y directores (según corresponda), revisar que toda la información sea correcta. Una vez que cambies el estado, no podrás volver a enviar la información")
    with col1:
        estado = st.selectbox("", variables.estados, index=index_estado, disabled=not campos_obligatorios_finalizar)
    with col2:
        if estado in [variables.estados[1], variables.estados[3]]:
            ofertaDate = data_inicial.get("Oferta Enviada")
            contratoDate = data_inicial.get("Contrato Firmado")

            # Obtener fecha actual como string
            hoy = date.today().strftime("%d/%m/%Y")

            if estado == variables.estados[1]:
                fecha_valor = hoy if pd.isna(ofertaDate) or not ofertaDate else ofertaDate
            else:
                fecha_valor = hoy if pd.isna(contratoDate) or not contratoDate else contratoDate

            st.text_input("Fecha", value=fecha_valor, disabled=True)
# ---------------------- GUARDAR DATOS ----------------------
fecha_creacion = data_inicial["Fecha creación"]
oferta_enviada = date.today().strftime("%d/%m/%Y") if estado == variables.estados[1] else ""
contrato_firmado = date.today().strftime("%d/%m/%Y") if estado == variables.estados[3] else ""
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
        "Pais": pais,
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
        "Estado": estado,
        "Oferta Enviada": oferta_enviada,
        "Tipo":tipo,
        "Contrato Firmado": contrato_firmado  
    }
    files_dict = {
        "CV": cv,
        "DNI": dni_doc,
        "Seguridad Social": ss,
        "Cuenta Bancaria": cuenta,
        "Contrato Firmado":contrato
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
            save_to_google_sheet(data, variables.connectionOnboarding)
            st.success("✅ Onboarding guardado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar los datos: {e}")
