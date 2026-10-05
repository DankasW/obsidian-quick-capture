# Obsidian Quick Capture

Mali alat za Windows 11. Pritisneš **Ctrl+Space** bilo gdje i otvori se prozor
za brzi upis bilješke, koja se sprema direktno u tvoj Obsidian vault.

Napisano u čistom Python stdlibu (tkinter + ctypes), bez dodatnih paketa.

## Vrste bilješki

- **Brza bilješka** (Ctrl+B) — novi fajl, naziv = prva linija teksta
- **Dnevnik** (Ctrl+D) — dodaje redak u tvoju today-notu (`Dnevnik/GODINA/GODINA-MM-DD.md`)
- **Ideja** (Ctrl+I) — isto kao Brza bilješka, drugi folder
- **Task** (Ctrl+T) — dodaje `- [ ] tekst` u `TODO.md`, uz opcionalni rok (date picker)

Dodavanje nove vrste = jedan unos u `note_types.json`, kod se ne mijenja.

## Postavljanje

1. Kopiraj `note_types.example.json` u `note_types.json`
2. Uredi `vault_root` i nazive foldera da odgovaraju tvom vaultu
   (`vault_root` je samo rezerva — alat sam prepoznaje trenutno otvoren
   vault iz Obsidianovog `obsidian.json`)
3. Pokreni `python capture.py`
4. Za auto-pokretanje pri loginu, napravi prečac u Startup folderu
   (`shell:startup`) prema `pythonw.exe capture.py`

## Ostalo

- Ctrl+Space ima fallback na Ctrl+Alt+Space ako je zauzet
- Prozor prati Windows temu (dark/light) i lagano je proziran
- `python test_capture.py` pokreće self-check testove
