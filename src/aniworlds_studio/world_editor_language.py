"""Small Tkinter builder for the base-language form."""

import tkinter as tk
from tkinter import ttk


def entry_field(parent: ttk.Widget, label: str) -> tk.StringVar:
    variable = tk.StringVar()
    ttk.Label(parent, text=label).pack(anchor="w", pady=(4, 2))
    ttk.Entry(parent, textvariable=variable).pack(fill="x")
    return variable


def build_language_fields(
    section: ttk.Widget,
    variables: dict[str, tk.StringVar],
    spoken: tk.BooleanVar,
    written: tk.BooleanVar,
) -> None:
    ttk.Separator(section).pack(fill="x", pady=12)
    ttk.Label(section, text="Базовый язык").pack(anchor="w")
    variables["language_id"] = entry_field(section, "ID языка")
    variables["language_name"] = entry_field(section, "Название языка")
    ttk.Checkbutton(section, text="Устная форма", variable=spoken).pack(anchor="w", pady=(6, 0))
    ttk.Checkbutton(section, text="Письменная форма", variable=written).pack(anchor="w")
