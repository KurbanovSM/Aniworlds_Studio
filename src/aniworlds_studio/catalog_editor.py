"""Reusable card editor for structured Studio catalog entries."""

# ruff: noqa: RUF001

import tkinter as tk
from collections.abc import Callable
from dataclasses import asdict
from tkinter import messagebox, ttk
from typing import Any

from aniworlds_studio.catalog_form_dialog import CardFormDialog
from aniworlds_studio.catalog_form_specs import CATALOG_FORM_SPECS, FieldSpec
from aniworlds_studio.catalog_references import entry_title
from aniworlds_studio.catalog_templates import CATALOG_HINTS, new_catalog_entry
from aniworlds_studio.foundation_export import replace_catalog_entries
from aniworlds_studio.studio_theme import LINE, MUTED, SURFACE, TEXT


class CatalogEditor(ttk.Frame):
    """Display each entry as a card and edit it through labeled controls."""

    def __init__(
        self,
        parent: ttk.Widget,
        *,
        field_name: str,
        identity_field: str,
        get_draft: Callable[[], Any],
        on_changed: Callable[[], None],
        fields: tuple[FieldSpec, ...] | None = None,
        replace_entries: Callable[[Any, str, list[dict[str, Any]]], None] = (
            replace_catalog_entries
        ),
        get_reference_draft: Callable[[], Any] | None = None,
    ) -> None:
        super().__init__(parent, padding=14, style="Surface.TFrame")
        self._field_name = field_name
        self._identity_field = identity_field
        self._get_draft = get_draft
        self._on_changed = on_changed
        self._fields = fields or CATALOG_FORM_SPECS[field_name]
        self._replace_entries = replace_entries
        self._get_reference_draft = get_reference_draft or get_draft
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text=CATALOG_HINTS[self._field_name], wraplength=760).pack(
            fill="x", pady=(0, 10)
        )
        ttk.Button(
            self,
            text="Добавить карточку",
            style="Primary.TButton",
            command=self._new,
        ).pack(anchor="w", pady=(0, 10))
        host = ttk.Frame(self)
        host.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(host, highlightthickness=0, background="#090a0e")
        scrollbar = ttk.Scrollbar(host, orient="vertical", command=self._canvas.yview)
        self._cards = ttk.Frame(self._canvas)
        window = self._canvas.create_window((0, 0), window=self._cards, anchor="nw")
        self._cards.bind(
            "<Configure>",
            lambda _event: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.bind(
            "<Configure>", lambda event: self._canvas.itemconfigure(window, width=event.width)
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._canvas.bind("<MouseWheel>", self._wheel)

    def refresh(self) -> None:
        for child in self._cards.winfo_children():
            child.destroy()
        entries = self._entries()
        if not entries:
            ttk.Label(
                self._cards,
                text="Карточек пока нет. Нажмите «Добавить карточку».",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=14)
            return
        for index, entry in enumerate(entries):
            self._card(index, entry)

    def _card(self, index: int, entry: Any) -> None:
        card = tk.Frame(
            self._cards,
            background=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        card.pack(fill="x", pady=5)
        title, identity = entry_title(entry, self._identity_field)
        text = tk.Frame(card, background=SURFACE)
        text.pack(side="left", fill="x", expand=True)
        tk.Label(
            text,
            text=title,
            background=SURFACE,
            foreground=TEXT,
            font=("Segoe UI Semibold", 12),
        ).pack(anchor="w")
        tk.Label(
            text,
            text=f"ID: {identity}",
            background=SURFACE,
            foreground=MUTED,
        ).pack(anchor="w", pady=(3, 0))
        ttk.Button(card, text="Удалить", command=lambda: self._delete(index)).pack(side="right")
        ttk.Button(card, text="Изменить", command=lambda: self._edit(index)).pack(
            side="right", padx=8
        )
        card.bind("<MouseWheel>", self._wheel)
        for child in card.winfo_children():
            child.bind("<MouseWheel>", self._wheel)

    def _entries(self) -> list[Any]:
        return getattr(self._get_draft(), self._field_name)

    def _new(self) -> None:
        self._open(None, new_catalog_entry(self._field_name))

    def _edit(self, index: int) -> None:
        self._open(index, asdict(self._entries()[index]))

    def _open(self, index: int | None, initial: dict) -> None:
        dialog = CardFormDialog(
            self,
            title="Новая карточка" if index is None else "Изменить карточку",
            fields=self._fields,
            initial=initial,
            draft=self._get_draft(),
            reference_draft=self._get_reference_draft(),
        )
        self.wait_window(dialog)
        if dialog.result is None:
            return
        mappings = [asdict(entry) for entry in self._entries()]
        if index is None:
            mappings.append(dialog.result)
        else:
            mappings[index] = dialog.result
        try:
            self._replace_entries(self._get_draft(), self._field_name, mappings)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Не удалось сохранить карточку", str(error))
            return
        self.refresh()
        self._on_changed()

    def _delete(self, index: int) -> None:
        mappings = [
            asdict(entry)
            for position, entry in enumerate(self._entries())
            if position != index
        ]
        try:
            self._replace_entries(self._get_draft(), self._field_name, mappings)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Не удалось удалить карточку", str(error))
            return
        self.refresh()
        self._on_changed()

    def _wheel(self, event: tk.Event) -> str:
        self._canvas.yview_scroll(-3 if event.delta > 0 else 3, "units")
        return "break"
