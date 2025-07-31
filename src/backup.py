from __future__ import annotations
import shutil
import datetime as _dt
from pathlib import Path
from typing import Union
import zipfile
import tempfile

from .logger import LogWriter
from .config import Config


class BackupManager:
    """High-level orchestrator for all backup operations."""

    def __init__(self, logger: LogWriter | None = None, config: Config | None = None) -> None:
        self.log = logger or LogWriter()
        self.cfg = config or Config()

    def copy_folder(
        self,
        src: Union[str, Path],
        dst_root: Union[str, Path] | None = None,
        version: str | None = None,
        compress: bool | None = None,          # NEW 🔹
    ) -> Path:
        """
        Copy *src* into *dst_root*.
        If *compress* is True, make a .zip instead of a folder.
        """
        compress = (
            compress if compress is not None else self.cfg.get("compress", False)
        )
        dst_root = dst_root or self.cfg.get("backup_root", "backups")
        version = version if version is not None else self.cfg.get("default_version")

        src_path = Path(src).expanduser().resolve()
        if not src_path.is_dir():
            msg = f"Source folder not found: {src_path}"
            self.log.error(msg)
            raise FileNotFoundError(msg)

        dst_root = Path(dst_root).expanduser().resolve()
        dst_root.mkdir(parents=True, exist_ok=True)

        dst = self._make_dst_path(src_path, dst_root, version, compress)

        if compress:
            self._zip_folder(src_path, dst)
            self.log.info(f"ZIPPED {src_path} → {dst}")
        else:
            shutil.copytree(src_path, dst)
            self.log.info(f"Copied {src_path} → {dst}")

        return dst

    

    # --------------------
    # PRIVATE HELPERS
    # --------------------
    def _make_dst_path(
        self,
        src_path: Path,
        dst_root: Path,
        version: str | None,
        compress: bool,
    ) -> Path:
        date_part = _dt.datetime.now().strftime("%Y-%m-%d")
        ver_part = f"_v{version}" if version else ""
        suffix = ".zip" if compress else ""
        name = f"{src_path.name}_{date_part}{ver_part}{suffix}"
        return dst_root / name

    def _zip_folder(self, src_dir: Path, zip_path: Path) -> None:
        """Recursively write *src_dir* into *zip_path*."""
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in src_dir.rglob("*"):
                # write relative paths to keep inside-zip structure clean
                zf.write(file, file.relative_to(src_dir))


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Copy a folder with timestamp.")
    parser.add_argument(
        "-z", "--zip",
        action="store_true",
        help="Store backup as a compressed .zip instead of a folder",
    )
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
        bm.copy_folder(
        args.src,
        args.dst_root,
        version=args.version,
        compress=args.zip,
    )
    except Exception as exc:
        print(f"✖ Error: {exc}", file=sys.stderr)
        sys.exit(1)