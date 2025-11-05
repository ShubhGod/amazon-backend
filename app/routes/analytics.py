from fastapi import APIRouter, Query, HTTPException
from app.services.analytics import get_category_winners, get_marketplace_score_sum

router = APIRouter(prefix="/dashboard", tags=["Analytics"])

@router.get("/analytics")
async def analytics_heatmap():
    """
    Returns heatmap data for analytics dashboard.
    """
    return get_category_winners()

@router.get("/analytics/marketshare")
async def marketplace_market_share(
    product: str = Query(..., description="Product category to get marketplace share for")
):
    """
    Get marketplace score sums for given product category for pie/donut chart.
    """
    try:
        data = get_marketplace_score_sum(product)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
