import streamlit as st
from navigation import make_sidebar_admin
from page_utils import apply_page_config
import json
import variables
import pandas as pd
from sheet_connection import getOnboardings,get_worksheet
from modulos.secciones import (
    seccion_informacion_personal,
    seccion_informacion_laboral,
    seccion_informacion_remuneracion,
    seccion_informacion_general
)
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "finalizados"
apply_page_config()
make_sidebar_admin()

st.markdown(
    f"<h2 style='text-align: center;'>FINALIZADOS</h2>",
    unsafe_allow_html=True
)
st.markdown("""
Aquí encontrarás los **onboardings que están finalizados o cancelados**.
""")
st.set_page_config(page_title="Onboardings en progreso", layout="wide")

# Leer datos del sheet
with st.spinner("Cargando datos, puede que tarde unos segundos"):
    df = getOnboardings()
    beneficiosLista = get_worksheet(variables.sheetId,variables.tabBeneficios)
if df.empty or "Estado" not in df.columns:
    st.warning("No se encontraron datos o falta la columna 'Estado'")
    st.stop()
df_in_progress = df[df["Estado"].isin([variables.estados[3],variables.estados[4]])]

if df_in_progress.empty:
    st.info("No hay onboardings en finalizados.")
    st.stop()

# Mostrar selectbox con emails
emails_disponibles = df_in_progress["Email"].dropna().unique().tolist()
st.header("")
colSelector ,colSpace,  colCarta, colRefresh = st.columns(4)
with colSelector:
    email_seleccionado = st.selectbox("Seleccioná un onboarding", emails_disponibles)
    onboarding = df_in_progress[df_in_progress["Email"] == email_seleccionado].iloc[0]
    data_inicial = onboarding.to_dict()

with colSpace:
    st.write("")
    if st.button("🔄"):
        getOnboardings.clear()
        df = getOnboardings()

colTitle, colEstado = st.columns(2)
with colTitle:
    st.subheader("📋 Detalles del onboarding")
with colEstado:
    valor_actual = data_inicial.get("Estado", "Iniciado")  # valor por defecto
    try:
        index_estado = variables.estados.index(valor_actual)
    except ValueError:
        index_estado = 0  # fallback si el valor no está en la lista

    estado = st.selectbox("Estado", variables.estados, index=index_estado)

infoPersonal = st.expander("🦸‍♂️ Información Personal")
with infoPersonal:
  datos_personales = seccion_informacion_personal(data_inicial,disabled=True)

infoLaboral = st.expander("🧳 Puesto Laboral")
with infoLaboral:
    containerBasico =st.container(border=True)
    with containerBasico:
        datos_laborales = seccion_informacion_laboral(data_inicial,hotel_sede_df=None,disabled=True)
    containerRemuneracion =st.container(border=True)
    with containerRemuneracion:
        datos_remuneracion = seccion_informacion_remuneracion(data_inicial,disabled=True)

infoGeneral = st.expander("💥 Información")
with infoGeneral:
    datos_generales = seccion_informacion_general(data_inicial,disabled=True)  

subirDocs = st.expander("⏫️ Documentos Subidos")
with subirDocs:
    for key, url in data_inicial.items():
        if key.startswith("Link ") and pd.notna(url) and str(url).strip():
            nombre = key.replace("Link ", "")
            st.markdown(f"{nombre}: [{nombre}]({url})")


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

