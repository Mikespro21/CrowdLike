# app/storage.py

import json
import os
from typing import Any, Dict, Optional
import hashlib
import secrets


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _safe_id(user_id: str) -> str:
    user_id = (user_id or "").strip()
    safe = "".join(c for c in user_id if c.isalnum() or c in ("-", "_", ".", "@"))
    return safe or "anonymous"

def _path(user_id: str) -> str:
    return os.path.join(DATA_DIR, f"user_{_safe_id(user_id)}.json")

def load_user_state(user_id: str) -> Optional[Dict[str, Any]]:
    p = _path(user_id)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None

def save_user_state(user_id: str, state: Dict[str, Any]) -> None:
    p = _path(user_id)
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        # Don’t crash the app if disk write fails
        pass

def merge_state(defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safe merge: defaults provide any new keys; loaded overrides existing keys.
    """
    out = dict(defaults)
    if isinstance(loaded, dict):
        out.update(loaded)
    return out
def _pbkdf2_hash(password: str, salt_hex: str, rounds: int = 200_000) -> str:
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        rounds,
        dklen=32,
    )
    return dk.hex()

def set_password_fields(state: dict, password: str) -> dict:
    """
    Sets password fields on a state dict. Stores only salted hash + metadata.
    """
    salt = secrets.token_hex(16)  # 16 bytes salt
    rounds = 200_000
    pw_hash = _pbkdf2_hash(password, salt, rounds)
    state["auth_pw_salt"] = salt
    state["auth_pw_hash"] = pw_hash
    state["auth_pw_rounds"] = rounds
    return state

def has_password(state: dict) -> bool:
    return bool(state.get("auth_pw_salt")) and bool(state.get("auth_pw_hash"))

def verify_password(state: dict, password: str) -> bool:
    salt = state.get("auth_pw_salt")
    pw_hash = state.get("auth_pw_hash")
    rounds = int(state.get("auth_pw_rounds") or 200_000)
    if not salt or not pw_hash:
        return False
    return _pbkdf2_hash(password, salt, rounds) == pw_hash
