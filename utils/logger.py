from rich.logging import RichHandler
import logging
import logging.handlers
from config import MAX_LOG_SIZE, ROTATE_LOGS, LOG_FILE

# Setup LOGGER
logger = logging.getLogger("Watch2GetherBot")
# Set the logger level
logger.setLevel(logging.DEBUG)

# Console handler with formatting
console_handler = RichHandler(rich_tracebacks=True)
console_handler.setFormatter(logging.Formatter('{name}: {message}', style='{'))
logger.addHandler(console_handler)

# File handler for persistent logs
file_handler = logging.handlers.RotatingFileHandler(
    filename=LOG_FILE,
    encoding='utf-8',
    maxBytes=MAX_LOG_SIZE,  # 32 MiB
    backupCount=ROTATE_LOGS,
)
file_handler.setFormatter(logging.Formatter('{name}: {message}', style='{'))
logger.addHandler(file_handler)

# Configure discord.py root logger to propagate logs
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.DEBUG)
discord_logger.handlers = []  # Clear default handlers
discord_logger.addHandler(console_handler)
discord_logger.addHandler(file_handler)
discord_logger.propagate = True  # Ensure sub-loggers (e.g., discord.gateway) propagate
logging.getLogger("discord.http").setLevel(logging.INFO)  # Reduce HTTP verbosity
logging.getLogger("discord.gateway").setLevel(logging.INFO)  # Reduce Gateway verbosity