import pandas as pd
from typing import Optional, List, Dict

def apply_filters(
    df: pd.DataFrame,
    product: Optional[str] = None,
    source: Optional[str] = None,
    rank_min: int = 1,
    rank_max: int = 5,
    has_price: bool = False,
    has_delivery: bool = False,
) -> pd.DataFrame:
    """Apply filters to DataFrame."""
    
    filtered = df.copy()
    
    # Product filter
    if product:
        products = [p.strip() for p in product.split(",")]
        filtered = filtered[filtered['product_name'].isin(products)]
    
    # Source filter
    if source:
        sources = [s.strip().lower() for s in source.split(",")]
        filtered = filtered[filtered['source_normalized'].isin(sources)]
    
    # Rank range
    filtered = filtered[(filtered['rank'] >= rank_min) & (filtered['rank'] <= rank_max)]
    
    # Price filter
    if has_price:
        filtered = filtered[filtered['price'] > 0]
    
    # Delivery filter
    if has_delivery:
        filtered = filtered[filtered['delivery_days'] >= 0]
    
    return filtered

def get_applied_filters(
    product: Optional[str] = None,
    source: Optional[str] = None,
    rank_min: int = 1,
    rank_max: int = 5,
    has_price: bool = False,
    has_delivery: bool = False,
) -> Dict:
    """Return summary of applied filters."""
    
    filters = {
        "rank_range": f"{rank_min}-{rank_max}",
    }
    
    if product:
        filters["product"] = product
    if source:
        filters["source"] = source
    if has_price:
        filters["has_valid_price"] = True
    if has_delivery:
        filters["has_valid_delivery"] = True
    
    return filters
