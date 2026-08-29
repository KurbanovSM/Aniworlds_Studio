"""Layout-independent clipboard shortcuts for editable Tk controls on Windows."""

import tkinter as tk
from tkinter import ttk

_VIRTUAL_EVENT_BY_KEYCODE = {
    65: "<<SelectAll>>",
    67: "<<Copy>>",
    86: "<<Paste>>",
    88: "<<Cut>>",
}
_EDITABLE_CONTROLS = (tk.Entry, tk.Text, ttk.Entry, ttk.Spinbox, ttk.Combobox)


def clipboard_event_for_keycode(keycode: int) -> str | None:
    """Resolve physical A/C/V/X keys independently of the active keyboard layout."""
    return _VIRTUAL_EVENT_BY_KEYCODE.get(keycode)


def install_clipboard_shortcuts(root: tk.Misc) -> None:
    """Make the standard Ctrl shortcuts work with Latin and Cyrillic layouts."""

    def handle(event: tk.Event) -> str | None:
        virtual_event = clipboard_event_for_keycode(event.keycode)
        if virtual_event is None or not isinstance(event.widget, _EDITABLE_CONTROLS):
            return None
        if virtual_event == "<<SelectAll>>":
            _select_all(event.widget)
        else:
            event.widget.event_generate(virtual_event)
        return "break"

    root.bind_all("<Control-KeyPress>", handle, add="+")


def _select_all(widget: tk.Entry | tk.Text | ttk.Entry | ttk.Spinbox | ttk.Combobox) -> None:
    if isinstance(widget, tk.Text):
        widget.tag_add("sel", "1.0", "end-1c")
        widget.mark_set("insert", "1.0")
        return
    widget.selection_range(0, "end")
    widget.icursor("end")
