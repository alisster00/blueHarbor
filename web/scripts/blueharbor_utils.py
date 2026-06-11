"""
blueharbor_utils - Internal utility library for BlueHarbor scripts.
Version : 0.3.1
Do not distribute outside BlueHarbor Solutions.
"""

import datetime
import logging
import os

LOG_FILE = "/var/log/blueharbor/utils.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger("blueharbor_utils")

def log(message: str, level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    _logger.log(lvl, message)

    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as fh:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fh.write(f"[{ts}] [{level}] {message}\n")
    except OSError:
        pass

def notify(recipient: str, subject: str, body: str) -> None:
    log(f"NOTIFY → {recipient} | {subject} | {body}")
