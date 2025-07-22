import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from contextvars import ContextVar
import uuid

# Context variable to store request ID for correlation
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class RequestIdFilter(logging.Filter):
    """Filter to add request ID to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

def setup_logger(name: str = "hospital_scheduler") -> logging.Logger:
    """Set up and configure the application logger"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    json_formatter = StructuredFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(RequestIdFilter())
    
    # File handler (INFO and above)
    file_handler = logging.FileHandler(logs_dir / "app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(RequestIdFilter())
    
    # Error file handler (ERROR and above)
    error_handler = logging.FileHandler(logs_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(RequestIdFilter())
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str = "hospital_scheduler") -> logging.Logger:
    """Get the configured logger instance"""
    return logging.getLogger(name)

def set_request_id(request_id: str) -> None:
    """Set the request ID for correlation across logs"""
    request_id_var.set(request_id)

def get_request_id() -> Optional[str]:
    """Get the current request ID"""
    return request_id_var.get()

def log_with_extra(logger: logging.Logger, level: int, message: str, **extra_fields: Any) -> None:
    """Log a message with extra structured fields"""
    record = logger.makeRecord(
        logger.name, level, "", 0, message, (), None
    )
    record.extra_fields = extra_fields
    logger.handle(record)

# Create default logger instance
logger = setup_logger()

# Convenience functions for common logging patterns
def log_request(method: str, path: str, status_code: int, duration_ms: float, user_id: Optional[str] = None) -> None:
    """Log HTTP request details"""
    extra_fields = {
        "event_type": "http_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    if user_id:
        extra_fields["user_id"] = user_id
    
    level = logging.INFO if status_code < 400 else logging.WARNING
    log_with_extra(logger, level, f"{method} {path} - {status_code} ({duration_ms:.2f}ms)", **extra_fields)

def log_database_operation(operation: str, table: str, duration_ms: float, success: bool, error: Optional[str] = None) -> None:
    """Log database operation details"""
    extra_fields = {
        "event_type": "database_operation",
        "operation": operation,
        "table": table,
        "duration_ms": duration_ms,
        "success": success,
    }
    if error:
        extra_fields["error"] = error
    
    level = logging.INFO if success else logging.ERROR
    log_with_extra(logger, level, f"DB {operation} on {table} - {'SUCCESS' if success else 'FAILED'}", **extra_fields)

def log_business_rule(rule_name: str, details: Dict[str, Any], success: bool) -> None:
    """Log business rule execution"""
    extra_fields = {
        "event_type": "business_rule",
        "rule_name": rule_name,
        "success": success,
        **details
    }
    
    level = logging.INFO if success else logging.WARNING
    log_with_extra(logger, level, f"Business rule '{rule_name}' - {'PASSED' if success else 'FAILED'}", **extra_fields)

def log_schedule_generation(schedule_type: str, week_start: str, employee_count: int, success: bool, error: Optional[str] = None) -> None:
    """Log schedule generation events"""
    extra_fields = {
        "event_type": "schedule_generation",
        "schedule_type": schedule_type,
        "week_start": week_start,
        "employee_count": employee_count,
        "success": success,
    }
    if error:
        extra_fields["error"] = error
    
    level = logging.INFO if success else logging.ERROR
    log_with_extra(logger, level, f"Schedule generation {schedule_type} for {week_start} - {'SUCCESS' if success else 'FAILED'}", **extra_fields) 