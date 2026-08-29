"""Tk controls for declarative Studio card fields."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from aniworlds_studio.catalog_form_specs import FieldSpec
from aniworlds_studio.catalog_form_values import FormControl, write_control
from aniworlds_studio.world_editor_shell import configure_native_editor


def build_control(
    parent: ttk.Widget,
    spec: FieldSpec,
    *,
    options: tuple[tuple[str, str], ...],
    initial: object,
) -> FormControl:
    """Build one labeled control using a compact two-column form."""
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=6)
    ttk.Label(row, text=spec.label, width=32, wraplength=240).pack(
        side="left", anchor="nw", padx=(0, 12)
    )
    kind = _normalized_kind(spec.kind)
    control = _widget_for_kind(row, kind, options, spec)
    control.widget.pack(side="left", fill="x", expand=True)
    write_control(control, initial)
    if spec.help_text:
        ttk.Label(parent, text=spec.help_text, style="Muted.TLabel", wraplength=680).pack(
            anchor="w", padx=(252, 0)
        )
    return control


def _widget_for_kind(
    parent: ttk.Frame,
    kind: str,
    options: tuple[tuple[str, str], ...],
    spec: FieldSpec,
) -> FormControl:
    if kind == "boolean":
        variable = tk.BooleanVar()
        return FormControl(kind, ttk.Checkbutton(parent, variable=variable), variable)
    if kind in {"long_text", "lines"}:
        height = 6 if kind == "long_text" else 5
        widget = tk.Text(parent, height=height, wrap="word", undo=True)
        configure_native_editor(widget)
        return FormControl(kind, widget)
    if kind in {"choices", "references"}:
        listbox = tk.Listbox(parent, selectmode="multiple", exportselection=False, height=5)
        configure_native_editor(listbox)
        for label, _ in options:
            listbox.insert("end", label)
        return FormControl(kind, listbox, options=options, variable=None)
    if kind in {"choice", "reference"}:
        variable = tk.StringVar()
        values = [label for label, _ in options]
        widget = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly")
        return FormControl(kind, widget, variable, options)
    variable = tk.StringVar()
    if kind in {"integer", "decimal", "optional_integer"}:
        widget = ttk.Spinbox(
            parent,
            from_=spec.minimum if spec.minimum is not None else 0,
            to=spec.maximum if spec.maximum is not None else 1_000_000,
            textvariable=variable,
        )
    else:
        widget = ttk.Entry(parent, textvariable=variable)
    return FormControl(kind, widget, variable)


def _normalized_kind(kind: str) -> str:
    return {
        "choice_optional": "choice",
        "reference_optional": "reference",
    }.get(kind, kind)


def bind_text_growth(text: tk.Text, maximum_lines: int = 12) -> None:
    """Grow long text areas with content without turning them into one long row."""

    def resize(_event: object | None = None) -> None:
        lines = max(3, min(maximum_lines, int(text.index("end-1c").split(".")[0])))
        text.configure(height=lines)

    text.bind("<KeyRelease>", resize, add="+")
    resize()


def bind_after_build(root: tk.Misc, callback: Callable[[tk.Text], None]) -> None:
    for child in root.winfo_children():
        if isinstance(child, tk.Text):
            callback(child)
        bind_after_build(child, callback)
