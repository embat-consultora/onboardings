import streamlit as st
from navigation import make_sidebar_admin
from page_utils import apply_page_config
from sheet_connection import save_to_google_sheet,get_worksheet
import file_utils
import data_utils
import variables
from datetime import date
import json
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "cartaOfertaHotel"
apply_page_config()
make_sidebar_admin()

st.markdown(
    f"<h2 style='text-align: center;'>Carta Oferta</h2>",
    unsafe_allow_html=True
)
tipo =st.session_state["tipo"] 
title, dateHeader = st.columns([3,1])
with title:
    st.header("Datos del nuevo ingreso")
    st.write("Completa el siguiente formulario para registrar el nuevo posible ingreso y generar un carta de oferta")
with dateHeader:
    fecha_creacion = date.today().strftime("%d/%m/%Y")
    st.text_input("Fecha Formulario", value=str(fecha_creacion), disabled=True)

col1, col2 = st.columns(2)
with col1:
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        if not data_utils.is_valid_email(email):
            st.warning("📧 El formato del email no es correcto")
with col2:
        apellido = st.text_input("Apellido")


col1, col2 = st.columns(2)
with col1:
    posicion = st.text_input("Posición")
    departamento = st.text_input("Departamento")

with col2:
    valor_contrato = variables.tipoContrato
    tipo_contrato = st.selectbox("Tipo Contrato", valor_contrato,
        index=valor_contrato.index(valor_contrato) if valor_contrato in valor_contrato else 0)

    tipo_contrato_custom = ""
    if tipo_contrato == "Otro":
        tipo_contrato_custom = st.text_input("Especifique tipo de contrato")

col1, col2 = st.columns(2)

fecha_valida = date.today()
with col1:
    fecha_incorporacion = st.date_input(
        "Fecha estimada de incorporación",
        value=fecha_valida
    )
    retribucion_fija = st.text_input("Retribución fija" )
with col2:
    retribucion_variable = st.text_input("Retribución variable (si aplica)")
    condiciones = st.text_input("Condiciones horarias y teletrabajo")

st.subheader("Beneficios")
beneficiosLista = get_worksheet(variables.sheetId,variables.tabBeneficios)
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
campos_obligatorios_completos = (
    nombre.strip() != "" and
    apellido.strip() != "" and
    departamento.strip() != "" and
    posicion.strip() != "" and
    retribucion_fija.strip() != "" and
    condiciones.strip() != ""
)
# ---------------------- GUARDAR DATOS ----------------------
if st.button("Generar Carta", disabled=not campos_obligatorios_completos):
    beneficios_json = {
        beneficio: st.session_state.get(f"checkbox_{beneficio}", False)
        for beneficio in opciones_beneficios
    }
    data = {
        "Fecha creación": fecha_creacion,
        "Email":email,
        "Nombre": nombre,
        "Apellido": apellido,
        "Posición": posicion,
        "Departamento": departamento,
        "Condiciones":condiciones,
        "Fecha incorporación": fecha_incorporacion.strftime("%d/%m/%Y"),
        "Tipo contrato": tipo_contrato,
        "Retribución fija": retribucion_fija,
        "Retribución variable": retribucion_variable,
        "Beneficios": json.dumps(beneficios_json, ensure_ascii=False),
        "Estado": "Iniciado",
        "Tipo": tipo,
    }


    with st.spinner("Guardando datos y generando carta... puede tardar unos segundos"):
        try:
            save_to_google_sheet(data, variables.connectionOnboarding)
            file_utils.generarCarta(data,tipo)
            st.success("✅ Onboarding guardado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar los datos: {e}")
