import streamlit as st
import io
import os
from docxtpl import DocxTemplate
import json
def generarCarta(dataCarta):
    if dataCarta:
        buffer = generar_docx_con_datos(dataCarta)
        nombre = dataCarta.get("Nombre", "") +"_"+ dataCarta.get("Apellido", "")
        file_name = f"carta_oferta_{nombre}"
        st.download_button(
            label="Descargar Carta Oferta",
            data=buffer,
            file_name=f"{file_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def generar_docx_con_datos(dataCarta):
    base_path = os.path.dirname(os.path.abspath(__file__))
    nombreCarta = f"carta_template.docx"
    plantilla_path = os.path.join(base_path,"files", nombreCarta)
    doc = DocxTemplate(plantilla_path)
    beneficios_dict = json.loads(dataCarta.get("Beneficios", "{}"))
    beneficios_lista = [k for k, v in beneficios_dict.items() if v]
    context = {
        "NOMBRE": dataCarta.get("Nombre", ""),
        "APELLIDO": dataCarta.get("Apellido", ""),
        "POSICION": dataCarta.get("Posición", ""),
        "DEPARTAMENTO": dataCarta.get("Departamento", ""),
        "FECHA_FORM": dataCarta.get("Fecha creación", ""),
        "PUESTO_DEL_REPORTE_DIRECTO": dataCarta.get("Puesto reporte", ""),
        "TIPO_CONTRATO": dataCarta.get("Tipo contrato", ""),
        "FECHA_ESTIMADA_INCORPORACION": str(dataCarta.get("Fecha incorporación", "")),
        "CONDICIONES": dataCarta.get("Condiciones", ""),
        "RETRIBUCION": dataCarta.get("Retribución fija", ""),
        "PORCENTAJE": dataCarta.get("Retribución variable", ""),
        "beneficios": beneficios_lista,
    }
   
    doc.render(context)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

