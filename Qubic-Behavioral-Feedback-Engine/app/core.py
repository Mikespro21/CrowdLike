import streamlit as st
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta


# =========================
# Page registry
# =========================

@dataclass
class Page:
    id: str
    label: str
    section: str
    template: str
    meta: Dict[str, str] = None


PAGES: List[Page] = []


def reset_pages() -> None:
    """Clear the page registry (useful on rerun)."""
    PAGES.clear()


def add_page(id: str, label: str, section: str, template: str, meta: Dict[str, str] = None) -> None:
    PAGES.append(Page(id=id, label=label, section=section, template=template, meta=meta or {}))


def get_page_by_id(page_id: str) -> Optional[Page]:
    return next((p for p in PAGES if p.id == page_id), None)


def navigate_to(page_id: str) -> None:
    """Schedule navigation to a page on the next rerun."""
    st.session_state["pending_nav_page_id"] = page_id
    try:
        st.experimental_rerun()
    except Exception:
        pass


# =========================
# Session user state
# =========================

DEFAULT_USER_STATE = {
    "username": "Login",
    "email": None,

    "xp": 0,
    "coins": 0,
    "gems": 0,

    "tests_taken": 0,
    "test_history": [],
    "xp_events": [],
    "days_active": [],

    "daily_tasks_done": {},

    "token_balance": 0.0,
    "token_trades": [],

    "qubic_identity": "",
    "qubic_tick_history": [],
    "qubic_price_history": [],

    "ai_chat_history": [],
}


def init_user_state() -> None:
    if "user_state" not in st.session_state:
        st.session_state.user_state = dict(DEFAULT_USER_STATE)


def get_user_state() -> Dict:
    init_user_state()
    return st.session_state.user_state


def record_activity_day() -> None:
    """Mark that the user was active today (for streak computation)."""
    state = get_user_state()
    today_str = date.today().isoformat()
    if today_str not in state["days_active"]:
        state["days_active"].append(today_str)
        state["days_active"].sort()


# =========================
# XP / levels / streaks
# =========================

def level_from_xp(xp: int) -> int:
    """Very simple level curve: 1000 XP per level."""
    return xp // 1000 + 1


def compute_streak(days_active: List[str]) -> int:
    """Current streak based on consecutive days ending today."""
    if not days_active:
        return 0

    active = {date.fromisoformat(d) for d in days_active}
    streak = 0
    cursor = date.today()
    while cursor in active:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def compute_best_streak(days_active: List[str]) -> int:
    """Longest streak of consecutive active days."""
    if not days_active:
        return 0

    dates_list = sorted(date.fromisoformat(d) for d in days_active)
    best = 1
    current = 1

    for i in range(1, len(dates_list)):
        if dates_list[i] == dates_list[i - 1] + timedelta(days=1):
            current += 1
            best = max(best, current)
        else:
            current = 1

    return best


def grant_xp(amount: int, source: str, description: str) -> None:
    """Add XP, derive coins, and log an XP event."""
    if amount <= 0:
        return

    state = get_user_state()
    state["xp"] += int(amount)
    state["coins"] += int(amount) // 10  # 1 coin per 10 XP

    state["xp_events"].append(
        {
            "ts": datetime.utcnow().isoformat(timespec="seconds"),
            "source": source,
            "amount": int(amount),
            "description": description,
        }
    )
    record_activity_day()


def record_test_attempt(test_id: str, name: str, subject: str, correct: int, total: int, time_sec: int) -> None:
    """Store a test/scenario attempt and award XP based on percentage (up to 200 XP)."""
    state = get_user_state()
    total = max(int(total), 1)
    correct = max(0, min(int(correct), total))

    percent = round((correct / total) * 100.0, 1)
    xp_gain = int(percent * 2)  # up to 200 XP

    grant_xp(xp_gain, "Test", f"{name} ({subject})")

    state["test_history"].append(
        {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "test_id": test_id,
            "name": name,
            "subject": subject,
            "correct": correct,
            "total": total,
            "percent": percent,
            "time_sec": int(time_sec),
            "xp_gained": xp_gain,
        }
    )
    state["tests_taken"] += 1
    record_activity_day()


def set_current_scenario(page_id: str, name: str, subject: str) -> None:
    """Remember the active scenario/test metadata for simulation."""
    st.session_state.current_test_id = page_id
    st.session_state.current_test_name = name
    st.session_state.current_test_subject = subject
    record_activity_day()


# =========================
# Token trading log
# =========================

def log_token_trade(action: str, amount: float, price: float, coin_delta: int, token_delta: float) -> None:
    state = get_user_state()
    state["token_trades"].append(
        {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "action": action,
            "amount": round(float(amount), 2),
            "price": round(float(price), 2),
            "coin_delta": int(coin_delta),
            "token_delta": round(float(token_delta), 2),
        }
    )


