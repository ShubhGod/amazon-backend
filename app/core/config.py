import os
from pathlib import Path
from logging import INFO

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EXCEL_FILE = DATA_DIR / "sheet.xlsx"

# API Config
API_TITLE = "AEO/GEO Dashboard API"
API_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "app.log"

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

# Caching
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

# Data Constants
MAX_RANK = 5
DELIVERY_THRESHOLDS = {
    "strong": (0, 1),      # 0-1 days → 1.0
    "medium": (2, 3),      # 2-3 days → 0.7
    "weak": (4, 7),        # 4-7 days → 0.3
}
PRICE_PERCENTILE_THRESHOLD = 25  # p25 for competitiveness

# Column Names
COLUMNS = {
    "product": "product_name",
    "prompt": "prompt_id",
    "rank": "rank",
    "source": "source_normalized",
    "price": "price",
    "currency": "price_currency",
    "delivery_fee": "delivery_fee",
    "delivery_days": "delivery_days",
    "card_id": "card_id",
    "source_raw": "source",
    "extra": "extra",
}

# Invalid/Missing Data Markers
INVALID_PRICE = -1
INVALID_DELIVERY = -1
INVALID_CURRENCY = "-1"
