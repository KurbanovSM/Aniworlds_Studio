"""Mouse-wheel routing for the scrollable world form."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk


def bind_form_mousewheel(root: tk.Misc, scroll: Callable[[int], None]) -> None:
    """Scroll the outer form except over controls with their own vertical view."""
    own_scroll = (tk.Text, tk.Listbox, ttk.Combobox)

    def bind_tree(widget: tk.Misc) -> None:
        if not isinstance(widget, own_scroll):
            widget.bind(
                "<MouseWheel>",
                lambda event: scroll(-3 if event.delta > 0 else 3),
                add="+",
            )
        for child in widget.winfo_children():
            bind_tree(child)

    bind_tree(root)
