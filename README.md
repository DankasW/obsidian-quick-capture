# Obsidian Quick Capture

A small tool for Windows 11. Press **Ctrl+Space** anywhere and a small window
opens for jotting down a quick note, saved straight into your Obsidian vault.

Written in plain Python stdlib (tkinter + ctypes), no extra packages.

## Note types

- **Quick note** (Ctrl+Q) — new file, named after the first line of text
- **Journal** (Ctrl+J) — appends a line to today's daily note (`Journal/YEAR/YEAR-MM-DD.md`)
- **Idea** (Ctrl+I) — same as Quick note, different folder
- **Task** (Ctrl+T) — appends `- [ ] text` to `TODO.md`, with an optional due date
  (click the date field for a small calendar, or use the Today / Tomorrow / In a week buttons)

These are the types in `note_types.example.json`. Each type's keyboard shortcut
is just Ctrl + its first letter, so adding a new type (one entry in
`note_types.json`, no code changes) also gives it a shortcut automatically
(pick a name with a first letter that isn't already used).

## Setup

1. Copy `note_types.example.json` to `note_types.json`
2. Edit `vault_root` and folder names to match your vault
   (`vault_root` is just a fallback — the tool auto-detects your currently
   open vault from Obsidian's own `obsidian.json`)
3. Run `python capture.py`
4. To auto-start at login, add a shortcut in the Startup folder
   (`shell:startup`) pointing to `pythonw.exe capture.py`

## Notes

- Ctrl+Space falls back to Ctrl+Alt+Space if it's already taken
- The window follows the Windows theme (dark/light), has rounded corners, no
  minimize/maximize/close buttons, and is slightly translucent
- Ctrl+Backspace deletes the previous word while typing
- Ctrl+Enter saves and clears the window for the next note, instead of closing it
  (Esc closes it)
- `python test_capture.py` runs the self-check tests
