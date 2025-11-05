from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import HomeDashboardResponse, KPIMetrics, LossReason, SourceBreakdown
from app.services.data_loader import get_data
from app.services.metrics import (
    calculate_global_metrics, calculate_loss_reasons, calculate_source_breakdown
)
from app.core.logger import logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/home", response_model=HomeDashboardResponse)
async def get_home_dashboard():
    """
    Executive summary: KPIs + loss reasons + source breakdown.
    """
    try:
        df = get_data()
        
        # Calculate all KPIs
        kpis_dict = calculate_global_metrics(df)
        kpis = KPIMetrics(**kpis_dict)
        
        # Loss reasons
        loss_reasons = [LossReason(**lr) for lr in calculate_loss_reasons(df)]
        
        # Source breakdown
        source_breakdown = [
            SourceBreakdown(**sb) for sb in calculate_source_breakdown(df)
        ]
        
        # Metadata
        metadata = {
            "total_prompts": df['prompt_id'].nunique(),
            "total_cards": len(df),
            "data_freshness": datetime.now().isoformat(),
            "rows_analyzed": len(df),
        }
        
        response = HomeDashboardResponse(
            kpis=kpis,
            loss_reasons=loss_reasons,
            source_breakdown=source_breakdown,
            metadata=metadata,
        )
        
        logger.info("Home dashboard generated successfully")
        return response
    
    except Exception as e:
        logger.error(f"Error in home dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
