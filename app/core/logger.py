import logging
import logging.handlers
from pathlib import Path
from app.core.config import LOG_LEVEL, LOG_FILE

# Create logs directory
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Setup logger
logger = logging.getLogger("aeo_geo_dashboard")
logger.setLevel(LOG_LEVEL)

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5_000_000, backupCount=5
)
file_handler.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
