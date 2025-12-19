import random
import streamlit as st
from datetime import date, timedelta
from typing import Dict
import requests
from datetime import datetime

from core import (
    Page,
    get_user_state,
    set_user_profile,
    grant_xp,
    set_current_scenario,
    record_test_attempt,
    record_activity_day,  # ✅ FIX: was used but not imported in your file
    compute_streak,
    compute_best_streak,
    get_last_test_attempt,
    get_last_attempt_for_test,
    get_xp_by_day,
    get_subject_xp_breakdown,
    ensure_daily_task_state,
    render_demo_disclaimer,
    compute_achievements_catalog,
    navigate_to,
    level_from_xp,
    log_token_trade,
    ensure_chat_history,
)

from qubic_rpc import (
    get_qubic_rpc_endpoint,
    get_qubic_status_cached,
    get_qubic_tick_cached,
    get_qubic_balance_cached,
    build_qubic_status_summary,
    build_qubic_balance_summary,
    format_qubic_value,
    update_qubic_market_history,
    pick_qubic_tick,
    pick_qubic_price,
)
COINGECKO_API = "https://api.coingecko.com/api/v3"

def _cg_get(path: str, params: dict):
    url = f"{COINGECKO_API}{path}"
    headers = {"User-Agent": "Crowdlike-Streamlit/1.0"}  # nice to have
    r = requests.get(url, params=params, headers=headers, timeout=12)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60, show_spinner=False)
def cg_simple_price(ids, vs="usd"):
    # Uses /simple/price :contentReference[oaicite:5]{index=5}
    if isinstance(ids, (list, tuple)):
        ids = ",".join(ids)
    return _cg_get(
        "/simple/price",
        {
            "ids": ids,
            "vs_currencies": vs,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
            "include_last_updated_at": "true",
        },
    )

@st.cache_data(ttl=90, show_spinner=False)
def cg_markets(vs="usd", per_page=50, page=1):
    # Uses /coins/markets :contentReference[oaicite:6]{index=6}
    return _cg_get(
        "/coins/markets",
        {
            "vs_currency": vs,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d",
        },
    )

@st.cache_data(ttl=180, show_spinner=False)
def cg_market_chart(coin_id: str, vs="usd", days=7):
    # Uses /coins/{id}/market_chart :contentReference[oaicite:7]{index=7}
    return _cg_get(
        f"/coins/{coin_id}/market_chart",
        {"vs_currency": vs, "days": days},
    )


# ============================================================
# Layout helpers
# ============================================================

def _container_start():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

def _container_end():
    st.markdown("</div>", unsafe_allow_html=True)


import streamlit as st
from core import get_user_state, navigate_to, compute_streak, level_from_xp

def _xp_progress(xp: int):
    """Returns (level, in_level_xp, needed_xp, pct_0_1)."""
    xp = int(xp)
    level = level_from_xp(xp)
    base = (level - 1) * 1000
    nxt = level * 1000
    in_level = max(0, xp - base)
    needed = max(1, nxt - base)
    pct = min(1.0, max(0.0, in_level / needed))
    return level, in_level, needed, pct

