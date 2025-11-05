from fastapi import APIRouter
from app.routes import home, explore, compare, prompt_detail, health, analytics

router = APIRouter()

# Include all route routers
router.include_router(health.router)
router.include_router(home.router)
router.include_router(explore.router)
router.include_router(compare.router)
router.include_router(prompt_detail.router)
router.include_router(analytics.router)