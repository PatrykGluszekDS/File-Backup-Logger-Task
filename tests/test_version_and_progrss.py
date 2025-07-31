from pathlib import Path
import shutil, tempfile

from src.backup import BackupManager

_TMP = Path(tempfile.gettempdir())


def test_version_bump():
    src = _TMP / "dummy_bump_src"
    if src.exists():
        shutil.rmtree(src)
    (src / "file").mkdir(parents=True)
    (src / "file" / "a.txt").write_text("x")

    bm = BackupManager()
    before = bm.cfg.get("default_version", "")
    bm.copy_folder(src, dst_root=_TMP, compress=False)
    after = bm.cfg.get("default_version")

    assert after != before
    # basic check: after ends in '.1' or increments by 1
    assert after.split(".")[-1].isdigit()

def test_progress_callback_called():
    src = _TMP / "dummy_progress_src"
    if src.exists():
        shutil.rmtree(src)
    for i in range(3):
        (src / f"file{i}.txt").parent.mkdir(parents=True, exist_ok=True)
        (src / f"file{i}.txt").write_text("x")

    bm = BackupManager()
    ticks = []

    def cb(done, total):
        ticks.append(done)

    bm.copy_folder(src, dst_root=_TMP, compress=False, progress_cb=cb)
    assert max(ticks) == len(ticks) == 3  # three files ➜ 3 ticks
