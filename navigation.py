import streamlit as st
from time import sleep
def get_current_page_name():
    return st.session_state.get("current_page", "")

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
            st.page_link("pages/home.py", label="Home")
            st.page_link("pages/onboarding.py", label="Nuevo Onboarding")
            st.page_link("pages/inprogress.py", label="Onboardings")
            st.page_link("pages/completed.py", label="Finalizados")
            st.write("")
            st.write("")

            if st.button("Cerrar Sesión"):
                logout()

        elif get_current_page_name() != "streamlit_app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("streamlit_app.py")

def logout():
    st.session_state.logged_in = False
    st.info("User successfully logged out")
    sleep(0.5)
    st.switch_page("streamlit_app.py")

