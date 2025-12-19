import streamlit as st
from core import apply_global_styles, init_user_state

def run():
    st.set_page_config(page_title="Simulator", layout="wide", initial_sidebar_state="expanded")
    apply_global_styles()
    init_user_state()
    st.markdown("### Simulator mode")
    st.info("Simulation mode placeholder. Build flows here.")

if __name__ == "__main__":
    run()