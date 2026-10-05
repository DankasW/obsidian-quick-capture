"""assert-based self-check za save_note i vault detekciju, bez frameworka."""
import json
import tempfile
from datetime import datetime
from pathlib import Path

from capture import save_note
from vault import detect_vault_root


def demo():
    with tempfile.TemporaryDirectory() as tmp:
        now = datetime(2026, 10, 5, 14, 32, 1)
        note_type = {"name": "Ideja", "folder": "Ideje"}
        path = save_note(tmp, note_type, "Testna misao", now=now)

        assert path.parent == Path(tmp) / "Ideje", "nije spremio u ispravan folder"
        assert path.name == "2026-10-05 143201 Quick Capture.md", path.name
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\ndate: 2026-10-05 14:32\ntype: Ideja\n---\n\n")
        assert content.endswith("Testna misao")

        task_type = {
            "name": "Task", "mode": "append", "target_file": "TODO.md",
            "line_format": "- [ ] {text}", "supports_due_date": True,
        }
        path = save_note(tmp, task_type, "Nazovi\nvodoinstalatera  ", now=now)
        save_note(tmp, task_type, "Druga stavka", now=now, due_date="2026-12-01")
        save_note(tmp, task_type, "Treća, neispravan rok", now=now, due_date="nije datum")
        assert path == Path(tmp) / "TODO.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert lines == [
            "- [ ] Nazovi vodoinstalatera ➕ 2026-10-05",
            "- [ ] Druga stavka 📅 2026-12-01",
            "- [ ] Treća, neispravan rok ➕ 2026-10-05",
        ], lines

        daily_type = {"name": "Dnevnik", "folder": "Dnevnik", "mode": "daily"}
        path = save_note(tmp, daily_type, "Prva misao dana.", now=now)
        save_note(tmp, daily_type, "Druga misao, kasnije.", now=now)
        assert path == Path(tmp) / "Dnevnik" / "2026" / "2026-10-05.md"
        assert path.read_text(encoding="utf-8") == "Prva misao dana.\n\nDruga misao, kasnije."

        idea_type = {"name": "Ideja", "folder": "Ideje", "title_from_first_line": True}
        path = save_note(tmp, idea_type, "Ideja za vikend: posjetiti dida?\nRazraditi kasnije.", now=now)
        assert path.name == "Ideja za vikend posjetiti dida.md", path.name
        path2 = save_note(tmp, idea_type, "Ideja za vikend: posjetiti dida?\nDrugi pokušaj.", now=now)
        assert path2.name == "Ideja za vikend posjetiti dida (2).md", path2.name

        cfg = Path(tmp) / "obsidian.json"
        cfg.write_text(json.dumps({"vaults": {
            "a": {"path": "C:\\VaultA", "ts": 200},
            "b": {"path": "C:\\VaultB", "ts": 100, "open": True},
        }}))
        assert detect_vault_root(config_path=cfg) == "C:\\VaultB", "open vault treba imati prednost"

        cfg.write_text(json.dumps({"vaults": {
            "a": {"path": "C:\\VaultA", "ts": 200},
            "b": {"path": "C:\\VaultB", "ts": 100},
        }}))
        assert detect_vault_root(config_path=cfg) == "C:\\VaultA", "bez open, pobjeđuje najnoviji ts"

        missing = Path(tmp) / "ne-postoji.json"
        assert detect_vault_root(fallback="C:\\Fallback", config_path=missing) == "C:\\Fallback"

        print("OK")


if __name__ == "__main__":
    demo()
