import streamlit as st
from core import apply_global_styles, init_user_state

def run():
    st.set_page_config(page_title="Arc Mode", layout="wide", initial_sidebar_state="expanded")
    apply_global_styles()
    init_user_state()
    st.markdown("### Arc mode")
    st.info("Arc mode coming soon. Shared state is ready via core.py.")

if __name__ == "__main__":
    run()