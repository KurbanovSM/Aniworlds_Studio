"""Reusable Tkinter text and entry builders."""

import tkinter as tk
from tkinter import ttk


def entry_field(parent: ttk.Widget, label: str, kind: str = "text") -> tk.StringVar:
    variable = tk.StringVar()
    ttk.Label(parent, text=label).pack(anchor="w", pady=(4, 2))
    if kind == "long_text":
        editor = tk.Text(parent, height=5, wrap="word", undo=True)
        editor.pack(fill="x")
        editor.bind(
            "<KeyRelease>",
            lambda _event: _text_changed(editor, variable),
        )
        variable.trace_add(
            "write",
            lambda *_args: _sync_text(editor, variable.get()),
        )
    else:
        ttk.Entry(parent, textvariable=variable).pack(fill="x")
    return variable


def _sync_text(editor: tk.Text, value: str) -> None:
    if editor.get("1.0", "end-1c") == value:
        return
    editor.delete("1.0", "end")
    editor.insert("1.0", value)
    _resize_text(editor)


def _text_changed(editor: tk.Text, variable: tk.StringVar) -> None:
    variable.set(editor.get("1.0", "end-1c"))
    _resize_text(editor)


def _resize_text(editor: tk.Text) -> None:
    lines = int(editor.index("end-1c").split(".")[0])
    editor.configure(height=max(4, min(12, lines)))
