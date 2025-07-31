import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union


class LogWriter:
    """Create one rotating file logger; expose .info() / .error()."""

    def __init__(
        self,
        log_dir: Union[str, Path] = "logs",
        max_bytes: int = 512 * 1024,     # 512 KB per file
        backup_count: int = 5,           # keep last 5 logs
    ) -> None:
        log_dir = Path(log_dir).expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "backup.log"

        self.logger = logging.getLogger("FileBackupLogger")
        self.logger.setLevel(logging.INFO)

        # -- File handler (rotates)
        file_h = RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count
        )
        file_h.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        # -- Console handler
        console_h = logging.StreamHandler()
        console_h.setFormatter(
            logging.Formatter("▶ %(message)s")
        )

        # Attach only once (avoid dupes if LogWriter is re-imported)
        if not self.logger.handlers:
            self.logger.addHandler(file_h)
            self.logger.addHandler(console_h)

    # Convenience passthroughs
    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)