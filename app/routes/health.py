from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import HealthResponse
from app.services.data_loader import get_data, get_stats
from app.core.logger import logger

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check: data status + quality metrics.
    """
    try:
        df = get_data()
        stats = get_stats()
        
        # Calculate data quality
        data_quality = {
            "price_coverage": stats.get("price_completeness", 0),
            "delivery_coverage": stats.get("delivery_completeness", 0),
            "overall_completeness": round(
                (stats.get("price_completeness", 0) + stats.get("delivery_completeness", 0)) / 2,
                2
            ),
        }
        
        response = HealthResponse(
            status="ok",
            data_loaded=True,
            total_rows=stats.get("total_rows", 0),
            unique_prompts=stats.get("unique_prompts", 0),
            data_freshness=datetime.now(),
            data_quality=data_quality,
        )
        
        logger.info("Health check passed")
        return response
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_cache():
    """
    Force reload data cache.
    """
    try:
        from services.data_loader import reload_data
        reload_data()
        logger.info("Cache reloaded")
        return {"status": "reloaded", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Reload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
