"""
Enhanced logging configuration for production-ready logging.
"""
import logging
import logging.config
import sys
from typing import Dict, Any
from pathlib import Path

from app.core.config import settings


class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to log records."""
    
    def filter(self, record):
        # Try to get correlation ID from context (will be set by middleware)
        correlation_id = getattr(record, 'correlation_id', None)
        if not correlation_id:
            correlation_id = 'no-correlation'
        record.correlation_id = correlation_id
        return True


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment."""
    
    # Determine log level
    log_level = getattr(settings, 'log_level', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "correlation_id": "%(correlation_id)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'filters': {
            'correlation': {
                '()': CorrelationFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filters': ['correlation'],
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filters': ['correlation'],
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filters': ['correlation'],
                'filename': 'logs/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'access_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filters': ['correlation'],
                'filename': 'logs/access.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # root logger
                'level': log_level,
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'app': {
                'level': log_level,
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'INFO',
                'handlers': ['access_file'],
                'propagate': False
            },
            'uvicorn.error': {
                'level': 'ERROR',
                'handlers': ['console', 'error_file'],
                'propagate': False
            },
            # Third-party loggers
            'discord': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'httpx': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'weaviate': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        }
    }
    
    return config


def setup_logging():
    """Setup logging configuration."""
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Set up correlation ID context (will be enhanced by middleware)
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


def log_with_correlation(logger: logging.Logger, level: str, message: str, correlation_id: str = None, **kwargs):
    """Log a message with correlation ID."""
    extra = {'correlation_id': correlation_id or 'no-correlation'}
    extra.update(kwargs)
    
    getattr(logger, level.lower())(message, extra=extra)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_info(self, message: str, correlation_id: str = None, **kwargs):
        """Log info message with correlation ID."""
        log_with_correlation(self.logger, 'info', message, correlation_id, **kwargs)
    
    def log_warning(self, message: str, correlation_id: str = None, **kwargs):
        """Log warning message with correlation ID."""
        log_with_correlation(self.logger, 'warning', message, correlation_id, **kwargs)
    
    def log_error(self, message: str, correlation_id: str = None, **kwargs):
        """Log error message with correlation ID."""
        log_with_correlation(self.logger, 'error', message, correlation_id, **kwargs)
    
    def log_debug(self, message: str, correlation_id: str = None, **kwargs):
        """Log debug message with correlation ID."""
        log_with_correlation(self.logger, 'debug', message, correlation_id, **kwargs)


# Performance monitoring decorator
def log_performance(func_name: str = None):
    """Decorator to log function performance."""
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            logger = logging.getLogger(name)
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Function executed successfully in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function failed after {execution_time:.4f}s: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            logger = logging.getLogger(name)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Function executed successfully in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function failed after {execution_time:.4f}s: {str(e)}")
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator