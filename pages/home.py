import streamlit as st
from page_utils import apply_page_config  # si ya tenés esto definido


apply_page_config()

st.markdown("<h1 style='text-align: center;'>👋 Bienvenido/a a la Plataforma de Onboarding</h1>", unsafe_allow_html=True)
st.write("Seleccioná una opción para comenzar:")

# Centrar botones con columnas
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🆕 Nuevo Onboarding", use_container_width=True):
        st.switch_page("pages/onboarding.py")  # Si usás múltiples archivos .py
        # o: st.session_state["current_page"] = "nuevo_onboarding"; st.experimental_rerun()

with col2:
    if st.button("🔄 Cambiar estado Onboarding", use_container_width=True):
        st.switch_page("pages/inprogress.py")

with col3:
    if st.button("📄 Generar carta oferta", use_container_width=True):
        st.switch_page("pages/inprogress.py")
