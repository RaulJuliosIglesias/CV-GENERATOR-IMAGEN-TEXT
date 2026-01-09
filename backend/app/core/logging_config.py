"""
Enhanced Logging Configuration
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
ERROR_LOG = LOGS_DIR / "error.log"
APP_LOG = LOGS_DIR / "app.log"
ACCESS_LOG = LOGS_DIR / "access.log"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Error logger
error_handler = RotatingFileHandler(
    ERROR_LOG,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(detailed_formatter)

# App logger
app_handler = RotatingFileHandler(
    APP_LOG,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(simple_formatter)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)

# Configure app logger
app_logger = logging.getLogger("app")
app_logger.addHandler(app_handler)
app_logger.addHandler(console_handler)
app_logger.addHandler(error_handler)
app_logger.setLevel(logging.INFO)

# Configure error logger
error_logger = logging.getLogger("error")
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

# Access logger (for API requests)
access_logger = logging.getLogger("access")
access_handler = RotatingFileHandler(
    ACCESS_LOG,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
access_handler.setFormatter(simple_formatter)
access_logger.addHandler(access_handler)
access_logger.setLevel(logging.INFO)

def log_request(request, response_time: float = None):
    """Log API request."""
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else "unknown",
        "status": getattr(response_time, "status_code", None) if hasattr(response_time, "status_code") else None
    }
    if response_time:
        log_data["response_time"] = f"{response_time:.3f}s"
    
    access_logger.info(f"API Request: {log_data}")

def log_error(error: Exception, context: dict = None):
    """Log error with context."""
    error_logger.error(
        f"Error: {str(error)}",
        exc_info=True,
        extra={"context": context or {}}
    )

def log_info(message: str, context: dict = None):
    """Log info message."""
    app_logger.info(message, extra={"context": context or {}})
