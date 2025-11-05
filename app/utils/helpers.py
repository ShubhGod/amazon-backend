import pandas as pd
from typing import Dict, List, Optional, Tuple
from app.core.config import (
    MAX_RANK, DELIVERY_THRESHOLDS, PRICE_PERCENTILE_THRESHOLD,
    INVALID_PRICE, INVALID_DELIVERY, COLUMNS
)

def normalize_source(source: str) -> str:
    """Normalize marketplace names (handles case, aliases)."""
    if pd.isna(source):
        return "unknown"
    s = str(source).strip().lower()
    mapping = {
        "amazon": "amazon",
        "amazon.in": "amazon",
        "flipkart": "flipkart",
        "fliptwirls.com": "flipkart",
        "ubuy": "ubuy",
    }
    return mapping.get(s, s)

def is_valid_price(price: float) -> bool:
    """Check if price is valid (not marker value)."""
    return price > 0 and price != INVALID_PRICE

def is_valid_delivery(delivery_days: int) -> bool:
    """Check if delivery_days is valid."""
    return delivery_days >= 0 and delivery_days != INVALID_DELIVERY

def get_delivery_strength(delivery_days: int) -> float:
    """Return delivery strength score (0.0-1.0)."""
    if not is_valid_delivery(delivery_days):
        return 0.0
    if delivery_days <= DELIVERY_THRESHOLDS["strong"][1]:
        return 1.0
    elif delivery_days <= DELIVERY_THRESHOLDS["medium"][1]:
        return 0.7
    elif delivery_days <= DELIVERY_THRESHOLDS["weak"][1]:
        return 0.3
    return 0.1

def parse_extra_column(extra_str: str) -> List[str]:
    """Parse 'extra' column (stored as string repr of list)."""
    try:
        if pd.isna(extra_str):
            return []
        if isinstance(extra_str, list):
            return extra_str
        # Try eval if it's a string representation
        import ast
        return ast.literal_eval(str(extra_str))
    except Exception:
        return []

def round_to_decimals(value: float, decimals: int = 2) -> float:
    """Round to N decimals."""
    return round(value, decimals) if value is not None else None

def calculate_price_competitiveness_flag(
    price: float, prices_in_prompt: List[float]
) -> bool:
    """Check if price <= p25 of prices in same prompt."""
    if not is_valid_price(price):
        return False
    valid_prices = [p for p in prices_in_prompt if is_valid_price(p)]
    if not valid_prices:
        return False
    p25 = pd.Series(valid_prices).quantile(PRICE_PERCENTILE_THRESHOLD / 100)
    return price <= p25

def calculate_nrs(rank: int, max_rank_in_prompt: int) -> float:
    """Calculate Normalized Rank Score (0-10)."""
    if rank < 1 or rank > max_rank_in_prompt:
        return 0.0
    nrs = ((max_rank_in_prompt + 1 - rank) / max_rank_in_prompt) * 10
    return round_to_decimals(nrs)

def get_rank_presence_score(rank: int) -> int:
    """Return rank presence score (0, 4, 7, 10)."""
    if rank == 1:
        return 10
    elif rank in [2, 3]:
        return 7
    elif rank <= 5:
        return 4
    return 0

def calculate_percentile(value: float, values: List[float]) -> Optional[float]:
    """Calculate percentile rank (0-100)."""
    valid = [v for v in values if is_valid_price(v)]
    if not valid or not is_valid_price(value):
        return None
    percentile = (sum(1 for v in valid if v < value) / len(valid)) * 100
    return round_to_decimals(percentile)
