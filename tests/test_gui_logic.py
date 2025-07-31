from pathlib import Path
import shutil, tempfile
from src.gui import BackupApp

_TMP = Path(tempfile.gettempdir())

def test_app_launches():
    # Just ensure Tk window can be created/destroyed headless
    app = BackupApp()
    app.update()       # process Tk events once
    app.destroy()

def test_backup_via_gui_logic():
    # Use GUI’s internal BackupManager but bypass the real dialog
    dummy_src = _TMP / "dummy_src_gui"
    if dummy_src.exists():
        shutil.rmtree(dummy_src)
    (dummy_src / "sub").mkdir(parents=True)
    (dummy_src / "file.txt").write_text("hi")

    app = BackupApp()
    app.src_path = dummy_src
    dst = app.bm.copy_folder(dummy_src, dst_root=_TMP, compress=False)

    try:
        assert dst.is_dir()
        assert (dst / "file.txt").exists()
    finally:
        shutil.rmtree(dst, ignore_errors=True)
        app.destroy()
