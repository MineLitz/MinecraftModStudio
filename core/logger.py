"""
Centralized logging for Minecraft Mod Studio.
Writes to resources/logs/mms.log and exposes log functions.
"""
import logging
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR  = os.path.join(BASE_DIR, "resources", "logs")
LOG_FILE = os.path.join(LOG_DIR, "mms.log")

os.makedirs(LOG_DIR, exist_ok=True)

# File handler — keeps last 500 KB, then rotates
from logging.handlers import RotatingFileHandler

_logger = logging.getLogger("MMS")
_logger.setLevel(logging.DEBUG)

if not _logger.handlers:
    _fh = RotatingFileHandler(
        LOG_FILE, maxBytes=500_000, backupCount=2, encoding="utf-8"
    )
    _fh.setLevel(logging.DEBUG)
    _fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _logger.addHandler(_fh)

    # Also mirror to stderr so the run.bat console shows errors
    _sh = logging.StreamHandler(sys.stderr)
    _sh.setLevel(logging.WARNING)
    _sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(_sh)

_logger.info("="*60)
_logger.info(f"Minecraft Mod Studio started — {datetime.now()}")
_logger.info("="*60)


def debug(msg: str):   _logger.debug(msg)
def info(msg: str):    _logger.info(msg)
def warning(msg: str): _logger.warning(msg)
def error(msg: str):   _logger.error(msg)
def critical(msg: str):_logger.critical(msg)

def exception(msg: str):
    """Log an exception with full traceback."""
    _logger.exception(msg)

def get_log_path() -> str:
    return LOG_FILE
