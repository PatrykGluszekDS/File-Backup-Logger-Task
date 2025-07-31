import json
from pathlib import Path
from typing import Any, Dict, Union

_DEFAULTS: Dict[str, Any] = {
    "backup_root": "backups",
    "default_version": "",
    "compress": False,
}


class Config:
    def __init__(self, file: Union[str, Path] = "config.json") -> None:
        self.path = Path(file).expanduser()
        if not self.path.exists():
            self._write_defaults()
        self._data: Dict[str, Any] = self._load()

    # ---------- public helpers ----------
    def get(self, key: str, fallback: Any = None) -> Any:
        return self._data.get(key, fallback)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    # ---------- internals ----------
    def _load(self) -> Dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def _write_defaults(self) -> None:
        self.path.write_text(json.dumps(_DEFAULTS, indent=2), encoding="utf-8")
