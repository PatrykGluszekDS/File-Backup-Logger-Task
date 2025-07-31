"""
Backup engine – Step 5 version
• Emits per-file progress via a callback
• Auto-bumps default_version in config.json on success
Compatible with Python 3.8+
"""

from __future__ import annotations

import datetime as _dt
import shutil
import zipfile
from pathlib import Path
from typing import Callable, List, Optional, Union

from .config import Config
from .logger import LogWriter


ProgressCB = Callable[[int, int], None]   # (done, total) → None


class BackupManager:
    def __init__(
        self,
        logger: Optional[LogWriter] = None,
        config: Optional[Config] = None,
    ) -> None:
        self.log = logger or LogWriter()
        self.cfg = config or Config()

    # ------------------------------------------------------------------ #
    #                              PUBLIC API                             #
    # ------------------------------------------------------------------ #
    def copy_folder(
        self,
        src: Union[str, Path],
        dst_root: Union[str, Path, None] = None,
        version: Optional[str] = None,
        compress: Optional[bool] = None,
        progress_cb: Optional[ProgressCB] = None,
    ) -> Path:
        """
        Copy *src* into *dst_root*.
        If *compress* is True, create a .zip.
        Emits incremental progress via *progress_cb* if provided.
        """
        compress = (
            compress if compress is not None else self.cfg.get("compress", False)
        )
        dst_root = Path(
            dst_root or self.cfg.get("backup_root", "backups")
        ).expanduser().resolve()

        version = version if version is not None else self.cfg.get("default_version")
        src_path = Path(src).expanduser().resolve()

        if not src_path.is_dir():
            msg = f"Source folder not found: {src_path}"
            self.log.error(msg)
            raise FileNotFoundError(msg)

        dst_root.mkdir(parents=True, exist_ok=True)
        dst_path = self._make_dst_path(src_path, dst_root, version, compress)

        # --- gather all files first so we know 'total' ---
        files: List[Path] = [f for f in src_path.rglob("*") if f.is_file()]
        total = len(files)
        if progress_cb:
            progress_cb(0, total)

        try:
            if compress:
                self._zip_with_progress(src_path, dst_path, files, progress_cb)
                self.log.info(f"ZIPPED {src_path} → {dst_path}")
            else:
                self._copy_with_progress(src_path, dst_path, files, progress_cb)
                self.log.info(f"Copied {src_path} → {dst_path}")
        except Exception:
            # do NOT bump version on failure
            raise

        # --- success ➜ bump version ---
        new_ver = self._bump_patch(version)
        self.cfg.set("default_version", new_ver)
        return dst_path

    # ------------------------------------------------------------------ #
    #                             INTERNALS                              #
    # ------------------------------------------------------------------ #
    def _copy_with_progress(
        self,
        src_dir: Path,
        dst_dir: Path,
        files: List[Path],
        progress_cb: Optional[ProgressCB],
    ) -> None:
        done = 0
        for file in files:
            target = dst_dir / file.relative_to(src_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
            done += 1
            if progress_cb:
                progress_cb(done, len(files))

    def _zip_with_progress(
        self,
        src_dir: Path,
        zip_path: Path,
        files: List[Path],
        progress_cb: Optional[ProgressCB],
    ) -> None:
        done = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                zf.write(file, file.relative_to(src_dir))
                done += 1
                if progress_cb:
                    progress_cb(done, len(files))

    # ----------------------------------------
    def _make_dst_path(
        self,
        src_path: Path,
        dst_root: Path,
        version: Optional[str],
        compress: bool,
    ) -> Path:
        date_part = _dt.datetime.now().strftime("%Y-%m-%d")
        ver_part = f"_v{version}" if version else ""
        suffix = ".zip" if compress else ""
        return dst_root / f"{src_path.name}_{date_part}{ver_part}{suffix}"

    @staticmethod
    def _bump_patch(ver: str) -> str:
        """
        Increment the last numeric component.
        '' ➜ '0.0.1'
        '2' ➜ '3'
        '1.4.9' ➜ '1.4.10'
        Non-numeric parts are preserved.
        """
        if not ver:
            return "0.0.1"
        parts = ver.split(".")
        for i in range(len(parts) - 1, -1, -1):
            if parts[i].isdigit():
                parts[i] = str(int(parts[i]) + 1)
                return ".".join(parts)
        # no numeric segment found
        return ver
