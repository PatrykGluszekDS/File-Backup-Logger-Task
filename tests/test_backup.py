from pathlib import Path
import shutil, tempfile
from src.backup import BackupManager

_TMP = Path(tempfile.gettempdir())

def _make_dummy_tree() -> Path:
    root = _TMP / "dummy_src"
    if root.exists():
        shutil.rmtree(root)
    (root / "sub").mkdir(parents=True)
    (root / "file.txt").write_text("hello")
    (root / "sub" / "inner.txt").write_text("world")
    return root

def test_plain_copy():
    src = _make_dummy_tree()
    bm = BackupManager()
    dst = bm.copy_folder(src, dst_root=_TMP, compress=False)
    try:
        assert dst.is_dir()
        assert (dst / "file.txt").exists()
        assert (dst / "sub" / "inner.txt").exists()
    finally:
        shutil.rmtree(dst, ignore_errors=True)

def test_zip_copy():
    src = _make_dummy_tree()
    bm = BackupManager()
    dst = bm.copy_folder(src, dst_root=_TMP, compress=True)
    try:
        assert dst.suffix == ".zip"
        assert dst.exists()
    finally:
        dst.unlink(missing_ok=True)
