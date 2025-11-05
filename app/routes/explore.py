from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.models.schemas import (
    ExploreDashboardResponse, HeatmapCell, ProductPerformanceRow, CardSummary
)
from app.services.data_loader import get_data
from app.services.filters import apply_filters, get_applied_filters
from app.services.analysis import (
    generate_heatmap_data, generate_product_performance, generate_card_summaries
)
from app.services.metrics import calculate_nrs_per_row
from app.core.logger import logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/explore", response_model=ExploreDashboardResponse)
async def get_explore_dashboard(
    product: Optional[str] = Query(None, description="Comma-separated product names"),
    source: Optional[str] = Query(None, description="Comma-separated source names"),
    rank_min: int = Query(1, ge=1, le=5),
    rank_max: int = Query(5, ge=1, le=5),
    has_price: bool = Query(False),
    has_delivery: bool = Query(False),
):
    """
    Filtered analysis: heatmap + product performance + cards.
    """
    try:
        df = get_data()
        
        # Apply filters
        filtered_df = apply_filters(
            df,
            product=product,
            source=source,
            rank_min=rank_min,
            rank_max=rank_max,
            has_price=has_price,
            has_delivery=has_delivery,
        )
        
        if len(filtered_df) == 0:
            logger.warning("No data after applying filters")
            return ExploreDashboardResponse(
                heatmap_data=[],
                product_performance=[],
                cards=[],
                applied_filters=get_applied_filters(product, source, rank_min, rank_max, has_price, has_delivery),
                metadata={"rows_returned": 0},
            )
        
        # Add NRS column
        filtered_df = calculate_nrs_per_row(filtered_df)
        
        # Generate visualizations
        heatmap_data = [HeatmapCell(**hm) for hm in generate_heatmap_data(filtered_df)]
        product_perf = [
            ProductPerformanceRow(**pp) for pp in generate_product_performance(filtered_df)
        ]
        cards = [CardSummary(**c) for c in generate_card_summaries(filtered_df)]
        
        # Metadata
        metadata = {
            "rows_returned": len(filtered_df),
            "unique_products": filtered_df['product_name'].nunique(),
            "unique_sources": filtered_df['source_normalized'].nunique(),
            "unique_prompts": filtered_df['prompt_id'].nunique(),
        }
        
        response = ExploreDashboardResponse(
            heatmap_data=heatmap_data,
            product_performance=product_perf,
            cards=cards,
            applied_filters=get_applied_filters(product, source, rank_min, rank_max, has_price, has_delivery),
            metadata=metadata,
        )
        
        logger.info(f"Explore dashboard generated with {len(filtered_df)} rows")
        return response
    
    except Exception as e:
        logger.error(f"Error in explore dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
