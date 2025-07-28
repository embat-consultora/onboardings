import streamlit as st
st.set_page_config(
    page_title="Formaciones Demo",
    page_icon="favicon.ico",
    layout="centered", 
    initial_sidebar_state="collapsed"
)
username="Email"
password="Contraseña"
forgotPassword="Olvidé mi contraseña"
loginButton="Iniciar Sesión"
logoutButton="Desloguearse"
errorRedirection="Sesion expirada. Redirigiendo a login..."
IncorrectPassword="Email o contraseña incorrectos. Intente nuevamente"
logoutMessage="Deslogueo exitoso"
loginMessage="Sesión iniciada exitosamente"
loginDescription="Por favor, para comenzar inicie sesión"

from time import sleep
import json
with open("cred.json") as f:
    credentials = json.load(f)
left_co, cent_co,last_co = st.columns([1,2,1])
with cent_co:
     st.image("./onboarding.png")

st.subheader("Bienvenido")
user_dict = {user['username']: user for user in credentials['users']}

username = st.text_input("Email",placeholder="Ingrese email")
password = st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña")

st.markdown(
    f'<div style="text-align: right;"><a href="mailto:support@embatconsultora.com">{forgotPassword}</a></div>',
    unsafe_allow_html=True
)

if st.button(loginButton, type="primary"):
    if username in user_dict:
        main_user = user_dict[username]
        if main_user['password'] == password:
            # Set session variables for the main user
            st.session_state.logged_in = True
            st.session_state.username = main_user['username'].upper()
            st.session_state.role = main_user['role']
            st.success("Inicio de sesión exitoso!")
            sleep(0.5)
            st.switch_page("pages/home.py")
        else:
            st.error(IncorrectPassword)
    else:
        st.error(IncorrectPassword)