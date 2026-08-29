"""Card list used for nested values inside a Studio catalog form."""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from aniworlds_studio.catalog_form_specs import FieldSpec


class NestedValueEditor(ttk.LabelFrame):
    def __init__(
        self,
        parent: ttk.Widget,
        *,
        title: str,
        fields: tuple[FieldSpec, ...],
        values: list[dict],
        open_form: Callable[[tuple[FieldSpec, ...], dict], dict | None],
        on_changed: Callable[[], None] = lambda: None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        super().__init__(parent, text=title, padding=10)
        self._fields = fields
        self._values = values
        self._open_form = open_form
        self._on_changed = on_changed
        self._minimum = minimum
        self._maximum = maximum
        self._list = tk.Listbox(self, height=5, exportselection=False)
        self._list.pack(fill="x")
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(8, 0))
        ttk.Button(controls, text="Добавить", command=self._add).pack(side="left")
        ttk.Button(controls, text="Изменить", command=self._edit).pack(side="left", padx=6)
        ttk.Button(controls, text="Удалить", command=self._delete).pack(side="left")
        self._list.bind("<Double-Button-1>", lambda _event: self._edit())
        self.refresh()

    def values(self) -> list[dict]:
        return [dict(value) for value in self._values]

    def refresh(self) -> None:
        self._list.delete(0, "end")
        for position, value in enumerate(self._values, 1):
            label = value.get("name") or value.get("item_id") or value.get("language_id")
            label = label or value.get("period_id") or value.get("id") or f"Запись {position}"
            self._list.insert("end", f"{position}. {label}")

    def _selected(self) -> int | None:
        selected = self._list.curselection()
        return int(selected[0]) if selected else None

    def _add(self) -> None:
        if self._maximum is not None and len(self._values) >= self._maximum:
            messagebox.showerror("Достигнут предел", f"Можно добавить не больше {self._maximum}.")
            return
        result = self._open_form(self._fields, _default_mapping(self._fields))
        if result is not None:
            self._values.append(result)
            self.refresh()
            self._on_changed()

    def _edit(self) -> None:
        index = self._selected()
        if index is None:
            return
        result = self._open_form(self._fields, self._values[index])
        if result is not None:
            self._values[index] = result
            self.refresh()
            self._on_changed()

    def _delete(self) -> None:
        index = self._selected()
        if index is None:
            return
        if self._minimum is not None and len(self._values) <= self._minimum:
            messagebox.showerror("Нельзя удалить", f"Должно остаться не меньше {self._minimum}.")
            return
        del self._values[index]
        self.refresh()
        self._on_changed()


def _default_mapping(fields: tuple[FieldSpec, ...]) -> dict:
    result: dict = {}
    for field in fields:
        if field.kind == "boolean":
            result[field.key] = False
        elif field.kind in {"integer", "decimal", "optional_integer"}:
            result[field.key] = field.minimum if field.kind == "integer" else None
        elif field.kind in {"lines", "choices", "references", "nested", "language_units"}:
            result[field.key] = []
        elif field.kind == "states":
            result[field.key] = {}
        elif field.options:
            result[field.key] = field.options[0][1]
        else:
            result[field.key] = ""
    return result
