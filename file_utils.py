import streamlit as st
import io
import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm  # o Inches
import json
import locale
from datetime import datetime
from sheet_connection import getOnboardings

# Establecer locale en español (puede variar según el sistema: "es_ES.UTF-8" en Linux/Mac, "Spanish_Spain" en Windows)
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

fecha = datetime.strptime("24/04/2025", "%d/%m/%Y")
formateada = fecha.strftime("%-d de %B de %Y")   # -> "24 de abril de 2025"

def generarCartaInProgress(email, tipo):
    getOnboardings.clear()
    data = getOnboardings()
    dataCarta = data[data["Email"] == email].iloc[0]
    if dataCarta.to_dict():
        buffer = generar_docx_con_datos(dataCarta.to_dict(), tipo)
        nombre = dataCarta.get("Nombre", "") +"_"+ dataCarta.get("Apellido", "")
        file_name = f"carta_oferta_{nombre or 'sin_nombre'}"
        st.download_button(
            label="Descargar Carta Oferta",
            data=buffer,
            file_name=f"{file_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def generarCarta(dataCarta, tipo):
    if dataCarta:
        buffer = generar_docx_con_datos(dataCarta, tipo)
        nombre = dataCarta.get("Nombre", "") +"_"+ dataCarta.get("Apellido", "")
        file_name = f"carta_oferta_{nombre or 'sin_nombre'}"
        st.download_button(
            label="Descargar Carta Oferta",
            data=buffer,
            file_name=f"{file_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def generar_docx_con_datos(dataCarta, tipo="Corporativo"):
    base_path = os.path.dirname(os.path.abspath(__file__))
    beneficios_lista = []
    if tipo == 'Hotel':
        nombreCarta = "carta_template_hotel.docx"
    else:
        nombreCarta = "carta_template.docx"
        beneficios_dict = {}
        # Soporta dict o JSON string en dataCarta["Beneficios"]
        raw_beneficios = dataCarta.get("Beneficios", "{}")
        if isinstance(raw_beneficios, str):
            try:
                beneficios_dict = json.loads(raw_beneficios or "{}")
            except json.JSONDecodeError:
                beneficios_dict = {}
        elif isinstance(raw_beneficios, dict):
            beneficios_dict = raw_beneficios
        beneficios_lista = [k for k, v in beneficios_dict.items() if v]

    # --------- [NUEVO] Imagen: admite subir por Streamlit o ruta en dataCarta ---------
    # Prioridad: archivo subido -> ruta en dataCarta["LogoPath"] -> sin logo
    logo_inline = None

    # Si en tu app ya tenés un uploader en la UI:
    # up_logo = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="logo_uploader", accept_multiple_files=False)
    # if up_logo:
    #     # Guardar a archivo temporal para InlineImage
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(up_logo.name)[1]) as tmp:
    #         tmp.write(up_logo.read())
    #         tmp_path = tmp.name
    #     logo_inline = InlineImage(DocxTemplate(os.path.join(base_path,"files", nombreCarta)), tmp_path, width=Cm(4))
    #
    # Alternativa: si te llega una ruta en dataCarta:
    logo_path = 'image.png'  # e.g. "files/logo.png"
    if not logo_inline and logo_path:
        # Importante: InlineImage necesita la instancia del documento al construirse
        pass  # lo creamos luego de cargar la plantilla
    texto_relocation = ""
    texto_retribucion_variable= ""
    if dataCarta.get("Relocation") == "Sí":
        vuelo = dataCarta.get("Vuelo", "")
        semanas = dataCarta.get("Semanas", "")
        texto_relocation = (
            f"Recolocación: Para que tu proceso de mudanza sea lo más positivo posible, "
            f"te proporcionamos vuelo de ida ({vuelo}) y alojamiento durante {semanas} semanas."
        )
    if dataCarta.get("Retribución variable") != "":
        porcent = dataCarta.get("Retribución variable", "")
        texto_retribucion_variable = (
            f"Retribución variable: Bono variable equivalente al {porcent}% del salario bruto "
            f"anual condicionado al cumplimiento de objetivos de acuerdo con la política de retribución "
            f"variable de la empresa."
        ) 
    context = {
        "NOMBRE": dataCarta.get("Nombre", "") or "",
        "APELLIDO": dataCarta.get("Apellido", "") or "",
        "POSICION": dataCarta.get("Posición", "") or "",
        "DEPARTAMENTO": dataCarta.get("Departamento", "") or "",
        "FECHA_FORM": datetime.strptime(dataCarta.get("Fecha creación", ""), "%d/%m/%Y").strftime("%-d de %B de %Y") or "",
        "PUESTO_DEL_REPORTE_DIRECTO": dataCarta.get("Puesto reporte", "") or "",
        "TIPO_CONTRATO": " ".join(filter(None, [
            str(dataCarta.get("Tipo contrato", "")).strip(),
            str(dataCarta.get("Tipo contrato custom", "")).strip()
        ])),
        "FECHA_ESTIMADA_INCORPORACION": str(dataCarta.get("Fecha incorporación", "") or ""),
        "CONDICIONES": dataCarta.get("Condiciones", "") or "",
        "RETRIBUCION": dataCarta.get("Retribución fija", "") or "",
        "PORCENTAJE": texto_retribucion_variable or "",
        "RELOCATION_TEXTO": texto_relocation or "Recolocación: No Aplica",
        "beneficios": beneficios_lista,
        "IMAGEN": None,
    }

    plantilla_path = os.path.join(base_path, "files", nombreCarta)
    doc = DocxTemplate(plantilla_path)

    # Si teníamos una ruta de imagen, ahora sí podemos crear InlineImage con esta instancia `doc`
    if not logo_inline and logo_path:
        abs_logo_path = logo_path if os.path.isabs(logo_path) else os.path.join(base_path, logo_path)
        if os.path.exists(abs_logo_path):
            logo_inline = InlineImage(doc, abs_logo_path, width=Cm(14))

    # Si implementaste el uploader, acá podrías recibir un `tmp_path` y hacer:
    # if 'tmp_path_logo' in st.session_state:
    #     logo_inline = InlineImage(doc, st.session_state['tmp_path_logo'], width=Cm(4))

    if logo_inline:
        context["IMAGEN"] = logo_inline

    doc.render(context)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
