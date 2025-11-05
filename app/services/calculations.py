import pandas as pd
from typing import Dict, List
from app.core.config import DELIVERY_THRESHOLDS
from app.utils.helpers import is_valid_price, is_valid_delivery, get_delivery_strength

def calculate_composite_rank_driver(
    attr_score: float = 0.0,
    delivery_score: float = 0.0,
    review_score: float = 0.0,
    price_score: float = 0.0,
    freshness_score: float = 0.0,
    citation_score: float = 0.0,
    weights: Dict[str, float] = None,
) -> float:
    """
    Composite scoring with tunable weights.
    weights: {attr, delivery, review, price, freshness, citation}
    """
    
    if weights is None:
        weights = {
            "attr": 0.25,
            "delivery": 0.20,
            "review": 0.20,
            "price": 0.15,
            "freshness": 0.10,
            "citation": 0.10,
        }
    
    score = (
        weights.get("attr", 0) * attr_score +
        weights.get("delivery", 0) * delivery_score +
        weights.get("review", 0) * review_score +
        weights.get("price", 0) * price_score +
        weights.get("freshness", 0) * freshness_score +
        weights.get("citation", 0) * citation_score
    )
    
    return round(min(10.0, max(0.0, score)), 2)

def calculate_rca_stack(row: pd.Series) -> Dict[str, float]:
    """
    Calculate RCA factors for single row (all stub values for now).
    """
    
    # Delivery strength
    delivery_score = get_delivery_strength(row['delivery_days']) * 10
    
    # Price score (normalized: 0-10)
    price_score = 0.0
    if is_valid_price(row['price']):
        price_score = 5.0  # Stub; needs context
    
    # Attribute completeness (stub)
    attr_score = 7.0
    
    # Review density (stub)
    review_score = 6.0
    
    # Citation parity (stub)
    citation_score = 5.0
    
    # Freshness (stub)
    freshness_score = 7.0
    
    return {
        "price": round(price_score, 1),
        "delivery": round(delivery_score, 1),
        "reviews": round(review_score, 1),
        "attributes": round(attr_score, 1),
        "citations": round(citation_score, 1),
        "freshness": round(freshness_score, 1),
    }

def calculate_auto_suggestions(rca_stack: Dict[str, float], row: pd.Series) -> List[str]:
    """Generate recommendations based on RCA scores."""
    
    suggestions = []
    
    if rca_stack["price"] < 3:
        suggestions.append("Reduce price to compete better")
    
    if rca_stack["delivery"] < 3:
        suggestions.append("Improve delivery time estimates")
    
    if rca_stack["attributes"] < 4:
        suggestions.append("Add missing product attributes & schema markup")
    
    if rca_stack["reviews"] < 4:
        suggestions.append("Increase review count & rating signals")
    
    if not is_valid_price(row['price']):
        suggestions.append("Add valid pricing information")
    
    if not is_valid_delivery(row['delivery_days']):
        suggestions.append("Provide delivery time estimate")
    
    return suggestions[:3]  # Top 3 only
