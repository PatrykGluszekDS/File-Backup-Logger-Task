"""
Core backup logic for File Backup Logger.
"""
from __future__ import annotations
import shutil
import datetime as _dt
from pathlib import Path
from typing import Union 


class BackupManager:
    """High-level orchestrator for all backup operations."""

    def copy_folder(self, src: Union[str, Path], dst_root: Union[str, Path]) -> Path:
        """
        Copy *src* directory into *dst_root*.

        Returns the Path to the newly created backup folder.
        Raises:
            FileNotFoundError - if *src* does not exist or is not a directory.
            shutil.Error      - bubbled-up copytree issues.
        """
        src_path = Path(src).expanduser().resolve()
        if not src_path.is_dir():
            raise FileNotFoundError(f"Source folder not found: {src_path}")

        timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        dst_root = Path(dst_root).expanduser().resolve()
        dst_path = dst_root / f"{src_path.name}_{timestamp}"

        # create the destination root if it doesn’t yet exist
        dst_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(src_path, dst_path)

        # temporary feedback until we wire-in a proper logger
        print(f"✔ Copied {src_path} → {dst_path}")

        return dst_path