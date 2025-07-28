
from PIL import Image
import streamlit as st
def apply_page_config():
    st.set_page_config(
        page_title="Formaciones Check - Demo",
        page_icon="🚀",  #
        layout="wide", # Optional: You can set the layout as "centered" or "wide"
        initial_sidebar_state="collapsed"
    )
 