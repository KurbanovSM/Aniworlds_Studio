"""Two-level editor for shared item catalog sections."""

# ruff: noqa: RUF001

from __future__ import annotations

import tkinter as tk
from dataclasses import asdict
from tkinter import messagebox, ttk
from types import SimpleNamespace
from typing import Any

from aniworlds_studio.catalog_editor import CatalogEditor
from aniworlds_studio.catalog_form_dialog import CardFormDialog
from aniworlds_studio.catalog_form_specs import CATALOG_FORM_SPECS, FieldSpec
from aniworlds_studio.foundation_models import EquipmentDraft, EquipmentSectionDraft
from aniworlds_studio.global_catalogs import GlobalCatalogDraft
from aniworlds_studio.studio_theme import LINE, MUTED, SURFACE, TEXT

SECTION_FIELDS = (
    FieldSpec("id", "ID раздела"),
    FieldSpec("name", "Название раздела"),
)


def replace_section_equipment(
    catalogs: GlobalCatalogDraft,
    section_id: str,
    entries: list[dict[str, Any]],
) -> None:
    """Replace only one section while preserving every other section."""
    retained = [item for item in catalogs.equipment if item.section_id != section_id]
    replacements = [EquipmentDraft(**{**item, "section_id": section_id}) for item in entries]
    catalogs.equipment[:] = [*retained, *replacements]


def rename_equipment_section(
    catalogs: GlobalCatalogDraft,
    old_id: str,
    replacement: EquipmentSectionDraft,
) -> None:
    """Rename one section and keep all its equipment attached."""
    if replacement.id != old_id and any(
        section.id == replacement.id for section in catalogs.equipment_sections
    ):
        raise ValueError("Раздел с таким ID уже существует.")
    section = next(section for section in catalogs.equipment_sections if section.id == old_id)
    section.id = replacement.id
    section.name = replacement.name
    for item in catalogs.equipment:
        if item.section_id == old_id:
            item.section_id = replacement.id


def delete_equipment_section(catalogs: GlobalCatalogDraft, section_id: str) -> None:
    """Delete one confirmed section and every card stored inside it."""
    catalogs.equipment_sections[:] = [
        item for item in catalogs.equipment_sections if item.id != section_id
    ]
    catalogs.equipment[:] = [item for item in catalogs.equipment if item.section_id != section_id]


