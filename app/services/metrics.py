import pandas as pd
from typing import Dict, List, Tuple
from app.core.config import COLUMNS, INVALID_PRICE, INVALID_DELIVERY
from app.utils.helpers import (
    is_valid_price, is_valid_delivery, get_delivery_strength,
    calculate_nrs, get_rank_presence_score, calculate_price_competitiveness_flag
)

def calculate_global_metrics(df: pd.DataFrame) -> Dict:
    """Calculate global KPI metrics."""
    
    total_prompts = df['prompt_id'].nunique()
    
    # G-SoV (Generative Share of Voice): % of prompts where source appears at rank 1 or 2
    gsov_by_source = {}
    for source in df['source_normalized'].unique():
        source_df = df[df['source_normalized'] == source]
        top_rank_prompts = source_df[source_df['rank'] <= 2]['prompt_id'].nunique()
        gsov_by_source[source] = round(top_rank_prompts / total_prompts, 3)
    
    gsov_overall = round(
        df[df['rank'] <= 2]['prompt_id'].nunique() / total_prompts, 3
    )
    
    # Average rank position
    avg_rank = round(df['rank'].mean(), 2)
    
    # Rank presence score (avg of all cards)
    df['rank_presence'] = df['rank'].apply(get_rank_presence_score)
    rank_presence_avg = round(df['rank_presence'].mean(), 2)
    
    # Price competitiveness rate
    def is_cheapest(group):
        valid_prices = group[group['price'] > 0]['price']
        if len(valid_prices) == 0:
            return pd.Series(0, index=group.index)
        min_price = valid_prices.min()
        return (group['price'] == min_price).astype(int)
    
    df['is_cheapest'] = df.groupby('prompt_id', group_keys=False).apply(is_cheapest)
    price_competitiveness = round(
        df[df['price'] > 0]['is_cheapest'].sum() / len(df[df['price'] > 0]), 3
    ) if len(df[df['price'] > 0]) > 0 else 0.0
    
    # Delivery strength score
    df['delivery_strength'] = df['delivery_days'].apply(get_delivery_strength)
    delivery_strength_avg = round(df['delivery_strength'].mean(), 2)
    
    # Prompt coverage
    prompt_coverage = round(
        df['prompt_id'].nunique() / df['prompt_id'].nunique(), 3
    )  # 1.0 for now (you appear in all)
    
    return {
        "gsov_overall": gsov_overall,
        "gsov_by_platform": gsov_by_source,
        "avg_rank_position": avg_rank,
        "rank_presence_score": rank_presence_avg,
        "price_competitiveness_rate": price_competitiveness,
        "delivery_strength_score": delivery_strength_avg,
        "prompt_coverage_rate": prompt_coverage,
    }

def calculate_loss_reasons(df: pd.DataFrame) -> List[Dict]:
    """Top 5 reasons for not ranking #1."""
    
    loss_categories = {
        "higher_price": 0,
        "slower_delivery": 0,
        "missing_price": 0,
        "missing_delivery": 0,
        "lower_rank_naturally": 0,
    }
    
    for prompt_id in df['prompt_id'].unique():
        group = df[df['prompt_id'] == prompt_id]
        best_rank_row = group.loc[group['rank'].idxmin()]
        best_rank = best_rank_row['rank']
        
        if best_rank > 1:
            for _, row in group.iterrows():
                if row['rank'] < best_rank_row['rank']:
                    if is_valid_price(row['price']) and is_valid_price(best_rank_row['price']):
                        if row['price'] < best_rank_row['price']:
                            loss_categories["higher_price"] += 1
                    
                    if is_valid_delivery(row['delivery_days']) and is_valid_delivery(best_rank_row['delivery_days']):
                        if row['delivery_days'] < best_rank_row['delivery_days']:
                            loss_categories["slower_delivery"] += 1
                
                if not is_valid_price(row['price']):
                    loss_categories["missing_price"] += 1
                if not is_valid_delivery(row['delivery_days']):
                    loss_categories["missing_delivery"] += 1
    
    total = sum(loss_categories.values()) or 1
    
    losses = [
        {"reason": k.replace("_", " ").title(), "occurrences": v, "weight": round(v / total, 3)}
        for k, v in sorted(loss_categories.items(), key=lambda x: x[1], reverse=True)
        if v > 0
    ]
    
    return losses[:5]

def calculate_source_breakdown(df: pd.DataFrame) -> List[Dict]:
    """Per-source performance metrics."""
    
    breakdown = []
    for source in sorted(df['source_normalized'].unique()):
        source_df = df[df['source_normalized'] == source]
        
        cards = len(source_df)
        avg_rank = round(source_df['rank'].mean(), 2)
        
        # Price competitiveness for this source
        top_rank_count = len(source_df[source_df['rank'] <= 2])
        price_comp = round(top_rank_count / cards, 3) if cards > 0 else 0.0
        
        breakdown.append({
            "source": source,
            "cards": cards,
            "avg_rank": avg_rank,
            "price_competitiveness": price_comp,
        })
    
    return sorted(breakdown, key=lambda x: x['avg_rank'])

def calculate_nrs_per_row(df: pd.DataFrame) -> pd.DataFrame:
    """Add NRS column to dataframe (per-prompt max_rank)."""
    
    def compute_nrs(group):
        max_rank = group['rank'].max()
        group['nrs'] = group['rank'].apply(lambda r: calculate_nrs(r, max_rank))
        return group
    
    df = df.groupby('prompt_id', group_keys=False).apply(compute_nrs)
    return df
