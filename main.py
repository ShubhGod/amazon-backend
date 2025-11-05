from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time

from app.core.config import API_TITLE, API_VERSION, CORS_ORIGINS, DEBUG
from app.core.logger import logger
from app.routes import router as api_router

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AEO/GEO Dashboard API - Analytics for Answer & Generative Engine Optimization",
    debug=DEBUG,
)

# ============ MIDDLEWARE ============

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request/Response Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing."""
    
    start_time = time.time()
    request_id = request.headers.get("x-request-id", f"req-{int(time.time() * 1000)}")
    
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"[{request_id}] Unhandled exception: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    
    process_time = time.time() - start_time
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} | "
        f"Status: {response.status_code} | Duration: {process_time:.2f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ============ INCLUDE API ROUTES ============
app.include_router(api_router, prefix="/api")

# ============ STARTUP/SHUTDOWN EVENTS ============

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info(f"{'='*60}")
    logger.info(f"AEO/GEO Dashboard API Starting...")
    logger.info(f"Version: {API_VERSION}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info(f"CORS Origins: {CORS_ORIGINS}")
    logger.info(f"{'='*60}")
    
    try:
        from app.services.data_loader import load_excel
        load_excel()
        logger.info("✓ Data loaded successfully on startup")
    except Exception as e:
        logger.error(f"✗ Failed to load data on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("AEO/GEO Dashboard API Shutting down...")
    logger.info(f"{'='*60}")

# ============ ROOT ENDPOINTS ============

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint - API info."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "openapi": "/openapi.json",
    }

@app.get("/info", tags=["Info"])
async def info():
    """API information."""
    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "description": "Analytics dashboard for AEO and GEO",
        "endpoints": {
            "home": "/api/dashboard/home",
            "explore": "/api/dashboard/explore",
            "compare": "/api/dashboard/compare",
            "prompt_detail": "/api/prompt/{prompt_id}",
            "health": "/api/health",
            "reload": "/api/reload",
        },
    }

# ============ RUN ============
# Use: uvicorn main:app --reload --host 0.0.0.0 --port 8000
