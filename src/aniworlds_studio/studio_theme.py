"""Dark visual theme shared by the offline Studio screens."""

import tkinter as tk
from tkinter import ttk

BACKGROUND = "#090a0e"
SIDEBAR = "#101117"
SURFACE = "#151720"
SURFACE_ALT = "#1d202b"
LINE = "#2a2d39"
TEXT = "#f4f2f7"
MUTED = "#999dab"
ACCENT = "#f5bf32"
ACCENT_DARK = "#171206"


def configure_studio_theme(root: tk.Tk) -> None:
    """Configure ttk so the desktop app resembles the established Studio shell."""
    root.configure(background=BACKGROUND)
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*TCombobox*Listbox.background", SURFACE_ALT)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BACKGROUND, foreground=TEXT)
    style.configure("TFrame", background=BACKGROUND)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("Sidebar.TFrame", background=SIDEBAR)
    style.configure("TLabel", background=BACKGROUND, foreground=TEXT)
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Accent.TLabel", foreground=ACCENT, font=("Segoe UI Semibold", 9))
    style.configure("Title.TLabel", font=("Segoe UI Semibold", 24))
    style.configure("SectionTitle.TLabel", font=("Segoe UI Semibold", 18))
    style.configure("Surface.TLabel", background=SURFACE, foreground=TEXT)
    style.configure("SurfaceMuted.TLabel", background=SURFACE, foreground=MUTED)
    style.configure("TLabelframe", background=SURFACE, bordercolor=LINE, relief="solid")
    style.configure(
        "TLabelframe.Label",
        background=SURFACE,
        foreground=ACCENT,
        font=("Segoe UI Semibold", 10),
    )
    style.configure(
        "TEntry",
        fieldbackground=SIDEBAR,
        foreground=TEXT,
        insertcolor=TEXT,
        bordercolor=LINE,
        lightcolor=LINE,
        darkcolor=LINE,
        padding=8,
    )
    style.configure(
        "TCombobox",
        fieldbackground=SIDEBAR,
        background=SURFACE_ALT,
        foreground=TEXT,
        arrowcolor=TEXT,
        bordercolor=LINE,
        padding=7,
    )
    style.map("TCombobox", fieldbackground=[("readonly", SIDEBAR)])
    style.configure("TSpinbox", fieldbackground=SIDEBAR, foreground=TEXT, padding=7)
    style.configure("TCheckbutton", background=SURFACE, foreground=TEXT)
    style.map("TCheckbutton", background=[("active", SURFACE)])
    style.configure("TButton", background=SURFACE_ALT, foreground=TEXT, bordercolor=LINE, padding=8)
    style.map("TButton", background=[("active", "#292d3a")])
    style.configure(
        "Primary.TButton",
        background=ACCENT,
        foreground=ACCENT_DARK,
        bordercolor=ACCENT,
        padding=(14, 10),
        font=("Segoe UI Semibold", 10),
    )
    style.map("Primary.TButton", background=[("active", "#ffd45c")])
    style.configure(
        "Nav.TButton",
        background=SIDEBAR,
        foreground=MUTED,
        borderwidth=0,
        anchor="w",
        padding=(14, 10),
    )
    style.configure(
        "ActiveNav.TButton",
        background=SURFACE_ALT,
        foreground=TEXT,
        bordercolor=ACCENT,
        borderwidth=1,
        anchor="w",
        padding=(14, 10),
        font=("Segoe UI Semibold", 10),
    )
    style.map("Nav.TButton", background=[("active", SURFACE_ALT)], foreground=[("active", TEXT)])
    style.configure("TNotebook", background=BACKGROUND, borderwidth=0)
    style.configure("TNotebook.Tab", background=SURFACE, foreground=MUTED, padding=(14, 8))
    style.map(
        "TNotebook.Tab",
        background=[("selected", SURFACE_ALT)],
        foreground=[("selected", TEXT)],
        padding=[("selected", (20, 12))],
        font=[("selected", ("Segoe UI Semibold", 10))],
    )
    style.configure("Vertical.TScrollbar", background=SURFACE_ALT, troughcolor=SIDEBAR)
