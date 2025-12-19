import streamlit as st

from core import (
    apply_global_styles,
    init_user_state,
    reset_pages,
    PAGES,
    get_page_by_id,
    get_user_state,
    DEFAULT_USER_STATE,
    set_user_profile,
    grant_xp,
)

from qubic_registry import register_pages
from qubic_templates import TEMPLATE_DISPATCH, TEMPLATE_OVERRIDES, tpl_simple_info

from storage import (
    load_user_state,
    save_user_state,
    merge_state,
    has_password,
    verify_password,
    set_password_fields,
)

# =========================
# Auth + Remember Me + Password (Demo)
# =========================

def _has_google_secrets() -> bool:
    """True only if secrets exist and are NOT placeholders."""
    try:
        auth = st.secrets.get("auth", {})
        cid = (auth.get("client_id") or "").strip()
        csec = (auth.get("client_secret") or "").strip()
        if not cid or not csec:
            return False
        if "REPLACE_WITH" in cid or "REPLACE_WITH" in csec:
            return False
        return True
    except Exception:
        return False


def _current_user_id() -> str:
    """
    Stable id for persistence:
    - Google email if logged in
    - else demo username/email in user_state
    """
    try:
        if _has_google_secrets() and getattr(st, "user", None) and st.user.is_logged_in:
            email = getattr(st.user, "email", None)
            if email:
                return str(email).strip().lower()
    except Exception:
        pass

    state = get_user_state()
    u = (state.get("email") or state.get("username") or "").strip()
    return u.lower() if u else "anonymous"


def _load_persisted_state_once(user_id: str) -> None:
    """Load saved state into session once per user per session."""
    if not user_id or user_id == "anonymous":
        return

    if st.session_state.get("_persist_loaded_for") == user_id:
        return

    loaded = load_user_state(user_id)
    if loaded:
        st.session_state.user_state = merge_state(DEFAULT_USER_STATE, loaded)

    st.session_state["_persist_loaded_for"] = user_id


def _persist_state_now() -> None:
    """Persist current user_state to disk (local JSON) if user_id is known."""
    user_id = _current_user_id()
    if not user_id or user_id == "anonymous":
        return
    save_user_state(user_id, get_user_state())


@st.dialog("Sign in", dismissible=False, width="small")
def login_dialog():
    """
    ONE dialog only (no nested dialogs).
    - If Google secrets exist (and not forced demo), shows Google tab + Demo tab
    - Otherwise shows Demo tab only
    """
    google_ready = _has_google_secrets() and not st.session_state.get("_force_demo_mode", False)

    tabs = (["Google"] if google_ready else []) + ["Demo"]
    choice = st.radio("Mode", tabs, horizontal=True, label_visibility="collapsed")

    # ----------------------
    # GOOGLE LOGIN
    # ----------------------
    if choice == "Google":
        st.write("Sign in with Google to continue.")
        st.button(
            "Continue with Google",
            on_click=st.login,
            use_container_width=True,
            key="google_login_btn",
        )
        st.caption("You’ll be redirected to Google and back.")

        # Let you proceed even if Google isn’t configured yet / you just want demo
        if st.button("Use demo instead", use_container_width=True, key="google_to_demo"):
            st.session_state["_force_demo_mode"] = True
            st.rerun()
        return

    # ----------------------
    # DEMO LOGIN + PASSWORD
    # ----------------------
    st.write("Demo sign-in (works without Google).")
    name = st.text_input("Username", placeholder="Miguel", key="demo_name").strip()

    if not name:
        st.caption("Use the same username to load your saved progress on this computer.")
        return

    user_id = name.lower()
    saved = load_user_state(user_id) or {}
    needs_pw = has_password(saved)

    # Existing demo account with password
    if needs_pw:
        pw = st.text_input("Password", type="password", key="demo_pw")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", use_container_width=True, key="demo_login_btn"):
                if not pw:
                    st.warning("Enter your password.")
                    return
                if not verify_password(saved, pw):
                    st.error("Wrong password.")
                    return

                set_user_profile(name)
                st.session_state.user_state = merge_state(DEFAULT_USER_STATE, saved)
                st.session_state["_logged_in_demo"] = True
                st.session_state["_persist_loaded_for"] = user_id
                st.rerun()

        with col_b:
            if st.button("Reset account", use_container_width=True, key="demo_reset_btn"):
                st.session_state["_reset_user_id"] = user_id

        if st.session_state.get("_reset_user_id") == user_id:
            st.warning("Reset deletes saved progress for this username on this computer.")
            if st.button("Confirm reset", use_container_width=True, key="demo_reset_confirm"):
                fresh = dict(DEFAULT_USER_STATE)
                fresh["username"] = name
                save_user_state(user_id, fresh)
                st.session_state.pop("_reset_user_id", None)
                st.success("Reset done. Now you can set a new password.")
                st.rerun()

        return

    # No password yet (new or old-without-password)
    st.caption("Optional: set a password for this demo account on this computer.")
    pw1 = st.text_input("Create password (optional)", type="password", key="demo_pw1")
    pw2 = st.text_input("Confirm password", type="password", key="demo_pw2")

    if st.button("Continue", use_container_width=True, key="demo_continue_btn"):
        set_user_profile(name)

        # Merge existing save (if any) with defaults
        merged = merge_state(DEFAULT_USER_STATE, saved) if saved else dict(DEFAULT_USER_STATE)
        merged["username"] = name

        # If they want a password, validate + hash it
        if pw1 or pw2:
            if pw1 != pw2:
                st.error("Passwords do not match.")
                return
            if len(pw1) < 4:
                st.error("Password too short (min 4).")
                return
            merged = set_password_fields(merged, pw1)

        st.session_state.user_state = merged
        st.session_state["_logged_in_demo"] = True
        st.session_state["_persist_loaded_for"] = user_id

        # Save immediately so “remember me” works right away
        save_user_state(user_id, merged)

        # Welcome bonus only if truly new
        if not saved:
            grant_xp(10, "Login", "Welcome bonus")

        st.rerun()


