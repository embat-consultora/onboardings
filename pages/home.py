import streamlit as st
from page_utils import apply_page_config

apply_page_config()

st.markdown("<h1 style='text-align: center;'>👋 Bienvenido/a a la Plataforma de Onboarding</h1>", unsafe_allow_html=True)
st.write("Seleccioná una opción para comenzar:")

# Estilo personalizado para botones más altos
button_style = """
    <style>
    div.stButton > button {
        height: 80px;
        font-size: 22px !important;
        padding: 10px 16px;
        border-radius: 12px;
    }
    </style>
"""

st.markdown(button_style, unsafe_allow_html=True)

# Centrar botones con columnas
col1, col2 = st.columns(2)

with col1:
    if st.button("💼 Corporativo", use_container_width=True):
        st.session_state["tipo"] = "Corporativo"
        st.switch_page("pages/cartaOferta.py")

with col2:
    if st.button("🏫 Hotel", use_container_width=True):
        st.session_state["tipo"] = "Hotel"
        st.switch_page("pages/cartaOfertaHotel.py")
