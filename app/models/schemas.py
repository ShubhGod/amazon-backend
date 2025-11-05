from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============ Home Dashboard ============
class KPIMetrics(BaseModel):
    gsov_overall: float = Field(..., ge=0, le=1)
    gsov_by_platform: Dict[str, float]
    avg_rank_position: float
    rank_presence_score: float = Field(..., ge=0, le=10)
    price_competitiveness_rate: float = Field(..., ge=0, le=1)
    delivery_strength_score: float = Field(..., ge=0, le=1)
    prompt_coverage_rate: float = Field(..., ge=0, le=1)

class LossReason(BaseModel):
    reason: str
    occurrences: int
    weight: float

class SourceBreakdown(BaseModel):
    source: str
    cards: int
    avg_rank: float
    price_competitiveness: float

class HomeDashboardResponse(BaseModel):
    kpis: KPIMetrics
    loss_reasons: List[LossReason]
    source_breakdown: List[SourceBreakdown]
    metadata: Dict[str, Any]

# ============ Explore Dashboard ============
class HeatmapCell(BaseModel):
    product: str
    source: str
    avg_nrs: float
    card_count: int

class ProductPerformanceRow(BaseModel):
    product: str
    gsov: float
    avg_rank: float
    prompt_count: int
    price_gap_pct: Optional[float]
    delivery_gap_days: Optional[int]

class CardSummary(BaseModel):
    card_id: str
    product_name: str
    rank: int
    source: str
    price: Optional[float]
    currency: Optional[str]
    delivery_days: Optional[int]
    delivery_fee: Optional[float]

class ExploreDashboardResponse(BaseModel):
    heatmap_data: List[HeatmapCell]
    product_performance: List[ProductPerformanceRow]
    cards: List[CardSummary]
    applied_filters: Dict[str, Any]
    metadata: Dict[str, Any]

# ============ Compare Dashboard ============
class ComparisonMetric(BaseModel):
    metric: str
    source1_value: float
    source2_value: float
    gap: float
    gap_pct: float
    winner: str  # "source1", "source2", "tie"

class WinLoseChip(BaseModel):
    factor: str
    status: str  # "win", "lose", "neutral"
    value: str  # e.g., "-12%", "+3 days"
    contribution: float

class ComparisonResponse(BaseModel):
    product_name: str
    source1: str
    source2: str
    metrics: List[ComparisonMetric]
    win_lose_chips: List[WinLoseChip]
    metadata: Dict[str, Any]

# ============ Prompt Detail ============
class PromptCard(BaseModel):
    card_id: str
    product_name: str
    rank: int
    source: str
    price: Optional[float]
    currency: Optional[str]
    delivery_days: Optional[int]
    delivery_fee: Optional[float]
    extra: Optional[List[str]]

class PriceStats(BaseModel):
    min_price: float
    max_price: float
    median_price: float
    your_price: Optional[float]
    your_percentile: Optional[float]

class PromptDetailResponse(BaseModel):
    prompt_id: str
    product_name: str
    prompt_text: str
    cards: List[PromptCard]
    price_stats: PriceStats
    metadata: Dict[str, Any]

# ============ Health Check ============
class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    total_rows: int
    unique_prompts: int
    data_freshness: datetime
    data_quality: Dict[str, float]
