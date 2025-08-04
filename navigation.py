import streamlit as st
from time import sleep
def get_current_page_name():
    return st.session_state.get("current_page", "")

def logout():
    st.session_state.logged_in = False
    st.info("User successfully logged out")
    sleep(0.5)
    st.switch_page("streamlit_app.py")


def make_sidebar_admin():
    with st.sidebar:
        st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            width: 200px;  /* Adjust the width to your preference */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        st.title("Menu")
        st.write("")
        st.write("")
        if st.session_state.get("logged_in", False):
            if st.session_state.get("tipo") == "Hotel":
                st.page_link("pages/home.py", label="Home")
                st.page_link("pages/cartaOfertaHotel.py", label="Crear Carta Oferta")
                st.page_link("pages/inprogress.py", label="Información Procesos")
                st.page_link("pages/completed.py", label="Finalizados")
                st.write("")
                st.write("")
                if st.button("Cerrar Sesión"):
                    logout()
            else:
                st.page_link("pages/home.py", label="Home")
                st.page_link("pages/cartaOferta.py", label="Crear Carta Oferta")
                st.page_link("pages/inprogress.py", label="Información Procesos")
                st.page_link("pages/completed.py", label="Finalizados")
                st.write("")
                st.write("")    
                if st.button("Cerrar Sesión"):
                    logout()


        else:
            st.switch_page("streamlit_app.py")