# =========================
# Profile + AI chat helpers
# =========================

def set_user_profile(username: str, email: str = None) -> None:
    state = get_user_state()
    if username:
        state["username"] = username
    if email:
        state["email"] = email
    record_activity_day()


def ensure_chat_history() -> List[Dict[str, str]]:
    state = get_user_state()
    if not isinstance(state.get("ai_chat_history"), list):
        state["ai_chat_history"] = []
    return state["ai_chat_history"]


# =========================
# Analytics helpers
# =========================

def get_last_test_attempt() -> Optional[Dict]:
    state = get_user_state()
    return state["test_history"][-1] if state["test_history"] else None


def get_last_attempt_for_test(test_id: str) -> Optional[Dict]:
    state = get_user_state()
    for attempt in reversed(state["test_history"]):
        if attempt["test_id"] == test_id:
            return attempt
    return None


def get_xp_by_day() -> Dict[str, int]:
    """Return dict { 'YYYY-MM-DD': total_xp } based on xp_events."""
    state = get_user_state()
    by_day: Dict[str, int] = {}
    for e in state["xp_events"]:
        ts = e.get("ts", "")
        day = ts.split("T")[0] if "T" in ts else ts[:10]
        by_day[day] = by_day.get(day, 0) + int(e.get("amount", 0))
    return by_day


def get_subject_xp_breakdown() -> Dict[str, Dict[str, int]]:
    """Use 'subject' in test_history as behavior channels for now."""
    state = get_user_state()
    breakdown: Dict[str, Dict[str, int]] = {}
    for a in state["test_history"]:
        subj = a.get("subject", "General behavior")
        breakdown.setdefault(subj, {"xp": 0, "tests": 0})
        breakdown[subj]["xp"] += int(a.get("xp_gained", 0))
        breakdown[subj]["tests"] += 1
    return breakdown


def ensure_daily_task_state() -> Dict[str, List[str]]:
    state = get_user_state()
    if not isinstance(state.get("daily_tasks_done"), dict):
        state["daily_tasks_done"] = {}
    return state["daily_tasks_done"]


def render_demo_disclaimer(note: str = None) -> None:
    message = note or (
        "All scores, XP, coins, and missions shown here are generated for this session only "
        "and reset on refresh. Connect a backend to persist real activity."
    )
    st.markdown(f"*{message}*")


# =========================
# Achievements
# =========================

def compute_achievements_catalog(state: Dict):
    xp = state["xp"]
    tests = state["tests_taken"]
    days = state["days_active"]

    streak_best = compute_best_streak(days)
    xp_by_day = get_xp_by_day()

    achievements = []

    def _add(id_, name, desc, unlocked, progress):
        achievements.append(
            {"id": id_, "name": name, "description": desc, "unlocked": unlocked, "progress": progress}
        )

    _add("xp_1000", "First 1,000 Behavior XP", "Reach 1,000 XP from simulated behavior runs.", xp >= 1000, f"{xp}/1000 XP")
    _add("xp_5000", "Serious Behavior Grinder", "Reach 5,000 XP in this session.", xp >= 5000, f"{xp}/5000 XP")

    _add("tests_3", "Tried 3 Scenarios", "Record results for at least 3 scenarios.", tests >= 3, f"{tests}/3 scenarios")
    _add("tests_10", "Scenario Explorer", "Record results for at least 10 scenarios.", tests >= 10, f"{tests}/10 scenarios")

    _add("streak_3", "3-Day Discipline Streak", "Be active on 3 consecutive days.", streak_best >= 3, f"Best streak: {streak_best}/3 days")
    _add("streak_7", "7-Day Commitment", "Be active on 7 consecutive days.", streak_best >= 7, f"Best streak: {streak_best}/7 days")

    # Weekend pair achievement
    active_dates = [date.fromisoformat(d) for d in days]
    active_set = set(active_dates)
    weekend_unlocked = any(d.weekday() == 5 and (d + timedelta(days=1)) in active_set for d in active_dates)
    _add("weekend_warrior", "Weekend Warrior", "Be active on both Saturday and Sunday (streak marker).",
         weekend_unlocked, "Seen Sat+Sun active day pair" if weekend_unlocked else "No Sat+Sun pair yet")

    # Momentum builder: active 5/7 days
    today = date.today()
    active_days_last7 = 0
    for offset in range(7):
        d_str = (today - timedelta(days=offset)).isoformat()
        if xp_by_day.get(d_str, 0) > 0 or d_str in days:
            active_days_last7 += 1
    _add("momentum_builder", "Momentum Builder", "Gain XP on 5 out of the last 7 days.", active_days_last7 >= 5,
         f"{active_days_last7}/5 active days in last 7")

    return achievements, streak_best


# =========================
# Global UI styles (FIXED)
# =========================

import streamlit as st

