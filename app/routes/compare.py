from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.models.schemas import ComparisonResponse, ComparisonMetric, WinLoseChip
from app.services.data_loader import get_data
from app.utils.helpers import is_valid_price, is_valid_delivery, round_to_decimals
from app.core.logger import logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/compare", response_model=ComparisonResponse)
async def get_comparison(
    product_name: str = Query(..., description="Product to compare"),
    source1: str = Query("amazon", description="Primary source"),
    source2: Optional[str] = Query(None, description="Secondary source (auto-detect if None)"),
):
    """
    Head-to-head comparison: source1 vs source2 for given product.
    """
    try:
        df = get_data()
        
        # Filter for product
        product_df = df[df['product_name'] == product_name]
        
        if len(product_df) == 0:
            raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")
        
        # Get source1 data
        s1_data = product_df[product_df['source_normalized'] == source1.lower()]
        
        # Auto-detect source2 if not provided
        if source2 is None:
            available_sources = [s for s in product_df['source_normalized'].unique() 
                                if s != source1.lower()]
            source2 = available_sources[0] if available_sources else "unknown"
        
        s2_data = product_df[product_df['source_normalized'] == source2.lower()]
        
        # Calculate metrics
        metrics = []
        
        # Avg Price
        s1_price = s1_data[s1_data['price'] > 0]['price'].mean() if len(s1_data[s1_data['price'] > 0]) > 0 else None
        s2_price = s2_data[s2_data['price'] > 0]['price'].mean() if len(s2_data[s2_data['price'] > 0]) > 0 else None
        
        if s1_price and s2_price:
            gap = s2_price - s1_price
            gap_pct = round_to_decimals((gap / s1_price) * 100)
            winner = "source1" if s1_price < s2_price else ("source2" if s2_price < s1_price else "tie")
            metrics.append(ComparisonMetric(
                metric="Average Price",
                source1_value=round_to_decimals(s1_price),
                source2_value=round_to_decimals(s2_price),
                gap=round_to_decimals(gap),
                gap_pct=gap_pct,
                winner=winner,
            ))
        
        # Avg Rank
        s1_rank = s1_data['rank'].mean() if len(s1_data) > 0 else 999
        s2_rank = s2_data['rank'].mean() if len(s2_data) > 0 else 999
        gap = s2_rank - s1_rank
        winner = "source1" if s1_rank < s2_rank else ("source2" if s2_rank < s1_rank else "tie")
        metrics.append(ComparisonMetric(
            metric="Average Rank",
            source1_value=round_to_decimals(s1_rank),
            source2_value=round_to_decimals(s2_rank),
            gap=round_to_decimals(gap),
            gap_pct=0.0,
            winner=winner,
        ))
        
        # Avg Delivery Days
        s1_delivery = s1_data[s1_data['delivery_days'] >= 0]['delivery_days'].mean() if len(s1_data[s1_data['delivery_days'] >= 0]) > 0 else None
        s2_delivery = s2_data[s2_data['delivery_days'] >= 0]['delivery_days'].mean() if len(s2_data[s2_data['delivery_days'] >= 0]) > 0 else None
        
        if s1_delivery and s2_delivery:
            gap = s2_delivery - s1_delivery
            winner = "source1" if s1_delivery < s2_delivery else ("source2" if s2_delivery < s1_delivery else "tie")
            metrics.append(ComparisonMetric(
                metric="Average Delivery Days",
                source1_value=round_to_decimals(s1_delivery),
                source2_value=round_to_decimals(s2_delivery),
                gap=round_to_decimals(gap),
                gap_pct=0.0,
                winner=winner,
            ))
        
        # Card Frequency
        s1_freq = len(s1_data)
        s2_freq = len(s2_data)
        winner = "source1" if s1_freq > s2_freq else ("source2" if s2_freq > s1_freq else "tie")
        metrics.append(ComparisonMetric(
            metric="Appearances",
            source1_value=float(s1_freq),
            source2_value=float(s2_freq),
            gap=float(s2_freq - s1_freq),
            gap_pct=0.0,
            winner=winner,
        ))
        
        # Win/Lose Chips
        chips = []
        for metric in metrics:
            if metric.winner == "source1":
                if metric.metric == "Average Price":
                    value = f"-{abs(metric.gap_pct):.0f}%"
                    factor = "Better Price"
                elif metric.metric == "Average Rank":
                    value = f"{abs(metric.gap):.1f} positions"
                    factor = "Better Rank"
                elif metric.metric == "Average Delivery Days":
                    value = f"-{abs(metric.gap):.0f} days"
                    factor = "Faster Delivery"
                else:
                    value = f"+{abs(metric.gap):.0f}"
                    factor = "More Appearances"
                
                chips.append(WinLoseChip(
                    factor=factor,
                    status="win",
                    value=value,
                    contribution=0.5,
                ))
        
        # Metadata
        metadata = {
            "comparison_timestamp": datetime.now().isoformat(),
            "s1_cards": len(s1_data),
            "s2_cards": len(s2_data),
        }
        
        response = ComparisonResponse(
            product_name=product_name,
            source1=source1,
            source2=source2,
            metrics=metrics,
            win_lose_chips=chips,
            metadata=metadata,
        )
        
        logger.info(f"Comparison generated: {source1} vs {source2} for {product_name}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
