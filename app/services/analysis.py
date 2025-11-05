import pandas as pd
from typing import List, Dict
from app.utils.helpers import calculate_nrs

def generate_heatmap_data(df: pd.DataFrame) -> List[Dict]:
    """Product × Source heatmap with avg NRS."""
    
    heatmap = []
    
    # Add NRS if not exists
    if 'nrs' not in df.columns:
        df = df.copy()
        def compute_nrs(group):
            max_rank = group['rank'].max()
            group['nrs'] = group['rank'].apply(lambda r: calculate_nrs(r, max_rank))
            return group
        df = df.groupby('prompt_id', group_keys=False).apply(compute_nrs)
    
    for product in sorted(df['product_name'].unique()):
        for source in sorted(df['source_normalized'].unique()):
            subset = df[(df['product_name'] == product) & (df['source_normalized'] == source)]
            
            if len(subset) > 0:
                avg_nrs = round(subset['nrs'].mean(), 2)
                heatmap.append({
                    "product": product,
                    "source": source,
                    "avg_nrs": avg_nrs,
                    "card_count": len(subset),
                })
    
    return heatmap

def generate_product_performance(df: pd.DataFrame) -> List[Dict]:
    """Product performance table."""
    
    if 'nrs' not in df.columns:
        df = df.copy()
        def compute_nrs(group):
            max_rank = group['rank'].max()
            group['nrs'] = group['rank'].apply(lambda r: calculate_nrs(r, max_rank))
            return group
        df = df.groupby('prompt_id', group_keys=False).apply(compute_nrs)
    
    performance = []
    
    for product in sorted(df['product_name'].unique()):
        product_df = df[df['product_name'] == product]
        
        # G-SoV
        total_prompts = df['prompt_id'].nunique()
        product_rank1_prompts = len(product_df[product_df['rank'] == 1])
        gsov = round(product_rank1_prompts / total_prompts, 3) if total_prompts > 0 else 0.0
        
        # Avg rank
        avg_rank = round(product_df['rank'].mean(), 2)
        
        # Prompt count
        prompt_count = product_df['prompt_id'].nunique()
        
        # Price gap (best price in product vs min price)
        best_price = product_df[product_df['price'] > 0]['price'].min() if len(product_df[product_df['price'] > 0]) > 0 else None
        worst_price = product_df[product_df['price'] > 0]['price'].max() if len(product_df[product_df['price'] > 0]) > 0 else None
        price_gap = round(((worst_price - best_price) / best_price * 100), 2) if best_price and worst_price else None
        
        # Delivery gap
        min_delivery = product_df[product_df['delivery_days'] >= 0]['delivery_days'].min() if len(product_df[product_df['delivery_days'] >= 0]) > 0 else None
        max_delivery = product_df[product_df['delivery_days'] >= 0]['delivery_days'].max() if len(product_df[product_df['delivery_days'] >= 0]) > 0 else None
        delivery_gap = max_delivery - min_delivery if min_delivery and max_delivery else None
        
        performance.append({
            "product": product,
            "gsov": gsov,
            "avg_rank": avg_rank,
            "prompt_count": prompt_count,
            "price_gap_pct": price_gap,
            "delivery_gap_days": delivery_gap,
        })
    
    return sorted(performance, key=lambda x: x['avg_rank'])

def generate_card_summaries(df: pd.DataFrame) -> List[Dict]:
    """Convert rows to card summaries."""
    
    cards = []
    for _, row in df.iterrows():
        cards.append({
            "card_id": row['card_id'],
            "product_name": row['product_name'],
            "rank": int(row['rank']),
            "source": row['source_normalized'],
            "price": float(row['price']) if row['price'] > 0 else None,
            "currency": row['price_currency'] if row['price_currency'] != '-1' else None,
            "delivery_days": int(row['delivery_days']) if row['delivery_days'] >= 0 else None,
            "delivery_fee": float(row['delivery_fee']) if row['delivery_fee'] > 0 else None,
        })
    
    return cards
