import requests
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional

QUBIC_PUBLIC_RPC = "https://testnet-rpc.qubicdev.com"


# =========================
# Raw RPC calls
# =========================

def fetch_qubic_status(rpc_endpoint: str = QUBIC_PUBLIC_RPC) -> Dict:
    """Call /v1/status on a Qubic RPC endpoint."""
    try:
        resp = requests.get(f"{rpc_endpoint}/v1/status", timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            return {"error": "Unexpected status payload"}
        return data
    except Exception as e:
        return {"error": str(e)}


def fetch_qubic_tick(rpc_endpoint: str = QUBIC_PUBLIC_RPC) -> Dict:
    """
    Try to read a 'tick' or height-like value from the RPC.

    NOTE: The public testnet RPC commonly does NOT expose /v1/tick,
    so 404 is treated as a friendly error.
    """
    try:
        resp = requests.get(f"{rpc_endpoint}/v1/tick", timeout=8)
        if resp.status_code == 404:
            return {"error": "Tick endpoint /v1/tick not available on this RPC"}
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            return {"error": "Unexpected tick payload"}
        return data
    except Exception as e:
        return {"error": str(e)}


def fetch_qubic_balance(identity: str, rpc_endpoint: str = QUBIC_PUBLIC_RPC) -> Dict:
    """Call /v1/balances/{identity} for a given address ID on Qubic."""
    try:
        identity = (identity or "").strip()
        if not identity:
            return {"error": "No identity provided"}
        resp = requests.get(f"{rpc_endpoint}/v1/balances/{identity}", timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            return {"error": "Unexpected balance payload"}
        return data
    except Exception as e:
        return {"error": str(e)}


# =========================
# Formatting / helpers
# =========================

def attach_fetch_meta(payload: dict) -> dict:
    """Attach a lightweight fetch timestamp to successful RPC payloads."""
    if not isinstance(payload, dict) or "error" in payload:
        return payload
    updated = dict(payload)
    updated["_fetched_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return updated


def format_qubic_value(value) -> str:
    """Format values from RPC in a compact, user-friendly way."""
    if value is None or value == "":
        return "n/a"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.6f}".rstrip("0").rstrip(".")
    return str(value)


def coerce_number(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_qubic_status_summary(status: dict) -> List[Dict[str, str]]:
    """Pick common status fields from a Qubic RPC payload."""
    if not isinstance(status, dict):
        return []
    fields = [
        ("Network", status.get("network") or status.get("networkName") or status.get("chain")),
        ("Epoch", status.get("epoch") or status.get("currentEpoch")),
        ("Tick", status.get("tick") or status.get("currentTick") or status.get("latestTick")),
        ("Active addresses", status.get("activeAddresses")),
        ("Circulating supply", status.get("circulatingSupply") or status.get("supply")),
        ("Price (USD)", status.get("price") or status.get("priceUsd")),
        ("Market cap (USD)", status.get("marketCap") or status.get("marketCapUsd")),
        ("Timestamp", status.get("timestamp") or status.get("time") or status.get("updatedAt")),
    ]
    summary = []
    for label, value in fields:
        if value is None or value == "":
            continue
        summary.append({"Metric": label, "Value": format_qubic_value(value)})
    return summary


def build_qubic_balance_summary(balance: dict) -> List[Dict[str, str]]:
    """Pick common balance fields from a Qubic RPC payload."""
    if not isinstance(balance, dict):
        return []
    fields = [
        ("Balance", balance.get("balance")),
        ("Incoming amount", balance.get("incomingAmount")),
        ("Outgoing amount", balance.get("outgoingAmount")),
        ("Incoming transfers", balance.get("numberOfIncomingTransfers")),
        ("Outgoing transfers", balance.get("numberOfOutgoingTransfers")),
    ]
    summary = []
    for label, value in fields:
        if value is None or value == "":
            continue
        summary.append({"Metric": label, "Value": format_qubic_value(value)})
    return summary


# =========================
# Cached-ish accessors
# =========================

def get_qubic_rpc_endpoint() -> str:
    endpoint = st.session_state.get("qubic_rpc_endpoint", QUBIC_PUBLIC_RPC)
    if not isinstance(endpoint, str):
        return QUBIC_PUBLIC_RPC
    endpoint = endpoint.strip()
    return endpoint or QUBIC_PUBLIC_RPC


def get_qubic_status_cached(rpc_endpoint: str) -> dict:
    return attach_fetch_meta(fetch_qubic_status(rpc_endpoint))


def get_qubic_tick_cached(rpc_endpoint: str) -> dict:
    return attach_fetch_meta(fetch_qubic_tick(rpc_endpoint))


def get_qubic_balance_cached(identity: str, rpc_endpoint: str) -> dict:
    return attach_fetch_meta(fetch_qubic_balance(identity, rpc_endpoint))


def pick_qubic_tick(status: dict, tick_info: dict) -> Optional[int]:
    candidates = []
    if isinstance(tick_info, dict) and "error" not in tick_info:
        candidates.append(tick_info.get("tick") or tick_info.get("currentTick") or tick_info.get("latestTick"))
    if isinstance(status, dict) and "error" not in status:
        candidates.append(status.get("tick") or status.get("currentTick") or status.get("latestTick"))

    for item in candidates:
        value = coerce_number(item)
        if value is not None:
            return int(value)
    return None


def pick_qubic_price(status: dict) -> Optional[float]:
    if not isinstance(status, dict) or "error" in status:
        return None
    for key in ("price", "priceUsd", "priceUSD"):
        if key in status:
            v = coerce_number(status.get(key))
            if v is not None:
                return v
    return None


def update_qubic_market_history(state, status: dict, tick_info: dict, max_points: int = 30):
    tick_value = pick_qubic_tick(status, tick_info)
    price_value = pick_qubic_price(status)
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    ticks = state.get("qubic_tick_history")
    if not isinstance(ticks, list):
        ticks = []
    if tick_value is not None:
        if not ticks or ticks[-1].get("value") != tick_value:
            ticks.append({"ts": ts, "value": tick_value})
            ticks = ticks[-max_points:]

    prices = state.get("qubic_price_history")
    if not isinstance(prices, list):
        prices = []
    if price_value is not None:
        rounded = round(price_value, 6)
        if not prices or prices[-1].get("value") != rounded:
            prices.append({"ts": ts, "value": rounded})
            prices = prices[-max_points:]

    state["qubic_tick_history"] = ticks
    state["qubic_price_history"] = prices
