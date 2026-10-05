"""Quick Capture za Obsidian. Globalni hotkey otvara mali prozor za upis bilješke.

Vrste bilješki i ciljni folderi se čitaju iz note_types.json (dodaj novu vrstu
tako da dodaš jedan unos u taj fajl, kod se ne mijenja).
"""
import ctypes
import ctypes.wintypes as wintypes
import json
import pathlib
import re
import sys
import tkinter as tk
from datetime import datetime, timedelta

import calendar_picker
import theme
import vault

CONFIG_PATH = pathlib.Path(__file__).parent / "note_types.json"
HOTKEY_ID = 1
MOD_CONTROL = 0x0002
MOD_ALT = 0x0001
VK_SPACE = 0x20
WM_HOTKEY = 0x0312
ERROR_ALREADY_EXISTS = 183
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def ensure_single_instance():
    kernel32.CreateMutexW(None, False, "QuickCaptureObsidianMutex")
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        sys.exit(0)


def register_hotkey():
    if user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL, VK_SPACE):
        return "Ctrl+Space"
    if user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_SPACE):
        return "Ctrl+Alt+Space"
    raise RuntimeError("Ni Ctrl+Space ni Ctrl+Alt+Space nisu dostupni (zauzeti su).")


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def sanitize_filename(name, max_length=100):
    name = INVALID_FILENAME_CHARS.sub("", name).strip().rstrip(".")
    return name[:max_length] or "Quick Capture"


def unique_path(folder, stem):
    path = folder / f"{stem}.md"
    counter = 2
    while path.exists():
        path = folder / f"{stem} ({counter}).md"
        counter += 1
    return path


