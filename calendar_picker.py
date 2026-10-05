"""Mali calendar popup za biranje datuma (stdlib `calendar`, bez vanjskih paketa)."""
import calendar
import tkinter as tk
from datetime import date

import theme

DAY_NAMES = ["Po", "Ut", "Sr", "Če", "Pe", "Su", "Ne"]


def pick_date(parent, initial=None, x=None, y=None):
    initial = initial or date.today()
    c = theme.colors()
    result = {"value": None}
    state = {"year": initial.year, "month": initial.month}

    win = tk.Toplevel(parent)
    win.title("Odaberi datum")
    win.configure(bg=c["bg"])
    win.attributes("-topmost", True)
    win.transient(parent)
    win.resizable(False, False)
    if x is not None and y is not None:
        win.geometry(f"+{x}+{y}")
    win.grab_set()

    grid_frame = tk.Frame(win, bg=c["bg"])

    def render():
        for widget in grid_frame.winfo_children():
            widget.destroy()
        label.config(text=f"{calendar.month_name[state['month']]} {state['year']}")
        for col, name in enumerate(DAY_NAMES):
            tk.Label(grid_frame, text=name, bg=c["bg"], fg=c["fg"], width=3).grid(row=0, column=col)
        for row, week in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(state["year"], state["month"]), start=1):
            for col, day in enumerate(week):
                if day == 0:
                    tk.Label(grid_frame, text="", bg=c["bg"], width=3).grid(row=row, column=col)
                    continue
                is_today = date(state["year"], state["month"], day) == date.today()
                tk.Button(
                    grid_frame, text=str(day), width=3, relief="flat", borderwidth=0,
                    bg=c["select_bg"] if is_today else c["button_bg"], fg=c["fg"],
                    activebackground=c["accent"],
                    command=lambda d=day: choose(d),
                ).grid(row=row, column=col, padx=1, pady=1)

    def choose(day):
        result["value"] = date(state["year"], state["month"], day).isoformat()
        win.destroy()

    def change_month(delta):
        month = state["month"] + delta - 1
        state["year"] += month // 12
        state["month"] = month % 12 + 1
        render()

    header = tk.Frame(win, bg=c["bg"])
    header.pack(pady=6)
    tk.Button(
        header, text="◀", command=lambda: change_month(-1), bg=c["button_bg"], fg=c["fg"],
        relief="flat", borderwidth=0, padx=8,
    ).pack(side="left")
    label = tk.Label(header, bg=c["bg"], fg=c["fg"], font=("Segoe UI", 10, "bold"), width=16, anchor="center")
    label.pack(side="left", padx=4)
    tk.Button(
        header, text="▶", command=lambda: change_month(1), bg=c["button_bg"], fg=c["fg"],
        relief="flat", borderwidth=0, padx=8,
    ).pack(side="left")

    win.bind("<Escape>", lambda event: win.destroy())

    grid_frame.pack(padx=8, pady=(0, 8))
    render()
    win.update_idletasks()
    theme.apply(win, theme.is_dark_mode())
    win.wait_window()
    return result["value"]
