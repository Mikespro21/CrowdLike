import random
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Action weights reflect "strain" or intensity of different behaviors.
ACTION_WEIGHTS = {
    "buy": 2.0,
    "sell": 2.0,
    "stake": 3.0,
    "swap": 3.0,
    "deposit": 1.0,
    "withdraw": 2.0,
}


def _day_key(ts) -> str:
    """Convert a datetime or timestamp to YYYY-MM-DD string."""
    if isinstance(ts, (int, float)):
        dt = datetime.utcfromtimestamp(ts)
    elif isinstance(ts, datetime):
        dt = ts
    else:
        # Fallback: now
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%d")


def _percentile_rank(value: float, population: List[float]) -> float:
    if not population:
        return 0.0
    count = sum(1 for x in population if x <= value)
    return (count / len(population)) * 100.0


def _avg_nonzero(values: List[float]) -> float:
    non_zero = [v for v in values if v > 0]
    if not non_zero:
        return 0.0
    return sum(non_zero) / len(non_zero)


def _build_demo_events(
    user_actions: List[Dict[str, Any]],
    num_other_users: int = 25,
    days: int = 14,
    seed: Optional[int] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Build a synthetic event dataset including the current user and other users.

    user_actions: list of dicts with at least action_type, amount, asset, timestamp (optional).
    """
    rng = random.Random(seed)
    user_id_you = "you"
    user_events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    now = datetime.utcnow()

    # Current user actions (treated as today)
    for act in user_actions:
        ts = act.get("timestamp") or now
        if not isinstance(ts, datetime):
            ts = now
        action_type = str(act.get("action_type", "other")).lower()
        amount = float(act.get("amount", 0.0))
        asset = str(act.get("asset", "QUBIC"))

        user_events[user_id_you].append(
            {
                "user_id": user_id_you,
                "timestamp": ts,
                "action_type": action_type,
                "amount": amount,
                "asset": asset,
            }
        )

    # Add some historical activity for the current user so momentum makes sense
    for day_offset in range(1, days):
        num_actions = rng.randint(0, 4)
        for _ in range(num_actions):
            ts = (
                now
                - timedelta(days=day_offset)
            ).replace(
                hour=rng.randint(0, 23),
                minute=rng.randint(0, 59),
                second=rng.randint(0, 59),
                microsecond=0,
            )
            action_type = rng.choice(list(ACTION_WEIGHTS.keys()))
            amount = rng.uniform(5, 150)
            user_events[user_id_you].append(
                {
                    "user_id": user_id_you,
                    "timestamp": ts,
                    "action_type": action_type,
                    "amount": amount,
                    "asset": "QUBIC",
                }
            )

    # Other synthetic users
    for i in range(num_other_users):
        user_id = f"user_{i+1}"
        for day_offset in range(days):
            num_actions = rng.randint(0, 6)
            for _ in range(num_actions):
                ts = (
                    now
                    - timedelta(days=day_offset)
                ).replace(
                    hour=rng.randint(0, 23),
                    minute=rng.randint(0, 59),
                    second=rng.randint(0, 59),
                    microsecond=0,
                )
                action_type = rng.choice(list(ACTION_WEIGHTS.keys()))
                amount = rng.uniform(5, 200)
                user_events[user_id].append(
                    {
                        "user_id": user_id,
                        "timestamp": ts,
                        "action_type": action_type,
                        "amount": amount,
                        "asset": "QUBIC",
                    }
                )
    return user_events


def _compute_daily_strain(user_events: Dict[str, List[Dict[str, Any]]]):
    """Compute daily strain and decision intensity for each user and day."""
    daily_strain: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    daily_decision: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for user, events in user_events.items():
        for ev in events:
            day = _day_key(ev["timestamp"])
            action_type = ev.get("action_type", "other")
            amount = float(ev.get("amount", 0.0))

            base_weight = ACTION_WEIGHTS.get(action_type, 1.0)
            # Mild boost for larger amounts so big trades feel "heavier"
            amount_factor = 1.0 + math.log1p(abs(amount)) / 5.0
            daily_strain[user][day] += base_weight * amount_factor

        # Decision score: smoothed transform of strain
        for day, s in daily_strain[user].items():
            daily_decision[user][day] = math.log1p(s)

    return daily_strain, daily_decision


def _compute_TES_BSS_for_day(
    day: str,
    daily_strain: Dict[str, Dict[str, float]],
    daily_decision: Dict[str, Dict[str, float]],
):
    users = list(daily_strain.keys())
    all_decisions = [daily_decision[u].get(day, 0.0) for u in users]
    all_strains = [daily_strain[u].get(day, 0.0) for u in users]

    if sum(all_strains) == 0:
        return {u: {"TES": 0.0, "BSS": 0.0} for u in users}

    epsilon = 0.25
    scores = {}

    for u in users:
        d_u = daily_decision[u].get(day, 0.0)
        s_u = daily_strain[u].get(day, 0.0)

        similar = sum(1 for d in all_decisions if abs(d - d_u) <= epsilon)
        TES = (similar / len(all_decisions)) * 100.0
        BSS = _percentile_rank(s_u, all_strains)

        scores[u] = {"TES": TES, "BSS": BSS}

    return scores


def _compute_BMS(
    daily_scores_by_user: Dict[str, Dict[str, Dict[str, float]]],
    days_list: List[str],
):
    BMS: Dict[str, Dict[str, float]] = {}

    for user, day_scores in daily_scores_by_user.items():
        TES_series: List[float] = []
        BSS_series: List[float] = []

        for day in days_list:
            entry = day_scores.get(day, {"TES": 0.0, "BSS": 0.0})
            TES_series.append(entry["TES"])
            BSS_series.append(entry["BSS"])

        active_days = sum(1 for x in BSS_series if x > 0)
        consistency = (active_days / len(days_list)) * 100.0 if days_list else 0.0

        if days_list:
            mid = max(1, len(days_list) // 2)
            past_avg = (
                _avg_nonzero(TES_series[:mid]) + _avg_nonzero(BSS_series[:mid])
            ) / 2.0
            recent_avg = (
                _avg_nonzero(TES_series[mid:]) + _avg_nonzero(BSS_series[mid:])
            ) / 2.0
            raw_trend = recent_avg - past_avg
        else:
            raw_trend = 0.0

        trend = max(0.0, min(100.0, 50.0 + raw_trend))
        BMS[user] = {
            "Consistency%": consistency,
            "Trend%": trend,
            "BMS%": 0.5 * consistency + 0.5 * trend,
        }

    return BMS


def _compute_CFS(
    BMS_history: Dict[str, Dict[str, float]],
    target_user: str = "you",
):
    users = list(BMS_history.keys())
    if target_user not in BMS_history:
        if not users:
            return {}
        target_user = users[0]

    target_past = BMS_history[target_user]["past"]
    delta = 5.0

    cohort = [
        u
        for u in users
        if u != target_user and abs(BMS_history[u]["past"] - target_past) <= delta
    ]

    if not cohort:
        return {
            "target_user": target_user,
            "cohort_size": 0,
            "Improve%": 0.0,
            "Stable%": 0.0,
            "Decline%": 0.0,
        }

    improved = 0
    stable = 0
    declined = 0
    TOL = 3.0

    for u in cohort:
        diff = BMS_history[u]["future"] - BMS_history[u]["past"]
        if diff > TOL:
            improved += 1
        elif diff < -TOL:
            declined += 1
        else:
            stable += 1

    n = len(cohort)
    return {
        "target_user": target_user,
        "cohort_size": n,
        "Improve%": (improved / n) * 100.0,
        "Stable%": (stable / n) * 100.0,
        "Decline%": (declined / n) * 100.0,
    }


def compute_metrics(
    user_actions: Optional[List[Dict[str, Any]]] = None,
    num_other_users: int = 25,
    days: int = 14,
    seed: Optional[int] = None,
):
    """High-level entry point used by the Streamlit app.

    user_actions: list of actions for the logged-in user in the current demo session.
    Returns a dict with:
        - target_user
        - days
        - daily_scores
        - BMS
        - CFS
    """
    if user_actions is None:
        user_actions = []

    user_events = _build_demo_events(
        user_actions, num_other_users=num_other_users, days=days, seed=seed
    )
    daily_strain, daily_decision = _compute_daily_strain(user_events)

    # Collect all observed days and keep the most recent `days` of them
    all_days = sorted(
        {
            _day_key(ev["timestamp"])
            for events in user_events.values()
            for ev in events
        }
    )
    if len(all_days) > days:
        days_list = all_days[-days:]
    else:
        days_list = all_days

    daily_scores_by_user: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(dict)

    for day in days_list:
        scores = _compute_TES_BSS_for_day(day, daily_strain, daily_decision)
        for user, s in scores.items():
            daily_scores_by_user[user][day] = s

    BMS_scores = _compute_BMS(daily_scores_by_user, days_list)

    # Create simple past/future BMS history with random noise
    rng = random.Random(seed)
    BMS_history: Dict[str, Dict[str, float]] = {}
    for user, info in BMS_scores.items():
        base = info["BMS%"]
        past = base + rng.uniform(-5, 5)
        future = base + rng.uniform(-5, 5)
        BMS_history[user] = {"past": past, "future": future}

    cfs_result = _compute_CFS(BMS_history, target_user="you")

    return {
        "target_user": "you",
        "days": days_list,
        "daily_scores": daily_scores_by_user,
        "BMS": BMS_scores,
        "CFS": cfs_result,
    }
