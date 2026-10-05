"""Čitanje Windows sistemske teme (dark/light) i stiliziranje prozora."""
import ctypes
import winreg

PERSONALIZE_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
DWMWA_USE_IMMERSIVE_DARK_MODE = 20

LIGHT = {
    "bg": "#f3f3f3",
    "fg": "#1a1a1a",
    "field_bg": "#ffffff",
    "accent": "#0067c0",
    "button_bg": "#e5e5e5",
    "select_bg": "#d9d9d9",
}
DARK = {
    "bg": "#202020",
    "fg": "#e8e8e8",
    "field_bg": "#2b2b2b",
    "accent": "#4cc2ff",
    "button_bg": "#323232",
    "select_bg": "#454545",
}


def is_dark_mode():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PERSONALIZE_KEY) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
    except OSError:
        return False


def colors():
    return DARK if is_dark_mode() else LIGHT


def apply(win, dark):
    """Oboji naslovnu traku prema sistemskoj temi i učini prozor blago prozirnim."""
    try:
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
        )
    except OSError:
        pass
    win.attributes("-alpha", 0.94)
