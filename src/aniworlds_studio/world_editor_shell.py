"""Old-Studio-inspired navigation shell for the world editor."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Any

from aniworlds_studio.studio_theme import ACCENT, LINE, MUTED, SIDEBAR, SURFACE, TEXT


class WorldEditorShell:
    """Keep one clear section visible and expose every section in a sidebar."""

    def __init__(self, parent: ttk.Widget) -> None:
        self._views: dict[str, ttk.Frame] = {}
        self._buttons: dict[str, ttk.Button] = {}
        self._active = ""
        self._build(parent)

    def _build(self, parent: ttk.Widget) -> None:
        body = ttk.Frame(parent)
        body.pack(fill="both", expand=True)
        sidebar_host = ttk.Frame(body, style="Sidebar.TFrame", width=246)
        sidebar_host.pack(side="left", fill="y")
        sidebar_host.pack_propagate(False)
        self._sidebar_canvas = tk.Canvas(
            sidebar_host,
            background=SIDEBAR,
            highlightthickness=0,
            width=228,
        )
        sidebar_scroll = ttk.Scrollbar(
            sidebar_host,
            orient="vertical",
            command=self._sidebar_canvas.yview,
        )
        self._sidebar = ttk.Frame(
            self._sidebar_canvas,
            style="Sidebar.TFrame",
            padding=(12, 14),
        )
        sidebar_window = self._sidebar_canvas.create_window(
            (0, 0),
            window=self._sidebar,
            anchor="nw",
        )
        self._sidebar.bind(
            "<Configure>",
            lambda _event: self._sidebar_canvas.configure(
                scrollregion=self._sidebar_canvas.bbox("all")
            ),
        )
        self._sidebar_canvas.bind(
            "<Configure>",
            lambda event: self._sidebar_canvas.itemconfigure(sidebar_window, width=event.width),
        )
        self._sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        self._sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scroll.pack(side="right", fill="y")
        self._sidebar_canvas.bind(
            "<MouseWheel>",
            lambda event: self._sidebar_canvas.yview_scroll(
                -3 if event.delta > 0 else 3,
                "units",
            ),
        )
        summary = tk.Frame(
            self._sidebar,
            background=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
        )
        summary.pack(fill="x", pady=(0, 14), ipady=10)
        tk.Label(
            summary,
            text="AW",
            width=3,
            height=2,
            background=ACCENT,
            foreground="#171206",
            font=("Segoe UI Semibold", 12),
        ).pack(side="left", padx=10)
        copy = tk.Frame(summary, background=SURFACE)
        copy.pack(side="left", fill="x", expand=True)
        tk.Label(
            copy,
            text="Основа мира",
            background=SURFACE,
            foreground=TEXT,
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w")
        tk.Label(
            copy,
            text="Редактор каталогов",
            background=SURFACE,
            foreground=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(2, 0))
        self.content = ttk.Frame(body, padding=(28, 22))
        self.content.pack(side="left", fill="both", expand=True)

    def add_view(
        self,
        key: str,
        title: str,
        subtitle: str,
        builder: Callable[[ttk.Frame], None],
        *,
        marker: str,
    ) -> ttk.Frame:
        button = ttk.Button(
            self._sidebar,
            text=f"{marker}   {title}\n      {subtitle}",
            style="Nav.TButton",
            command=lambda: self.show(key),
        )
        button.pack(fill="x", pady=2)
        button.bind(
            "<MouseWheel>",
            lambda event: self._sidebar_canvas.yview_scroll(
                -3 if event.delta > 0 else 3,
                "units",
            ),
        )
        view = ttk.Frame(self.content)
        self._views[key] = view
        self._buttons[key] = button
        builder(view)
        return view

    def show(self, key: str) -> None:
        if key not in self._views:
            raise KeyError(key)
        if self._active:
            self._views[self._active].pack_forget()
            self._buttons[self._active].configure(style="Nav.TButton")
        self._active = key
        self._views[key].pack(fill="both", expand=True)
        self._buttons[key].configure(style="ActiveNav.TButton")


def build_page_heading(parent: ttk.Widget, eyebrow: str, title: str, description: str) -> None:
    ttk.Label(parent, text=eyebrow.upper(), style="Accent.TLabel").pack(anchor="w")
    ttk.Label(
        parent,
        text=title,
        font=("Segoe UI Semibold", 24),
    ).pack(anchor="w", pady=(4, 2))
    ttk.Label(
        parent,
        text=description,
        style="Muted.TLabel",
        wraplength=760,
    ).pack(anchor="w", pady=(0, 18))


def configure_native_editor(widget: tk.Widget) -> None:
    options: dict[str, Any] = {
        "background": SIDEBAR,
        "foreground": TEXT,
        "selectbackground": "#594d9f",
        "selectforeground": TEXT,
        "highlightbackground": LINE,
        "highlightcolor": ACCENT,
        "highlightthickness": 1,
        "relief": "flat",
    }
    if isinstance(widget, tk.Text):
        options["insertbackground"] = TEXT
    widget.configure(options)