def render_top_bar(active_page_label: str, show_user: bool = True):
    state = get_user_state()

    xp = int(state.get("xp", 0))
    coins = int(state.get("coins", 0))
    gems = int(state.get("gems", 0))
    tokens = float(state.get("token_balance", 0.0))
    streak = compute_streak(state.get("days_active", []))

    level, in_level, needed, pct = _xp_progress(xp)

    username_raw = (state.get("username") or "").strip()
    username = "Login" if username_raw.lower() in ("", "guest", "login") else username_raw

    # Unique key prefix to avoid StreamlitDuplicateElementKey even if HUD renders multiple times
    st.session_state["_hud_render_i"] = st.session_state.get("_hud_render_i", 0) + 1
    rid = st.session_state["_hud_render_i"]
    key_prefix = f"hud:{active_page_label}:{rid}:"

    st.markdown('<div class="hud">', unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="hud-top">
  <div class="hud-title">
    <div class="hud-logo">CROWDLIKE</div>
    <div class="hud-sub">Behavior HUD • session demo</div>
  </div>

  <div class="hud-center">
    <span class="hud-chip">{active_page_label}</span>
    <div class="hud-xp">
      <div class="hud-xp-label">
        <span>LVL {level}</span>
        <span>{in_level}/{needed} XP</span>
      </div>
      <div class="hud-xp-bar">
        <div class="hud-xp-fill" style="width:{pct*100:.1f}%"></div>
      </div>
    </div>
  </div>

  <div class="hud-stats">
    <div class="hud-stat"><span class="hud-k">Coins</span><span class="hud-v">{coins}</span></div>
    <div class="hud-stat"><span class="hud-k">Gems</span><span class="hud-v">{gems}</span></div>
    <div class="hud-stat"><span class="hud-k">Tokens</span><span class="hud-v">{tokens:.2f}</span></div>
    <div class="hud-stat"><span class="hud-k">Streak</span><span class="hud-v">{streak}</span></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hud-bottom">', unsafe_allow_html=True)

    # ✅ Added Market tab here
    nav_items = [
        ("Hub", "hub"),
        ("Home", "home_dashboard"),
        ("Lab", "metrics_lab"),
        ("Market", "market_live"),
        ("Wallet", "wallet_dashboard"),
        ("Network", "qubic_network"),
    ]

    col_nav, col_user = st.columns([6.5, 1.5])

    with col_nav:
        cols = st.columns(len(nav_items))
        for (label, target), c in zip(nav_items, cols):
            c.button(
                label,
                on_click=navigate_to,
                args=(target,),
                use_container_width=True,
                key=f"{key_prefix}tab:{target}",
            )

    with col_user:
        if show_user:
            if st.button(username, key=f"{key_prefix}user", use_container_width=True):
                navigate_to("login" if username == "Login" else "profile_customization")

    st.markdown("</div>", unsafe_allow_html=True)  # hud-bottom
    st.markdown("</div>", unsafe_allow_html=True)  # hud

# ============================================================
# Generic templates
# ============================================================

def tpl_market_live(page: Page):
    render_top_bar(page.label)
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Live Market (Real Prices)")
    st.caption("Data: CoinGecko public API • Updates ~every 60–90s • Info-only (not financial advice).")

    top = st.columns([1.1, 1.1, 1.3, 2.5])
    vs = top[0].selectbox("Currency", ["usd", "eur", "mxn"], index=0, key="cg_vs")
    per_page = top[1].selectbox("Rows", [25, 50, 100], index=1, key="cg_rows")
    days = top[2].selectbox("Chart window", [1, 7, 14, 30, 90, 180, 365], index=1, key="cg_days")

    if top[3].button("Refresh now", use_container_width=True, key="cg_refresh"):
        cg_simple_price.clear()
        cg_markets.clear()
        cg_market_chart.clear()
        st.rerun()

    # --- QUBIC spotlight (real market)
    st.write("---")
    st.markdown("#### Spotlight: QUBIC")
    try:
        q = cg_simple_price(["qubic"], vs=vs).get("qubic", {})
        if q:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Price", q.get(vs, "—"))
            c2.metric("24h %", f"{q.get(f'{vs}_24h_change', 0):.2f}%")
            c3.metric("24h Vol", q.get(f"{vs}_24h_vol", "—"))
            c4.metric("Mkt Cap", q.get(f"{vs}_market_cap", "—"))
        else:
            st.info("QUBIC not returned by CoinGecko right now (API may be rate-limited).")
    except Exception as e:
        st.info("Live market temporarily unavailable (CoinGecko request failed).")
        st.caption(f"Details: {e}")

    # --- Top market table
    st.write("---")
    st.markdown("#### Top Coins (by market cap)")
    data = []
    try:
        data = cg_markets(vs=vs, per_page=int(per_page), page=1) or []
    except Exception as e:
        st.info("Couldn’t load the market list right now.")
        st.caption(f"Details: {e}")

    if data:
        # Build a clean table (list of dicts so st.dataframe is happy)
        rows = []
        for item in data:
            rows.append({
                "Name": item.get("name"),
                "Symbol": (item.get("symbol") or "").upper(),
                "Price": item.get("current_price"),
                "24h %": item.get("price_change_percentage_24h_in_currency"),
                "7d %": item.get("price_change_percentage_7d_in_currency"),
                "Market Cap": item.get("market_cap"),
                "24h Volume": item.get("total_volume"),
            })

        st.dataframe(rows, use_container_width=True, hide_index=True)

        movers = st.columns(2)
        gainers = sorted(rows, key=lambda r: (r["24h %"] is None, -(r["24h %"] or 0)))[:8]
        losers  = sorted(rows, key=lambda r: (r["24h %"] is None, (r["24h %"] or 0)))[:8]

        with movers[0]:
            st.markdown("#### Top gainers (24h)")
            st.table([{"Name": r["Name"], "24h %": r["24h %"]} for r in gainers])
        with movers[1]:
            st.markdown("#### Top losers (24h)")
            st.table([{"Name": r["Name"], "24h %": r["24h %"]} for r in losers])

        # --- Coin detail + chart
        st.write("---")
        st.markdown("#### Coin detail")
        coin_options = [(x.get("name"), x.get("id")) for x in data if x.get("id")]
        default_idx = 0
        for i, (_, cid) in enumerate(coin_options):
            if cid == "qubic":
                default_idx = i
                break

        picked_name, picked_id = st.selectbox(
            "Pick a coin",
            coin_options,
            index=default_idx,
            format_func=lambda t: t[0],
            key="cg_coin_pick",
        )

        try:
            ch = cg_market_chart(picked_id, vs=vs, days=int(days))
            prices = ch.get("prices") or []
            if prices:
                series = [p[1] for p in prices]
                st.line_chart({"price": series})
                st.caption(f"{picked_name} • last {days} day(s) • {vs.upper()} • updated {datetime.utcnow().isoformat(timespec='seconds')}Z")
            else:
                st.caption("No chart points returned.")
        except Exception as e:
            st.info("Chart unavailable right now.")
            st.caption(f"Details: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


def tpl_simple_info(page: Page, title: str = None, body: str = None):
    render_top_bar(page.label)
    _container_start()
    st.markdown(f"### {title or page.label}")
    st.write(body or "Static informational page placeholder.")
    _container_end()


def tpl_simple_table(page: Page, title: str = None):
    render_top_bar(page.label)
    _container_start()
    st.markdown(f"### {title or page.label}")
    st.table({"Column A": ["Row 1", "Row 2"], "Column B": ["Value 1", "Value 2"]})
    _container_end()


def tpl_simple_list(page: Page, title: str = None):
    render_top_bar(page.label)
    _container_start()
    st.markdown(f"### {title or page.label}")
    for i in range(1, 6):
        st.write(f"- Item {i}")
    _container_end()


def tpl_settings_form(page: Page, title: str = None):
    render_top_bar(page.label)
    _container_start()
    st.markdown(f"### {title or page.label}")
    st.text_input("Sample text field", value="")
    st.checkbox("Enable sample option")
    st.selectbox("Sample mode", ["Off", "Low", "Medium", "High"])
    if st.button("Save changes"):
        st.success("Settings saved for this session.")
    _container_end()


# ============================================================
# Key product pages
# ============================================================

def tpl_hub(page: Page):
    render_top_bar(page.label)
    _container_start()
    st.markdown("### Qubic Hub")
    st.write("Fast routes to the pages you use the most.")
    cols = st.columns(4)
    cols[0].button("Home", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)
    cols[1].button("Simulation Lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    cols[2].button("Wallet", on_click=navigate_to, args=("wallet_dashboard",), use_container_width=True)
    cols[3].button("Qubic Network", on_click=navigate_to, args=("qubic_network",), use_container_width=True)
    _container_end()


def tpl_login(page: Page):
    # If you want only ONE login button, hide floating button on login page:
    render_top_bar(page.label, show_floating_user=True)
    _container_start()

    st.markdown("### Login")
    st.write("Sign in to personalize XP, coins and test history for this session.")

    st.markdown("#### Quick sign-in (demo)")
    if st.button("Sign in with Google"):
        set_user_profile("Google User", "you@example.com")
        grant_xp(15, "Login", "Google quick sign-in bonus")
        st.success("Signed in with Google (placeholder). XP +15.")
        st.button("Go to dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)

    st.write("---")
    st.markdown("#### Email login (demo)")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        username = (email or "").strip() or "Member"
        state = get_user_state()
        state["username"] = username
        state["email"] = (email or "").strip() or state.get("email") or "you@example.com"
        grant_xp(10, "Login", "Login bonus")
        st.success(f"Logged in as {username}. XP +10 to get you started.")
        st.button("Go to dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)

    st.write("---")
    st.button("Back to landing", on_click=navigate_to, args=("landing_public",), use_container_width=True)
    _container_end()


def tpl_landing(page: Page):
    render_top_bar(page.label)
    _container_start()
    st.markdown("## Understand your on-chain behavior. Shape your future.")
    st.markdown(
        '<div class="card-hero">Design your behavioral loop with XP, streaks, coins, and scenario feedback. Connect data when ready.</div>',
        unsafe_allow_html=True,
    )
    cta1, cta2, cta3 = st.columns(3)
    cta1.button("Start onboarding", on_click=navigate_to, args=("onboard_subjects",), use_container_width=True)
    cta2.button("Open dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)
    cta3.button("See XP & achievements", on_click=navigate_to, args=("achievements_list",), use_container_width=True)
    _container_end()


def tpl_home_dashboard(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    streak = compute_streak(state["days_active"])

    _container_start()
    st.markdown("### Home")
    st.caption(f"User: {state['username']}")

    metrics = st.columns(4)
    metrics[0].metric("XP", state["xp"])
    metrics[1].metric("Coins", state["coins"])
    metrics[2].metric("Tokens", round(state.get("token_balance", 0.0), 2))
    metrics[3].metric("Streak", streak)

    st.write("---")
    quick = st.columns(4)
    quick[0].button("Hub", on_click=navigate_to, args=("hub",), use_container_width=True)
    quick[1].button("Simulation Lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    quick[2].button("Wallet", on_click=navigate_to, args=("wallet_dashboard",), use_container_width=True)
    quick[3].button("Qubic Network", on_click=navigate_to, args=("qubic_network",), use_container_width=True)
    _container_end()


def tpl_qubic_network(page: Page):
    render_top_bar(page.label)
    state = get_user_state()

    _container_start()
    st.markdown("### Qubic Network")

    rpc_endpoint = get_qubic_rpc_endpoint()
    st.caption(f"RPC: {rpc_endpoint}")

    status = get_qubic_status_cached(rpc_endpoint)
    if "error" in status:
        st.info("Live RPC not reachable right now.")
        st.caption(f"Details: {status['error']}")
    else:
        summary = build_qubic_status_summary(status)
        st.table(summary) if summary else st.json(status)
        if status.get("_fetched_at"):
            st.caption(f"Updated: {status['_fetched_at']}")

    identity = (state.get("qubic_identity") or "").strip()
    if identity:
        bal = get_qubic_balance_cached(identity, rpc_endpoint)
        if "error" in bal:
            st.caption(f"Balance lookup failed: {bal['error']}")
        else:
            bal_summary = build_qubic_balance_summary(bal)
            st.table(bal_summary) if bal_summary else st.json(bal)
    else:
        st.caption("Set an identity in Wallet to show balances here.")

    _container_end()


def tpl_metrics_lab(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    streak_current = compute_streak(state["days_active"])

    _container_start()
    st.markdown("### Simulation Lab")
    st.write("Quick simulation to update XP and token balance.")

    metrics = st.columns(4)
    metrics[0].metric("XP", state["xp"])
    metrics[1].metric("Coins", state["coins"])
    metrics[2].metric("Tokens", round(state.get("token_balance", 0.0), 2))
    metrics[3].metric("Streak", streak_current)

    st.write("---")
    scenario = st.selectbox("Mode", ["Calm holder", "Active scalper", "Governance run", "Airdrop sprint"], index=0)
    xp_gain = st.slider("XP to award", min_value=10, max_value=250, value=120, step=5)
    token_delta = st.slider("Token balance change", min_value=-50.0, max_value=80.0, value=5.0, step=1.0)

    note = f"{scenario} pulse: +{xp_gain} XP | token Δ {token_delta}"
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Apply simulation"):
            grant_xp(int(xp_gain), "Simulation", note)
            state["token_balance"] = round(state.get("token_balance", 0.0) + float(token_delta), 2)
            record_activity_day()
            st.success(f"Logged: {note}")
    with c2:
        if st.button("Quick random"):
            xp_rand = random.randint(50, 200)
            token_rand = round(random.uniform(-20, 50), 2)
            grant_xp(int(xp_rand), "Simulation", "Random behavior simulation")
            state["token_balance"] = round(state.get("token_balance", 0.0) + token_rand, 2)
            record_activity_day()
            st.success(f"Random run: +{xp_rand} XP, token Δ {token_rand}.")

    _container_end()


def tpl_wallet_dashboard(page: Page):
    render_top_bar(page.label)
    state = get_user_state()

    _container_start()
    st.markdown("### Wallet")
    st.markdown("#### Connect wallet (read-only)")

    rpc_endpoint = st.text_input(
        "RPC endpoint",
        value=get_qubic_rpc_endpoint(),
        key="wallet_rpc_endpoint",
        help="Public testnet can be flaky. Paste your node URL to improve reliability.",
    )
    identity_input = st.text_input(
        "Identity (address ID)",
        value=state.get("qubic_identity", ""),
        key="wallet_identity_input",
        help="Paste a testnet identity (address) to display balances.",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save connection"):
            st.session_state["qubic_rpc_endpoint"] = (rpc_endpoint or "").strip() or get_qubic_rpc_endpoint()
            state["qubic_identity"] = (identity_input or "").strip()
            st.success("Saved RPC + identity for this session.")
    with c2:
        st.button("Refresh", on_click=record_activity_day)

    live_endpoint = st.session_state.get("qubic_rpc_endpoint", rpc_endpoint)
    status = get_qubic_status_cached(live_endpoint)
    if "error" in status:
        st.info("Live RPC not reachable right now. Try again or set your own node URL above.")
        st.caption(f"Details: {status['error']}")
    else:
        summary = build_qubic_status_summary(status)
        st.table(summary) if summary else st.json(status)

    identity = (state.get("qubic_identity") or "").strip()
    if identity:
        bal = get_qubic_balance_cached(identity, live_endpoint)
        if "error" in bal:
            st.caption(f"Balance lookup failed: {bal['error']}")
        else:
            bal_summary = build_qubic_balance_summary(bal)
            st.table(bal_summary) if bal_summary else st.json(bal)
    else:
        st.caption("Paste an identity to see live balances here.")

    _container_end()


def tpl_token_trading(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    token_balance = float(state.get("token_balance", 0.0))
    coins = int(state["coins"])

    _container_start()
    st.markdown("### Token Trading Desk")
    st.write(f"Coins: {coins} | Token balance: {round(token_balance, 2)}")

    price = st.number_input("Current token price (coins)", min_value=1, max_value=1000, value=50, step=1)
    buy_amount = st.number_input("Amount to buy", min_value=0.0, value=0.0, step=1.0)
    sell_amount = st.number_input("Amount to sell", min_value=0.0, value=0.0, step=1.0)

    col_buy, col_sell = st.columns(2)
    with col_buy:
        if st.button("Buy tokens"):
            cost = buy_amount * price
            if cost <= coins and buy_amount > 0:
                state["coins"] -= int(cost)
                state["token_balance"] = round(token_balance + buy_amount, 2)
                log_token_trade("buy", buy_amount, price, -int(cost), buy_amount)
                record_activity_day()
                st.success(f"Bought {buy_amount} tokens for {int(cost)} coins.")
            else:
                st.warning("Not enough coins or invalid amount.")

    with col_sell:
        if st.button("Sell tokens"):
            proceeds = sell_amount * price
            if sell_amount <= token_balance and sell_amount > 0:
                state["coins"] += int(proceeds)
                state["token_balance"] = round(token_balance - sell_amount, 2)
                log_token_trade("sell", sell_amount, price, int(proceeds), -sell_amount)
                record_activity_day()
                st.success(f"Sold {sell_amount} tokens for {int(proceeds)} coins.")
            else:
                st.warning("Not enough tokens or invalid amount.")

    if state.get("token_trades"):
        st.write("---")
        st.markdown("#### Recent trades")
        recent = list(reversed(state["token_trades"]))[:5]
        st.table({
            "Time": [t["timestamp"] for t in recent],
            "Action": [t["action"] for t in recent],
            "Amount": [t["amount"] for t in recent],
            "Price": [t["price"] for t in recent],
            "Coin Δ": [t["coin_delta"] for t in recent],
            "Token Δ": [t["token_delta"] for t in recent],
        })

    _container_end()


def tpl_achievements_list(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    catalog, best_streak = compute_achievements_catalog(state)

    _container_start()
    st.markdown("### Achievements directory")
    st.caption(f"Best streak so far: {best_streak} day(s).")

    rows = {"ID": [], "Achievement": [], "Status": [], "Progress": []}
    for ach in catalog:
        rows["ID"].append(ach["id"])
        rows["Achievement"].append(ach["name"])
        rows["Status"].append("Unlocked" if ach["unlocked"] else "Locked")
        rows["Progress"].append(ach["progress"])

    st.table(rows)
    render_demo_disclaimer("Achievements are unlocked based on what you do in this session.")
    _container_end()


# ============================================================
# Dispatch tables (keep registry working)
# ============================================================

TEMPLATE_DISPATCH = {
    # Core navigation + UX
    "hub": tpl_hub,
    "landing": tpl_landing,
    "login": tpl_login,

    # Core product pages
    "home_dashboard": tpl_home_dashboard,
    "metrics_lab": tpl_metrics_lab,
    "wallet_dashboard": tpl_wallet_dashboard,
    "token_trading": tpl_token_trading,
    "qubic_network": tpl_qubic_network,

    #Market
    "market_live": tpl_market_live,


    # Achievements
    "achievements_list": tpl_achievements_list,

    # Generic fallback templates used by registry
    "simple_info": tpl_simple_info,
    "simple_table": tpl_simple_table,
    "simple_list": tpl_simple_list,
    "settings_form": tpl_settings_form,
}

TEMPLATE_OVERRIDES = {
    # You can map specific page IDs to a template name if needed.
    # Example: "xp_history": "simple_table"
}
