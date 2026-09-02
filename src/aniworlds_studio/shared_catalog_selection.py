"""Select shared catalog records and configure only their world-owned fields."""

import tkinter as tk
from dataclasses import asdict
from tkinter import messagebox, ttk

from aniworlds_studio.catalog_form_dialog import CardFormDialog
from aniworlds_studio.catalog_form_specs import FieldSpec
from aniworlds_studio.foundation_models import CreatureKindDraft, GroupDraft


class SharedCatalogSelectionEditor(ttk.Frame):
    """Add shared records to one world without duplicating base-data editing."""

    def __init__(
        self,
        parent: ttk.Widget,
        *,
        field_name: str,
        get_draft,
        get_catalogs,
        on_changed,
        world_fields: tuple[FieldSpec, ...] = (),
    ) -> None:
        super().__init__(parent, padding=14, style="Surface.TFrame")
        self._field_name = field_name
        self._get_draft = get_draft
        self._get_catalogs = get_catalogs
        self._on_changed = on_changed
        self._world_fields = world_fields
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(
            self,
            text=(
                "Основная карточка редактируется во вкладке «Общие каталоги». "
                "Здесь запись добавляется в мир и получает мировые связи."
            ),
            style="Muted.TLabel",
            wraplength=840,
        ).pack(anchor="w", pady=(0, 10))
        columns = ttk.Frame(self)
        columns.pack(fill="both", expand=True)
        available = ttk.LabelFrame(columns, text="Общий каталог", padding=10)
        selected = ttk.LabelFrame(columns, text="Добавлено в мир", padding=10)
        available.pack(side="left", fill="both", expand=True, padx=(0, 6))
        selected.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self._available = tk.Listbox(available, exportselection=False)
        self._available.pack(fill="both", expand=True)
        ttk.Button(available, text="Добавить в мир", command=self._add).pack(
            anchor="w", pady=(8, 0)
        )
        self._selected = tk.Listbox(selected, exportselection=False)
        self._selected.pack(fill="both", expand=True)
        controls = ttk.Frame(selected, style="Surface.TFrame")
        controls.pack(fill="x", pady=(8, 0))
        if self._world_fields:
            ttk.Button(controls, text="Настроить в мире", command=self._configure).pack(side="left")
        ttk.Button(controls, text="Убрать из мира", command=self._remove).pack(
            side="left", padx=(6, 0)
        )

    def refresh(self) -> None:
        self._available.delete(0, "end")
        self._selected.delete(0, "end")
        for item in self._shared_entries():
            self._available.insert("end", _entry_label(item))
        for item in self._world_entries():
            self._selected.insert("end", _entry_label(item))

    def _shared_entries(self) -> list:
        return getattr(self._get_catalogs(), self._field_name)

    def _world_entries(self) -> list:
        return getattr(self._get_draft(), self._field_name)

    def _add(self) -> None:
        index = _selected_index(self._available)
        if index is None:
            return
        shared = self._shared_entries()[index]
        if any(item.id == shared.id for item in self._world_entries()):
            messagebox.showerror("Уже добавлено", "Эта запись уже используется в мире.")
            return
        self._world_entries().append(_world_copy(self._field_name, shared))
        self.refresh()
        self._on_changed()

    def _remove(self) -> None:
        index = _selected_index(self._selected)
        if index is None:
            return
        del self._world_entries()[index]
        self.refresh()
        self._on_changed()

    def _configure(self) -> None:
        index = _selected_index(self._selected)
        if index is None:
            return
        entry = self._world_entries()[index]
        initial = asdict(entry)
        dialog = CardFormDialog(
            self,
            title=f"Настройки в мире: {entry.name}",
            fields=self._world_fields,
            initial=initial,
            draft=self._get_draft(),
        )
        self.wait_window(dialog)
        if dialog.result is None:
            return
        for key, value in dialog.result.items():
            setattr(entry, key, value)
        self.refresh()
        self._on_changed()


def _world_copy(field_name: str, shared):
    data = asdict(shared)
    if field_name == "creature_kinds":
        return CreatureKindDraft(**data)
    if field_name == "groups":
        return GroupDraft(**data)
    return type(shared)(**data)


def _selected_index(widget: tk.Listbox) -> int | None:
    selected = widget.curselection()
    return int(selected[0]) if selected else None


def _entry_label(item) -> str:
    section = f"[{item.section_id}] " if getattr(item, "section_id", "") else ""
    return f"{section}{item.name} ({item.id})"
