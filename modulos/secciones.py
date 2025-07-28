# form_sections.py

import streamlit as st
import data_utils
from datetime import date,datetime
import pandas as pd

def safe_get(data, key, default=""):
    value = data.get(key, default)
    return "" if pd.isna(value) else value

def seccion_informacion_personal(data_inicial=None, disabled=False):
    if data_inicial is None:
        data_inicial = {}

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre", value=safe_get(data_inicial,"Nombre"),disabled=disabled)
        if nombre == "":
            st.warning("Este campo es obligatorio", icon="⚠️")
        dni = st.text_input("DNI/NIE", value=safe_get(data_inicial,"DNI"),disabled=disabled)
    with col2:
        apellido = st.text_input("Apellido", value=safe_get(data_inicial,"Apellido"),disabled=disabled)
        if apellido == "":
            st.warning("Este campo es obligatorio", icon="⚠️")
        email = st.text_input("Email", value=safe_get(data_inicial,"Email"),disabled=disabled)
        if email == "":
            st.warning("Este campo es obligatorio", icon="⚠️")
        elif not data_utils.is_valid_email(email):
            st.warning("📧 El formato del email no es correcto")

    return {
        "Nombre": nombre,
        "Apellido": apellido,
        "DNI": dni,
        "Email": email
    }

import streamlit as st
import data_utils

def safe_get(diccionario, clave, default=""):
    valor = diccionario.get(clave, default)
    return "" if valor is None or str(valor).lower() == "nan" else valor

def seccion_informacion_laboral(data_inicial=None, hotel_sede_df=None, disabled=False):
    if data_inicial is None:
        data_inicial = {}

    tipoOptions = ["Corporativo", "Hotel"]
    corp = ["Staff", "Manager", "Executive"]
    hotel = ["Personal Base", "Mandos Intermedios", "Dirección"]
    tipoContratoOptions = ["Discontinuo", "Fijo indefinido", "Temporal de sustitución", "Otro"]

    col1, col2 = st.columns(2)
    with col1:
        posicion = st.text_input("Posición", value=safe_get(data_inicial, "Posición"),disabled=disabled)
        
        valor_tipo = safe_get(data_inicial, "Tipo", "Corporativo")
        tipo = st.selectbox("Tipo", tipoOptions, index=tipoOptions.index(valor_tipo) if valor_tipo in tipoOptions else 0,disabled=disabled)
        
        departamento = st.text_input("Departamento", value=safe_get(data_inicial, "Departamento"),disabled=disabled)
        nombre_manager = st.text_input("Nombre Manager", value=safe_get(data_inicial, "Manager"),disabled=disabled)
        mail_manager = st.text_input("Mail Manager", value=safe_get(data_inicial, "Mail Manager"),disabled=disabled)
        if mail_manager and not data_utils.is_valid_email(mail_manager):
            st.warning("📧 El formato del email no es correcto")
        puesto_reporte = st.text_input("Puesto del reporte directo", value=safe_get(data_inicial, "Puesto reporte"),disabled=disabled)

    with col2:
        valor_contrato = safe_get(data_inicial, "Tipo contrato", "Fijo indefinido")
        tipo_contrato = st.selectbox("Tipo Contrato", tipoContratoOptions,
            index=tipoContratoOptions.index(valor_contrato) if valor_contrato in tipoContratoOptions else 0, disabled=
            disabled)

        tipo_contrato_custom = ""
        if tipo_contrato == "Otro":
            tipo_contrato_custom = st.text_input("Especifique tipo de contrato", value=safe_get(data_inicial, "Tipo contrato custom"),disabled=disabled)

        tipoPerfilLista = corp if tipo == "Corporativo" else hotel
        valor_perfil = safe_get(data_inicial, "Tipo perfil", tipoPerfilLista[0])
        tipoPerfil = st.selectbox("Tipo Perfil", tipoPerfilLista,
            index=tipoPerfilLista.index(valor_perfil) if valor_perfil in tipoPerfilLista else 0,disabled=disabled)

        nombre_superior = mail_superior = nombre_secretaria = mail_secretaria = ""

        if tipoPerfil == hotel[2]:  # "Dirección"
            nombre_superior = st.text_input("Nombre Superior Directo", value=safe_get(data_inicial, "Superior"),disabled=disabled)
            mail_superior = st.text_input("Mail Superior Directo", value=safe_get(data_inicial, "Mail Superior"),disabled=disabled)
            if mail_superior and not data_utils.is_valid_email(mail_superior):
                st.warning("📧 El formato del email no es correcto")
        elif tipoPerfil == corp[2]:  # "Executive"
            nombre_secretaria = st.text_input("Nombre Secretaría Dirección", value=safe_get(data_inicial, "Secretaría Dirección"),disabled=disabled)
            mail_secretaria = st.text_input("Mail Secretaría Dirección", value=safe_get(data_inicial, "Mail Secretaría"),disabled=disabled)
            if mail_secretaria and not data_utils.is_valid_email(mail_secretaria):
                st.warning("📧 El formato del email no es correcto")

        if hotel_sede_df is not None:
            paises_unicos = sorted(hotel_sede_df["Pais"].dropna().unique())
            pais_por_defecto = safe_get(data_inicial, "Pais", paises_unicos[0] if paises_unicos else "")
            pais_seleccionado = st.selectbox("🌍 Seleccioná un país", paises_unicos,
                index=paises_unicos.index(pais_por_defecto) if pais_por_defecto in paises_unicos else 0)

            nombres_filtrados = hotel_sede_df[hotel_sede_df["Pais"] == pais_seleccionado]["Nombre"].tolist()
            ubicacion_defecto = safe_get(data_inicial, "Ubicación")
            ubicacion = st.selectbox("Ubicación (Hotel - Sede)", nombres_filtrados,
                index=nombres_filtrados.index(ubicacion_defecto) if ubicacion_defecto in nombres_filtrados else 0,disabled=disabled)
        else:
            ubicacion = ""

    return {
        "Posición": posicion,
        "Tipo": tipo,
        "Departamento": departamento,
        "Manager": nombre_manager,
        "Mail Manager": mail_manager,
        "Puesto reporte": puesto_reporte,
        "Tipo contrato": tipo_contrato,
        "Tipo contrato custom": tipo_contrato_custom,
        "Tipo perfil": tipoPerfil,
        "Superior": nombre_superior,
        "Mail Superior": mail_superior,
        "Secretaría Dirección": nombre_secretaria,
        "Mail Secretaría": mail_secretaria,
        "Ubicación": ubicacion,
        "Pais": pais_seleccionado if hotel_sede_df is not None else ""
    }


