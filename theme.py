"""Čitanje Windows sistemske teme (dark/light) i stiliziranje prozora."""
import ctypes
import winreg

PERSONALIZE_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2
GWL_STYLE = -16
WS_SYSMENU = 0x00080000
SWP_FLAGS = 0x0001 | 0x0002 | 0x0004 | 0x0020  # NOSIZE | NOMOVE | NOZORDER | FRAMECHANGED

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
    """Oboji naslovnu traku prema sistemskoj temi, zaobli rubove, skine min/max/close i učini prozor blago prozirnim."""
    try:
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id()) or win.winfo_id()
        dark_value = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark_value), ctypes.sizeof(dark_value)
        )
        corner_value = ctypes.c_int(DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(corner_value), ctypes.sizeof(corner_value)
        )
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style & ~WS_SYSMENU)
        ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_FLAGS)
    except OSError:
        pass
    win.attributes("-alpha", 0.94)
