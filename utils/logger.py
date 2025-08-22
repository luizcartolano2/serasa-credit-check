import logging
import sys
import json
import uuid
from flask import g, request


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for logging records.
    This formatter outputs log records in JSON format, including the log level,
    timestamp, message, and correlation ID if available.
    Attributes:
        datefmt (str): Format for the timestamp in the log records.

    Methods:
        format(record):
            Formats the log record as a JSON string.
    """
    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record as a JSON string.
        :param record: a logging.LogRecord instance containing the log information
        :return: a JSON string representation of the log record
        """
        log_record = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
            "correlation_id": getattr(g, "correlation_id", None),
        }
        return json.dumps(log_record)


# Initialize the logger for the credit check service
logger = logging.getLogger("credit_check")
logger.setLevel(logging.INFO)

# Create a stream handler that outputs to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)


def get_correlation_id() -> str:
    """
    Retrieves the correlation ID from the request headers or generates a new one if not present.
    :return: a string representing the correlation ID
    """
    if not hasattr(g, "correlation_id"):
        g.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    return g.correlation_id
