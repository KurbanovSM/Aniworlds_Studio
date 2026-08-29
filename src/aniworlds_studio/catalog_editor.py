"""Reusable list-and-JSON editor for structured Studio catalog entries."""

# ruff: noqa: RUF001

import json
import tkinter as tk
from collections.abc import Callable
from dataclasses import asdict
from tkinter import messagebox, ttk
from typing import Any

from aniworlds_studio.catalog_templates import CATALOG_HINTS, new_catalog_entry
from aniworlds_studio.foundation_export import replace_catalog_entries
from aniworlds_studio.foundation_models import UniverseDraft


class CatalogEditor(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Notebook,
        *,
        field_name: str,
        identity_field: str,
        get_draft: Callable[[], UniverseDraft],
        on_changed: Callable[[], None],
    ) -> None:
        super().__init__(parent, padding=10)
        self._field_name = field_name
        self._identity_field = identity_field
        self._get_draft = get_draft
        self._on_changed = on_changed
        self._selected_index: int | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text=CATALOG_HINTS[self._field_name], wraplength=700).pack(
            fill="x", pady=(0, 8)
        )
        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=1)
        body.add(right, weight=3)
        self._list = tk.Listbox(left, exportselection=False, height=18)
        self._list.pack(fill="both", expand=True)
        self._list.bind("<<ListboxSelect>>", self._select)
        controls = ttk.Frame(left)
        controls.pack(fill="x", pady=(6, 0))
        ttk.Button(controls, text="Добавить", command=self._new).pack(side="left")
        ttk.Button(controls, text="Удалить", command=self._delete).pack(side="left", padx=6)
        self._text = tk.Text(right, wrap="none", height=22, undo=True)
        self._text.pack(fill="both", expand=True)
        ttk.Button(right, text="Применить запись", command=self._apply).pack(
            anchor="e", pady=(6, 0)
        )

    def refresh(self) -> None:
        entries = self._entries()
        self._list.delete(0, "end")
        for position, entry in enumerate(entries, 1):
            identity = getattr(entry, self._identity_field, "")
            name = getattr(entry, "name", identity)
            self._list.insert("end", f"{position}. {name} ({identity})")
        if self._selected_index is not None and self._selected_index < len(entries):
            self._list.selection_set(self._selected_index)

    def _entries(self) -> list[Any]:
        return getattr(self._get_draft(), self._field_name)

    def _select(self, _event: object) -> None:
        selection = self._list.curselection()
        if not selection:
            return
        self._selected_index = int(selection[0])
        self._show(asdict(self._entries()[self._selected_index]))

    def _new(self) -> None:
        self._selected_index = None
        self._list.selection_clear(0, "end")
        self._show(new_catalog_entry(self._field_name))

    def _show(self, payload: dict) -> None:
        self._text.delete("1.0", "end")
        self._text.insert("1.0", json.dumps(payload, ensure_ascii=False, indent=2))

    def _apply(self) -> None:
        try:
            payload = json.loads(self._text.get("1.0", "end"))
            if not isinstance(payload, dict):
                raise ValueError("Запись должна быть JSON-объектом.")
            mappings = [asdict(entry) for entry in self._entries()]
            if self._selected_index is None:
                mappings.append(payload)
            else:
                mappings[self._selected_index] = payload
            replace_catalog_entries(self._get_draft(), self._field_name, mappings)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            messagebox.showerror("Не удалось применить запись", str(error))
            return
        self._selected_index = (
            len(mappings) - 1 if self._selected_index is None else self._selected_index
        )
        self.refresh()
        self._on_changed()

    def _delete(self) -> None:
        if self._selected_index is None:
            return
        mappings = [
            asdict(entry)
            for position, entry in enumerate(self._entries())
            if position != self._selected_index
        ]
        try:
            replace_catalog_entries(self._get_draft(), self._field_name, mappings)
        except (ValueError, TypeError) as error:
            messagebox.showerror("Не удалось удалить запись", str(error))
            return
        self._selected_index = None
        self._text.delete("1.0", "end")
        self.refresh()
        self._on_changed()