def apply_global_styles() -> None:
    """
    Clean white 'game HUD' theme.
    CSS only: do NOT inject any fake HTML login button here.
    """
    st.markdown(
        """
<style>
@import url("https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600;700&display=swap");

:root{
  --bg: #F6F8FC;
  --bg2:#FFFFFF;
  --text:#0F172A;
  --muted: rgba(15,23,42,0.62);

  --accent:#2563EB;   /* blue */
  --accent2:#7C3AED;  /* purple */
  --good:#16A34A;
  --warn:#F59E0B;

  --border: rgba(15,23,42,0.12);
  --shadow: 0 10px 30px rgba(15,23,42,0.10);
  --shadow2: 0 6px 16px rgba(15,23,42,0.08);

  --hudH: 104px; /* reserve space for HUD */
}

html, body, .stApp{
  background:
    radial-gradient(900px 500px at 15% 0%, rgba(37,99,235,0.08), transparent 55%),
    radial-gradient(900px 500px at 85% 0%, rgba(124,58,237,0.08), transparent 55%),
    linear-gradient(180deg, var(--bg), #EEF2FF);
  color: var(--text) !important;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
}

/* Push content below HUD */
.block-container{
  padding-top: calc(var(--hudH) + 10px) !important;
}

/* Sidebar: clean menu */
section[data-testid="stSidebar"]{
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(10px);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] *{
  color: var(--text) !important;
}
section[data-testid="stSidebar"] .stSelectbox label{
  color: var(--muted) !important;
  font-family: "Space Mono", monospace;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* Main container */
.main-container{
  max-width: 1120px;
  width: 92vw;
  margin: 18px auto 64px auto;
}

/* Headings: keep game feel but clean */
h1,h2,h3,h4,h5,h6{
  color: var(--text) !important;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* Cards/panels */
.card, .card-hero{
  background: rgba(255,255,255,0.86);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow2);
}
.card-hero{
  border: 1px solid rgba(37,99,235,0.22);
  box-shadow: var(--shadow);
}

/* Small label chip */
.chip, .hud-chip{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(37,99,235,0.20);
  background: rgba(37,99,235,0.08);
  color: rgba(15,23,42,0.85);
  font-family: "Space Mono", monospace;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Buttons: clean, game-like */
.stButton>button, button{
  border-radius: 14px !important;
  border: 1px solid rgba(15,23,42,0.16) !important;
  background: rgba(255,255,255,0.95) !important;
  color: var(--text) !important;
  font-weight: 600 !important;
  box-shadow: 0 6px 18px rgba(15,23,42,0.08);
}
.stButton>button:hover, button:hover{
  border-color: rgba(37,99,235,0.28) !important;
  background: rgba(37,99,235,0.06) !important;
}

/* HUD */
.hud{
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 999999;
  backdrop-filter: blur(12px);
  background: rgba(255,255,255,0.78);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow);
  padding: 10px 14px 12px 14px;
}
.hud-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 14px;
}
.hud-title{
  display:flex;
  flex-direction:column;
  gap: 4px;
  min-width: 240px;
}
.hud-logo{
  font-family: "Press Start 2P", monospace;
  font-size: 13px;
  letter-spacing: 0.08em;
}
.hud-sub{
  font-family: "Space Mono", monospace;
  font-size: 11px;
  color: var(--muted);
}
.hud-center{
  flex:1;
  display:flex;
  flex-direction:column;
  gap: 8px;
  align-items:center;
}
.hud-xp{
  width: min(520px, 100%);
}
.hud-xp-label{
  display:flex;
  justify-content:space-between;
  font-family:"Space Mono", monospace;
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}
.hud-xp-bar{
  height: 12px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(15,23,42,0.05);
  overflow:hidden;
}
.hud-xp-fill{
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, rgba(37,99,235,0.92), rgba(124,58,237,0.92));
}

.hud-stats{
  display:flex;
  gap: 10px;
  align-items:center;
  flex-wrap: wrap;
  justify-content:flex-end;
}
.hud-stat{
  display:flex;
  flex-direction:column;
  gap: 2px;
  padding: 8px 10px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.92);
  min-width: 92px;
}
.hud-k{
  font-family: "Space Mono", monospace;
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.hud-v{
  font-family: Inter, system-ui, sans-serif;
  font-size: 14px;
  font-weight: 700;
}

/* HUD bottom nav row */
.hud-bottom{
  margin-top: 10px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
}
.hud-bottom .stButton>button{
  padding: 10px 10px !important;
  border-radius: 14px !important;
  width: 100% !important;
}

/* Mobile */
@media (max-width: 900px){
  :root{ --hudH: 150px; }
  .hud-top{ flex-wrap: wrap; justify-content:center; }
  .hud-title{ min-width:auto; align-items:center; }
  .hud-stats{ justify-content:center; width: 100%; }
}
</style>
        """,
        unsafe_allow_html=True,
    )
