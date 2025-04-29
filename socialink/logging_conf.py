import logging
from logging.config import dictConfig

from socialink.config import DevConfig, config


def obfuscated(email: str, obfuscated_length: int) -> str:
    chars = email[:obfuscated_length]
    f, l = email.split("@")
    return chars + ("*" * (len(f) - obfuscated_length)) + "@" + l


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03dZ  %(levelname)-8s  %(correlation_id)s  %(name)s %(lineno)d  %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "socialink.log",
                    "maxBytes": 1024 * 1024,  # 1MB
                    "backupCount": 3,
                    "encoding": "utf8",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
            },
            "loggers": {
                "socialink": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO",
                },
                "databases": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
            },
        }
    )