def seccion_informacion_remuneracion(data_inicial=None, disabled=False):
    if data_inicial is None:
        data_inicial = {}

    col1, col2 = st.columns(2)
    try:
        raw_fecha = data_inicial.get("Fecha incorporación", "")
        fecha_valida = datetime.strptime(raw_fecha, "%d/%m/%Y").date() if raw_fecha else date.today()
    except Exception:
        fecha_valida = date.today()
    with col1:
        fecha_incorporacion = st.date_input(
            "Fecha estimada de incorporación",
            value=fecha_valida,
            disabled=disabled
        )
        retribucion_fija = st.text_input("Retribución fija", value=safe_get(data_inicial,"Retribución fija"),disabled=disabled)
    with col2:
        condiciones = st.text_input("Condiciones horarias y teletrabajo", value=safe_get(data_inicial,"Condiciones"),disabled=disabled)
        retribucion_variable = st.text_input("Retribución variable (si aplica)", value=safe_get(data_inicial,"Retribución variable"),disabled=disabled)

    return {
        "Fecha incorporación": fecha_incorporacion,
        "Retribución fija": retribucion_fija,
        "Condiciones": condiciones,
        "Retribución variable": retribucion_variable
    }

def seccion_informacion_general(data_inicial=None, disabled=False):
    if data_inicial is None:
        data_inicial = {}

    col1, col2 = st.columns(2)
    with col1:
        nombre_hrbp = st.text_input("Nombre HRBP", value=safe_get(data_inicial,"HRBP", " "),disabled=disabled)
        nombre_recruiter = st.text_input("Nombre Recruiter", value=safe_get(data_inicial,"Recruiter", " "),disabled=disabled)
        mail_completa = st.text_input("Mail de quien completa el formulario", value=safe_get(data_inicial,"Mail TA", " "),disabled=disabled)
    with col2:
        mail_hrbp = st.text_input("Mail HRBP", value=safe_get(data_inicial,"Mail HRBP"),disabled=disabled)
        nombre_completa = st.text_input("Nombre de quien completa el formulario", value=safe_get(data_inicial,"Nombre TA"),disabled=disabled)

    return {
        "HRBP": nombre_hrbp,
        "Recruiter": nombre_recruiter,
        "Mail TA": mail_completa,
        "Mail HRBP": mail_hrbp,
        "Nombre TA": nombre_completa
    }
