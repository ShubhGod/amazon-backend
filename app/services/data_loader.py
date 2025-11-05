import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import EXCEL_FILE, CACHE_TTL_SECONDS, COLUMNS
from app.core.logger import logger

class DataCache:
    """In-memory cache for DataFrame."""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.loaded_at: Optional[datetime] = None
        self.stats = {}
    
    def is_expired(self) -> bool:
        """Check if cache expired."""
        if not self.loaded_at:
            return True
        return datetime.now() - self.loaded_at > timedelta(seconds=CACHE_TTL_SECONDS)
    
    def clear(self):
        """Clear cache."""
        self.df = None
        self.loaded_at = None
        self.stats = {}

cache = DataCache()

def load_excel() -> pd.DataFrame:
    """Load Excel → DataFrame with validation."""
    global cache
    
    # Return cached if valid
    if cache.df is not None and not cache.is_expired():
        logger.info("Returning cached DataFrame")
        return cache.df
    
    logger.info(f"Loading Excel from {EXCEL_FILE}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Sheet1")
        
        # Standardize columns
        df.rename(columns=str.lower, inplace=True)
        
        # Data cleaning
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(-1)
        df['delivery_days'] = pd.to_numeric(df['delivery_days'], errors='coerce').fillna(-1).astype(int)
        df['delivery_fee'] = pd.to_numeric(df['delivery_fee'], errors='coerce').fillna(-1)
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce').fillna(0).astype(int)
        
        # Normalize source
        df['source_normalized'] = df['source_normalized'].fillna('unknown')
        
        # Compute stats
        cache.df = df
        cache.loaded_at = datetime.now()
        cache.stats = compute_data_stats(df)
        
        logger.info(f"Loaded {len(df)} rows | {df['prompt_id'].nunique()} unique prompts")
        return df
    
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        raise

def compute_data_stats(df: pd.DataFrame) -> dict:
    """Compute data quality stats."""
    return {
        "total_rows": len(df),
        "unique_prompts": df['prompt_id'].nunique(),
        "unique_products": df['product_name'].nunique(),
        "unique_sources": df['source_normalized'].nunique(),
        "rows_with_valid_price": (df['price'] > 0).sum(),
        "rows_with_valid_delivery": (df['delivery_days'] >= 0).sum(),
        "price_completeness": round((df['price'] > 0).sum() / len(df), 2),
        "delivery_completeness": round((df['delivery_days'] >= 0).sum() / len(df), 2),
    }

def get_data() -> pd.DataFrame:
    """Get cached or fresh DataFrame."""
    return load_excel()

def get_stats() -> dict:
    """Get cache stats."""
    return cache.stats

def reload_data():
    """Force reload cache."""
    cache.clear()
    return load_excel()