class EquipmentSectionsEditor(ttk.Frame):
    """Show catalog cards first and item cards only inside an opened catalog."""

    def __init__(self, parent: ttk.Widget, *, get_catalogs, on_changed) -> None:
        super().__init__(parent, padding=14, style="Surface.TFrame")
        self._get_catalogs = get_catalogs
        self._on_changed = on_changed
        self._detail: ttk.Frame | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        self._list_view = ttk.Frame(self, style="Surface.TFrame")
        self._list_view.pack(fill="both", expand=True)
        ttk.Label(
            self._list_view,
            text=(
                "Сначала создайте каталог сеттинга, например «Наруто». Затем откройте "
                "его и добавляйте обычные предметы, одежду, броню и оружие."
            ),
            wraplength=800,
        ).pack(fill="x", pady=(0, 10))
        ttk.Button(
            self._list_view,
            text="Добавить каталог",
            style="Primary.TButton",
            command=self._new,
        ).pack(anchor="w", pady=(0, 10))
        host = ttk.Frame(self._list_view)
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

    def refresh(self) -> None:
        for child in self._cards.winfo_children():
            child.destroy()
        sections = self._get_catalogs().equipment_sections
        if not sections:
            ttk.Label(
                self._cards,
                text="Каталогов пока нет. Нажмите «Добавить каталог».",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=14)
            return
        for section in sections:
            self._card(section)

    def _card(self, section: EquipmentSectionDraft) -> None:
        card = tk.Frame(
            self._cards,
            background=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        card.pack(fill="x", pady=5)
        text = tk.Frame(card, background=SURFACE)
        text.pack(side="left", fill="x", expand=True)
        tk.Label(
            text,
            text=section.name,
            background=SURFACE,
            foreground=TEXT,
            font=("Segoe UI Semibold", 12),
        ).pack(anchor="w")
        count = sum(item.section_id == section.id for item in self._get_catalogs().equipment)
        tk.Label(
            text,
            text=f"ID: {section.id} · карточек: {count}",
            background=SURFACE,
            foreground=MUTED,
        ).pack(anchor="w", pady=(3, 0))
        ttk.Button(card, text="Удалить", command=lambda: self._delete(section.id)).pack(
            side="right"
        )
        ttk.Button(card, text="Изменить", command=lambda: self._edit(section.id)).pack(
            side="right", padx=8
        )
        ttk.Button(card, text="Открыть", command=lambda: self._open_section(section.id)).pack(
            side="right"
        )

    def _new(self) -> None:
        dialog = CardFormDialog(
            self,
            title="Новый каталог предметов",
            fields=SECTION_FIELDS,
            initial=asdict(EquipmentSectionDraft()),
            draft=self._get_catalogs(),
        )
        self.wait_window(dialog)
        if dialog.result is None:
            return
        section = EquipmentSectionDraft(**dialog.result)
        if not section.id.strip() or not section.name.strip():
            messagebox.showerror("Не удалось создать каталог", "Заполните ID и название.")
            return
        if any(item.id == section.id for item in self._get_catalogs().equipment_sections):
            messagebox.showerror("Не удалось создать каталог", "Каталог с таким ID уже существует.")
            return
        self._get_catalogs().equipment_sections.append(section)
        self.refresh()
        self._on_changed()

    def _edit(self, section_id: str) -> None:
        section = self._section(section_id)
        dialog = CardFormDialog(
            self,
            title="Изменить каталог предметов",
            fields=SECTION_FIELDS,
            initial=asdict(section),
            draft=self._get_catalogs(),
        )
        self.wait_window(dialog)
        if dialog.result is None:
            return
        replacement = EquipmentSectionDraft(**dialog.result)
        if not replacement.id.strip() or not replacement.name.strip():
            messagebox.showerror("Не удалось сохранить раздел", "Заполните ID и название.")
            return
        try:
            rename_equipment_section(self._get_catalogs(), section_id, replacement)
        except ValueError as error:
            messagebox.showerror("Не удалось сохранить раздел", str(error))
            return
        self.refresh()
        self._on_changed()

    def _delete(self, section_id: str) -> None:
        section = self._section(section_id)
        count = sum(item.section_id == section_id for item in self._get_catalogs().equipment)
        warning = (
            f"Удалить каталог «{section.name}»?\n\n"
            f"Вместе с ним безвозвратно будут удалены все карточки внутри: {count}."
        )
        if not messagebox.askyesno("Подтвердите удаление каталога", warning, icon="warning"):
            return
        delete_equipment_section(self._get_catalogs(), section_id)
        self.refresh()
        self._on_changed()

    def _open_section(self, section_id: str) -> None:
        section = self._section(section_id)
        proxy = SimpleNamespace(
            equipment=[
                item for item in self._get_catalogs().equipment if item.section_id == section_id
            ]
        )
        self._list_view.pack_forget()
        if self._detail is not None:
            self._detail.destroy()
        self._detail = ttk.Frame(self, padding=8, style="Surface.TFrame")
        self._detail.pack(fill="both", expand=True)
        heading = ttk.Frame(self._detail, style="Surface.TFrame")
        heading.pack(fill="x", pady=(0, 8))
        ttk.Button(heading, text="← К разделам", command=self._close_section).pack(side="left")
        ttk.Label(
            heading,
            text=f"{section.name} · ID: {section.id}",
            style="SectionTitle.TLabel",
        ).pack(side="left", padx=12)

        def replace(_draft, _field_name, entries) -> None:
            replace_section_equipment(self._get_catalogs(), section_id, entries)
            proxy.equipment = [
                item for item in self._get_catalogs().equipment if item.section_id == section_id
            ]

        def changed() -> None:
            self.refresh()
            self._on_changed()

        editor = CatalogEditor(
            self._detail,
            field_name="equipment",
            identity_field="id",
            get_draft=lambda: proxy,
            on_changed=changed,
            fields=CATALOG_FORM_SPECS["items"],
            replace_entries=replace,
            get_reference_draft=self._get_catalogs,
        )
        editor.pack(fill="both", expand=True)

    def _close_section(self) -> None:
        if self._detail is not None:
            self._detail.destroy()
            self._detail = None
        self.refresh()
        self._list_view.pack(fill="both", expand=True)

    def _section(self, section_id: str) -> EquipmentSectionDraft:
        return next(
            section
            for section in self._get_catalogs().equipment_sections
            if section.id == section_id
        )
