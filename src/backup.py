from __future__ import annotations
import shutil
import datetime as _dt
from pathlib import Path
from typing import Union

from .logger import LogWriter   # NEW 🔹


class BackupManager:
    """High-level orchestrator for all backup operations."""

    def __init__(self, logger: LogWriter | None = None) -> None:   # NEW 🔹
        self.log = logger or LogWriter()

    # ------------
    # PUBLIC API
    # ------------
    def copy_folder(
        self,
        src: Union[str, Path],
        dst_root: Union[str, Path] = "backups",
        version: str | None = None,        # NEW 🔹
    ) -> Path:
        """
        Copy *src* directory into *dst_root* under a name that embeds
        today's date and an optional version string.

        Example: MyApp_2024-05-04_v1.2.3
        """
        src_path = Path(src).expanduser().resolve()
        if not src_path.is_dir():
            msg = f"Source folder not found: {src_path}"
            self.log.error(msg)
            raise FileNotFoundError(msg)

        dst_root = Path(dst_root).expanduser().resolve()
        dst_root.mkdir(parents=True, exist_ok=True)

        dst_path = self._make_dst_path(src_path, dst_root, version)

        try:
            shutil.copytree(src_path, dst_path)
            self.log.info(f"Copied {src_path} → {dst_path}")
        except PermissionError as exc:
            self.log.error(f"PermissionError: {exc}")
            raise
        except shutil.Error as exc:
            self.log.error(f"shutil.Error: {exc}")
            raise

        return dst_path

    # ------------
    # PRIVATE HELPERS
    # ------------
    def _make_dst_path(
        self,
        src_path: Path,
        dst_root: Path,
        version: str | None,
    ) -> Path:
        date_part = _dt.datetime.now().strftime("%Y-%m-%d")
        ver_part = f"_v{version}" if version else ""
        return dst_root / f"{src_path.name}_{date_part}{ver_part}"


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Copy a folder with timestamp.")
    parser.add_argument("src", help="Source directory to back up")
    parser.add_argument(
        "dst_root",
        nargs="?",
        default="backups",
        help="Folder in which to create the backup copy (default: backups/)",
    )
    parser.add_argument(
        "-v", "--version",
        help="Version string to embed in the backup name (e.g. 1.2.3)",
    )
    args = parser.parse_args()

    bm = BackupManager()
    try:
        bm.copy_folder(args.src, args.dst_root, version=args.version)
    except Exception as exc:
        print(f"✖ Error: {exc}", file=sys.stderr)
        sys.exit(1)