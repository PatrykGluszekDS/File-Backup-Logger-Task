"""
Lightweight wrapper around Python's ``logging`` module.
"""

import logging
from pathlib import Path
from typing import Union


class LogWriter:
    def __init__(self, log_dir: Union[str, Path] = "logs") -> None:
        log_dir = Path(log_dir).expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "backup.log"

        # Basic one-liner configuration (will expand later)
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
        self.logger = logging.getLogger("FileBackupLogger")

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)