def save_note(vault_root, note_type, text, now=None, due_date=""):
    now = now or datetime.now()
    mode = note_type.get("mode")
    if mode == "append":
        return append_line(vault_root, note_type, text, now, due_date)
    if mode == "daily":
        return append_daily(vault_root, note_type, text, now)
    folder = pathlib.Path(vault_root) / note_type["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    if note_type.get("title_from_first_line"):
        stem = sanitize_filename(text.splitlines()[0])
        path = unique_path(folder, stem)
    else:
        path = folder / f"{now:%Y-%m-%d %H%M%S} Quick Capture.md"
    frontmatter = f"---\ndate: {now:%Y-%m-%d %H:%M}\ntype: {note_type['name']}\n---\n\n"
    path.write_text(frontmatter + text, encoding="utf-8")
    return path


def append_daily(vault_root, note_type, text, now):
    folder = pathlib.Path(vault_root) / note_type["folder"] / f"{now:%Y}"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{now:%Y-%m-%d}.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if existing.strip() else ""
    with path.open("a", encoding="utf-8") as f:
        f.write(separator + text)
    return path


def append_line(vault_root, note_type, text, now, due_date=""):
    path = pathlib.Path(vault_root) / note_type["target_file"]
    one_liner = " ".join(text.split())
    line = note_type.get("line_format", "{text}").format(text=one_liner)
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            line += f" 📅 {due_date}"
        except ValueError:
            line += f" ➕ {now:%Y-%m-%d}"
    else:
        line += f" ➕ {now:%Y-%m-%d}"
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return path


def open_capture_window(note_types, vault_root):
    dark = theme.is_dark_mode()
    c = theme.colors()

    win = tk.Tk()
    win.title("Obsidian Quick Capture by D@nkas")
    win.attributes("-topmost", True)
    win.geometry("480x340")
    win.configure(bg=c["bg"])

    selected = tk.StringVar(value=note_types[0]["name"])
    shortcuts = {nt["name"][0].upper(): nt for nt in note_types}

    type_frame = tk.Frame(win, bg=c["bg"])
    type_frame.pack(pady=10)
    for nt in note_types:
        tk.Radiobutton(
            type_frame, text=f"{nt['name']} (Ctrl+{nt['name'][0].upper()})", variable=selected, value=nt["name"],
            indicatoron=False, bg=c["button_bg"], fg=c["fg"], selectcolor=c["select_bg"],
            activebackground=c["select_bg"], relief="flat", borderwidth=0,
            padx=12, pady=5, highlightthickness=0,
        ).pack(side="left", padx=4)

    text_box = tk.Text(
        win, height=8, width=56, wrap="word", bg=c["field_bg"], fg=c["fg"],
        insertbackground=c["fg"], relief="flat", borderwidth=0,
        highlightthickness=1, highlightbackground=c["accent"], highlightcolor=c["accent"],
    )
    text_box.pack(padx=10, pady=4)

    def delete_word_before(event):
        # ponytail: briše samo unutar trenutnog retka, ne prelazi u prethodni red
        insert_idx = text_box.index("insert")
        line, _ = insert_idx.split(".")
        line_text = text_box.get(f"{line}.0", insert_idx)
        match = re.search(r"\S+\s*$", line_text)
        new_col = match.start() if match else 0
        text_box.delete(f"{line}.{new_col}", insert_idx)
        return "break"

    text_box.bind("<Control-BackSpace>", delete_word_before)

    due_date_var = tk.StringVar(value="")
    due_frame = tk.Frame(win, bg=c["bg"])
    tk.Label(due_frame, text="Rok:", bg=c["bg"], fg=c["fg"]).pack(side="left", padx=(0, 6))
    due_entry = tk.Entry(
        due_frame, textvariable=due_date_var, width=12, bg=c["field_bg"], fg=c["fg"],
        insertbackground=c["fg"], relief="flat", highlightthickness=1,
        highlightbackground=c["accent"], highlightcolor=c["accent"], state="readonly",
        readonlybackground=c["field_bg"],
    )
    due_entry.pack(side="left", padx=(0, 8))

    def open_calendar(event=None):
        try:
            initial = datetime.strptime(due_date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            initial = None
        x = due_entry.winfo_rootx() + due_entry.winfo_width() + 8
        y = due_entry.winfo_rooty()
        chosen = calendar_picker.pick_date(win, initial, x=x, y=y)
        if chosen:
            due_date_var.set(chosen)

    due_entry.bind("<Button-1>", open_calendar)
    today = datetime.now().date()
    for label, value in (
        ("Danas", today),
        ("Sutra", today + timedelta(days=1)),
        ("Tjedan dana", today + timedelta(days=7)),
    ):
        tk.Button(
            due_frame, text=label, bg=c["button_bg"], fg=c["fg"], activebackground=c["select_bg"],
            relief="flat", borderwidth=0, padx=8, pady=2,
            command=lambda v=value: due_date_var.set(v.isoformat()),
        ).pack(side="left", padx=2)

    def update_due_visibility(*_args):
        note_type = next(nt for nt in note_types if nt["name"] == selected.get())
        if note_type.get("supports_due_date"):
            due_frame.pack(pady=(0, 4))
        else:
            due_frame.pack_forget()

    selected.trace_add("write", update_due_visibility)
    update_due_visibility()

    def grab_focus():
        win.lift()
        ctypes.windll.user32.SetForegroundWindow(win.winfo_id())
        win.focus_force()
        text_box.focus_set()

    win.update_idletasks()
    theme.apply(win, dark)
    win.after(50, grab_focus)

    def do_save(event=None):
        content = text_box.get("1.0", "end").strip()
        if content:
            note_type = next(nt for nt in note_types if nt["name"] == selected.get())
            save_note(vault_root, note_type, content, due_date=due_date_var.get().strip())
            text_box.delete("1.0", "end")
            due_date_var.set("")
            text_box.focus_set()

    def do_cancel(event=None):
        win.destroy()

    button_frame = tk.Frame(win, bg=c["bg"])
    button_frame.pack(side="bottom", pady=8)
    for text, cmd in (("Spremi (Ctrl+Enter)", do_save), ("Odustani (Esc)", do_cancel)):
        tk.Button(
            button_frame, text=text, command=cmd, bg=c["button_bg"], fg=c["fg"],
            activebackground=c["select_bg"], relief="flat", borderwidth=0, padx=10, pady=4,
        ).pack(side="left", padx=6)

    win.bind("<Control-Return>", do_save)
    win.bind("<Escape>", do_cancel)

    def select_type(name):
        def handler(event):
            selected.set(name)
            return "break"
        return handler

    for letter, nt in shortcuts.items():
        seq = f"<Control-{letter.lower()}>"
        handler = select_type(nt["name"])
        win.bind(seq, handler)
        text_box.bind(seq, handler)
        due_entry.bind(seq, handler)

    win.mainloop()


def main():
    ensure_single_instance()
    config = load_config()
    hotkey_used = register_hotkey()
    print(f"Quick Capture aktivan. Hotkey: {hotkey_used}")

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == WM_HOTKEY:
            vault_root = vault.detect_vault_root(fallback=config.get("vault_root"))
            open_capture_window(config["types"], vault_root)


if __name__ == "__main__":
    main()
