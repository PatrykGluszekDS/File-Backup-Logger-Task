"""
Minimal Tkinter front-end for File Backup Logger.
Step-4 version – tested on Python 3.9/3.10.
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from typing import Optional
from pathlib import Path

from .backup import BackupManager
from .config import Config


class BackupApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("File-Backup-Logger")

        # ------------ state ------------
        self.cfg = Config()
        self.bm = BackupManager(config=self.cfg)
        self.src_path: Optional[Path] = None
        self.dst_root: Optional[Path] = None
        self.compress = tk.BooleanVar(value=self.cfg.get("compress", False))

        # ------------ UI ------------
        self._build_widgets()

    # ------------------------------------------------------------------ #
    #                            Widgets                                  #
    # ------------------------------------------------------------------ #
    def _build_widgets(self) -> None:
        pad_opts = {"padx": 10, "pady": 8}        # renamed 🔹

        # Source selector
        src_frame = ttk.Frame(self)
        src_frame.pack(fill="x", **pad_opts)

        ttk.Label(src_frame, text="Source folder:").pack(side="left")
        self.src_lbl = ttk.Label(src_frame, text="— none selected —")
        self.src_lbl.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(
            src_frame, text="Browse…", command=self._choose_src
        ).pack(side="right")

        # Destination selector
        dst_frame = ttk.Frame(self)
        dst_frame.pack(fill="x", **pad_opts)

        ttk.Label(dst_frame, text="Backup root:").pack(side="left")
        self.dst_lbl = ttk.Label(
            dst_frame,
            text=str(self.cfg.get("backup_root", "backups")),
        )
        self.dst_lbl.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(
            dst_frame, text="Change…", command=self._choose_dst
        ).pack(side="right")

        # ZIP checkbox
        ttk.Checkbutton(
            self,
            text="Store as .zip archive",
            variable=self.compress,
        ).pack(anchor="w", **pad_opts)

        # Progress bar
        self.prog = ttk.Progressbar(self, mode="indeterminate")
        self.prog.pack(fill="x", **pad_opts)

        # Action button
        ttk.Button(
            self, text="Back Up Now", command=self._start_backup
        ).pack(pady=(0, 12))

    # ------------------------------------------------------------------ #
    #                           Callbacks                                 #
    # ------------------------------------------------------------------ #
    def _choose_src(self) -> None:
        folder = filedialog.askdirectory(title="Select folder to back up")
        if folder:
            self.src_path = Path(folder)
            self.src_lbl.config(text=str(self.src_path))

    def _choose_dst(self) -> None:
        folder = filedialog.askdirectory(
            title="Select destination root (optional)",
            initialdir=str(
                Path(self.cfg.get("backup_root", "backups")).expanduser()
            ),
        )
        if folder:
            self.dst_root = Path(folder)
            self.dst_lbl.config(text=str(self.dst_root))

    # --------------------------------------------------------------
    def _start_backup(self) -> None:
        if not self.src_path:
            messagebox.showerror("Missing source", "Please choose a source folder.")
            return

        # persist the user's compression preference
        self.cfg.set("compress", self.compress.get())

        self.prog.start(10)
        self.attributes("-disabled", True)  # freeze UI while working

        thread = threading.Thread(target=self._do_backup, daemon=True)
        thread.start()

    def _do_backup(self) -> None:
        try:
            self.bm.copy_folder(
                src=self.src_path,
                dst_root=self.dst_root or self.cfg.get("backup_root", "backups"),
                compress=self.compress.get(),
            )
            self.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", f"Backup completed:\n{self.src_path}"
                ),
            )
        except Exception as exc:  # noqa: BLE001
            self.after(
                0,
                lambda: messagebox.showerror("Backup failed", str(exc)),
            )
        finally:
            self.after(0, self._reset_ui)

    def _reset_ui(self) -> None:
        self.prog.stop()
        self.attributes("-disabled", False)


# ---------------------------------------------------------------------- #
#  CLI entry-point                                                       #
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    app = BackupApp()
    app.mainloop()
