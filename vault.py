"""Auto-detekcija trenutno otvorenog Obsidian vaulta iz obsidian.json."""
import json
import os
import pathlib

OBSIDIAN_CONFIG = pathlib.Path(os.environ["APPDATA"]) / "obsidian" / "obsidian.json"


def detect_vault_root(fallback=None, config_path=OBSIDIAN_CONFIG):
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        vaults = data.get("vaults", {})
        if not vaults:
            return fallback
        open_vault = next((v for v in vaults.values() if v.get("open")), None)
        chosen = open_vault or max(vaults.values(), key=lambda v: v.get("ts", 0))
        return chosen["path"]
    except (OSError, json.JSONDecodeError, KeyError):
        return fallback
