"""Logging setup

Sets up and defiens the logger for the compiler.
"""

# Stdlib imports
import logging

logger = logging.getLogger("penguin")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Forhindre duplikering af handleres, hvis denne fil importeres flere gange
if not logger.hasHandlers():
    logger.addHandler(console_handler)
