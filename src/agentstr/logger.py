import logging
import os


class Logger:
    """Cache and configure :pyclass:`logging.Logger` instances by *name*."""

    _instances: dict[str, "Logger"] = {}

    def __new__(cls, name: str | None = None):  # noqa: D401
        key = name or __name__
        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)
        return cls._instances[key]

    def __init__(self, name: str | None = None):  # noqa: D401
        if hasattr(self, "_initialized") and self._initialized:  # already configured
            return
        self.name = name or __name__
        self.logger = logging.getLogger(self.name)
        self._setup_logger()
        self._initialized = True

    def _setup_logger(self):
        """Configure the logger with the log level from environment variable."""
        # Default log level if not specified in environment
        default_level = logging.INFO

        # Get log level from environment variable
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, default_level)

        # Configure the logger
        self.logger.setLevel(log_level)

        # Create console handler and set level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        ch.setFormatter(formatter)

        # Remove any existing handlers to avoid duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Add the handler to the logger
        self.logger.addHandler(ch)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

# Create a default logger instance
def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: The name of the logger. If None, uses the module's name.

    Returns:
        A configured logging.Logger instance.
    """
    return Logger(name).get_logger()