def require_login_popup() -> None:
    """
    - If Google secrets exist and not forced demo:
        - if logged in -> sync profile + load persisted
        - else -> show login dialog (Google tab available)
    - Otherwise:
        - demo login (with optional password) via same dialog
    """
    google_ready = _has_google_secrets() and not st.session_state.get("_force_demo_mode", False)

    if google_ready:
        if st.user.is_logged_in:
            name = getattr(st.user, "name", None) or "Member"
            email = getattr(st.user, "email", None)
            set_user_profile(name, email=email)
            _load_persisted_state_once(_current_user_id())
            return

        login_dialog()
        st.stop()

    # Demo path
    if st.session_state.get("_logged_in_demo"):
        _load_persisted_state_once(_current_user_id())
        return

    login_dialog()
    st.stop()


# =========================
# Pages / Routing
# =========================

def _prepare_pages():
    reset_pages()
    register_pages()
    for page in PAGES:
        if page.id in TEMPLATE_OVERRIDES:
            page.template = TEMPLATE_OVERRIDES[page.id]


def _render(active_page):
    renderer = TEMPLATE_DISPATCH.get(active_page.template)
    if renderer is None:
        tpl_simple_info(active_page, title=active_page.label, body="Template not yet implemented.")
    else:
        renderer(active_page)


def main():
    _prepare_pages()

    sections_order = [
        "Entry & Auth",
        "Onboarding & Home",
        "Account & Profile",
        "XP & Stats",
        "Behavior Scenarios",
        "Shop & Currency",
        "Social & Competition",
        "Settings & System",
        "Admin & Dev",
        "Test Library",
        "Algebra 1",
        "Physics & Science",
        "Practice & Training",
    ]
    sections = [s for s in sections_order if any(p.section == s for p in PAGES)]

    # Default landing: Hub (if exists)
    hub_page = get_page_by_id("hub")
    if hub_page:
        st.session_state.setdefault("nav_section", hub_page.section)
        st.session_state.setdefault("nav_page_label", hub_page.label)

    # Handle pending navigation (set by navigate_to)
    pending_page_id = st.session_state.pop("pending_nav_page_id", None)
    if pending_page_id:
        page = get_page_by_id(pending_page_id)
        if page:
            st.session_state["nav_section"] = page.section
            st.session_state["nav_page_label"] = page.label

    # Initialize sidebar selections
    if "nav_section" not in st.session_state and sections:
        st.session_state["nav_section"] = sections[0]

    if "nav_page_label" not in st.session_state:
        first_section_pages = [p for p in PAGES if p.section == st.session_state.get("nav_section")]
        st.session_state["nav_page_label"] = first_section_pages[0].label if first_section_pages else ""

    with st.sidebar:
        st.markdown("### Pages")
        selected_section = st.selectbox("Section", sections, key="nav_section")
        section_pages = [p for p in PAGES if p.section == selected_section]

        labels = [p.label for p in section_pages]
        if st.session_state.get("nav_page_label") not in labels and labels:
            st.session_state["nav_page_label"] = labels[0]

        selected_label = st.selectbox("Page", labels, key="nav_page_label")
        active_page = next(p for p in section_pages if p.label == selected_label)

    _render(active_page)


def run():
    st.set_page_config(
        page_title="Qubic Behavioral Feedback Engine",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_global_styles()

    # Ensure state exists before auth
    init_user_state()

    # Auth gate (Google if available; else demo)
    require_login_popup()

    # Render app
    main()

    # Persist at end of run
    _persist_state_now()


if __name__ == "__main__":
    run()
