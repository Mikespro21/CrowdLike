import streamlit as st

from core import (
    apply_global_styles,
    set_user_profile,
    grant_xp,
)

# =========================================================
# Auth helpers (Demo now, Google later)
# =========================================================

def _has_google_secrets() -> bool:
    try:
        auth = st.secrets.get("auth", {})
        cid = (auth.get("client_id") or "").strip()
        csec = (auth.get("client_secret") or "").strip()
        return bool(cid) and bool(csec) and "REPLACE_WITH" not in cid and "REPLACE_WITH" not in csec
    except Exception:
        return False


@st.dialog("Sign in to continue", dismissible=False, width="small")
def _demo_login_dialog():
    st.write("Demo sign-in (no Google yet). Pick a username to continue.")
    name = st.text_input("Username", placeholder="Miguel", key="demo_login_name")

    if st.button("Continue", use_container_width=True):
        name = (name or "").strip()
        if not name:
            st.warning("Please enter a name.")
            return

        set_user_profile(name)
        grant_xp(10, "Login", "Welcome bonus")
        st.session_state["_logged_in_demo"] = True
        st.rerun()


@st.dialog("Sign in to continue", dismissible=False, width="small")
def _google_login_dialog():
    st.write("Sign in with Google to continue.")
    st.button("Continue with Google", on_click=st.login, use_container_width=True)
    st.caption("You’ll be redirected to Google and back.")


def require_login_popup():
    # Google mode (future)
    if _has_google_secrets():
        if st.user.is_logged_in:
            if not st.session_state.get("_synced_streamlit_user", False):
                name = getattr(st.user, "name", None) or "Member"
                email = getattr(st.user, "email", None)
                set_user_profile(name, email=email)
                st.session_state["_synced_streamlit_user"] = True
            return

        _google_login_dialog()
        st.stop()

    # Demo mode (now)
    if st.session_state.get("_logged_in_demo"):
        return

    _demo_login_dialog()
    st.stop()


# =========================================================
# Main app entry
# =========================================================

def main():
    # Your existing app logic lives here
    st.write("App loaded successfully 🎉")


def run():
    st.set_page_config(
        page_title="Qubic Behavioral Feedback Engine",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_global_styles()
    require_login_popup()  # 👈 popup appears immediately
    main()
