"""Tkinter adapter for editing and publishing a complete world foundation."""

# ruff: noqa: RUF001

import tkinter as tk
from tkinter import messagebox, ttk

from aniworlds_studio.foundation_models import UniverseDraft
from aniworlds_studio.global_catalogs import synchronize_shared_catalogs
from aniworlds_studio.world_editor_catalogs import build_catalog_views
from aniworlds_studio.world_editor_fields import (
    ECONOMY_FIELDS,
    STRENGTH_FIELDS,
    UNIVERSE_FIELDS,
    WORLD_RULE_FIELDS,
)
from aniworlds_studio.world_editor_files import (
    open_world_dialog,
    publish_dialog,
    save_draft_dialog,
    show_preview,
)
from aniworlds_studio.world_editor_language import entry_field
from aniworlds_studio.world_editor_pages import (
    build_basics_page,
    build_overview_page,
    build_review_page,
)
from aniworlds_studio.world_editor_shell import WorldEditorShell


class WorldEditorFrame(ttk.Frame):
    """World-only editor; global values belong to the separate first tab."""

    def __init__(self, parent: ttk.Notebook, *, get_global_catalogs) -> None:
        super().__init__(parent)
        self._draft = UniverseDraft()
        self._variables: dict[str, tk.StringVar] = {}
        self._status = tk.StringVar(value="Новый черновик")
        self._get_global_catalogs = get_global_catalogs
        self._build()
        self._load_form()

    def _build(self) -> None:
        toolbar = ttk.Frame(self, padding=(18, 12))
        toolbar.pack(fill="x")
        for text, command in (
            ("Новый", self._new),
            ("Открыть мир", self._open),
            ("Сохранить черновик", self._save_draft),
            ("Предпросмотр", self._preview),
            ("Опубликовать", self._publish),
        ):
            style = "Primary.TButton" if text == "Опубликовать" else "TButton"
            ttk.Button(toolbar, text=text, command=command, style=style).pack(
                side="left", padx=(0, 8)
            )
        ttk.Label(toolbar, textvariable=self._status).pack(side="right")
        ttk.Separator(self).pack(fill="x")
        shell = WorldEditorShell(self)
        shell.add_view("overview", "Обзор", "Порядок работы", self._build_overview, marker="1")
        shell.add_view(
            "universe",
            "Вселенная",
            "Название и описание",
            lambda parent: self._build_scalar_page(
                parent, "Раздел 2", "Вселенная", "Основная карточка вселенной.", UNIVERSE_FIELDS
            ),
            marker="2",
        )
        shell.add_view(
            "rules",
            "Правила и силы",
            "Лорные ограничения",
            lambda parent: self._build_scalar_page(
                parent,
                "Раздел 3",
                "Правила и системы сил",
                "Многострочные поля расширяются по мере заполнения.",
                WORLD_RULE_FIELDS,
            ),
            marker="3",
        )
        shell.add_view(
            "economy",
            "Экономика",
            "Валюта мира",
            lambda parent: self._build_scalar_page(
                parent,
                "Раздел 4",
                "Экономика",
                "Валюта относится только к этой вселенной.",
                ECONOMY_FIELDS,
            ),
            marker="4",
        )
        shell.add_view(
            "strength",
            "Запас сил",
            "Название ресурса способностей",
            lambda parent: self._build_scalar_page(
                parent,
                "Раздел 5",
                "Запас сил",
                "Название запаса сил относится только к этой вселенной.",
                STRENGTH_FIELDS,
            ),
            marker="5",
        )
        self._catalog_editors = build_catalog_views(
            shell,
            lambda: self._draft,
            self._get_global_catalogs,
            self._catalog_changed,
        )
        shell.add_view(
            "review",
            "Готовность",
            "Проверка и публикация",
            self._build_review,
            marker="✓",
        )
        shell.show("overview")

    def _build_scalar_page(self, parent, eyebrow, title, description, fields) -> None:
        form = build_basics_page(parent, eyebrow, title, description)
        section = ttk.LabelFrame(form, text=title, padding=14)
        section.pack(fill="x")
        for field in fields:
            key, label, *kind = field
            self._variables[key] = entry_field(section, label, kind[0] if kind else "text")

    def _build_overview(self, parent: ttk.Frame) -> None:
        build_overview_page(parent)

    def _build_review(self, parent: ttk.Frame) -> None:
        build_review_page(parent, self._preview, self._publish)

    def _catalog_changed(self) -> None:
        self._status.set("Черновик изменён")
        self.after_idle(self._refresh_catalogs)

    def _refresh_catalogs(self) -> None:
        for editor in getattr(self, "_catalog_editors", ()):
            editor.refresh()

    def refresh(self) -> None:
        """Refresh shared-catalog choices after the user returns to the Worlds tab."""
        self._refresh_catalogs()

    def _store_form(self) -> None:
        for key in ("id", "name", "description", "world_rules", "power_systems"):
            setattr(self._draft, key, self._variables[key].get())
        for key in ("currency_id", "currency_name", "currency_symbol", "strength_name"):
            setattr(self._draft.gameplay, key, self._variables[key].get())
        synchronize_shared_catalogs(self._draft, self._get_global_catalogs())

    def _load_form(self) -> None:
        for key in ("id", "name", "description", "world_rules", "power_systems"):
            self._variables[key].set(getattr(self._draft, key))
        for key in ("currency_id", "currency_name", "currency_symbol", "strength_name"):
            self._variables[key].set(str(getattr(self._draft.gameplay, key)))

    def _new(self) -> None:
        self._draft = UniverseDraft()
        self._load_form()
        self._refresh_catalogs()
        self._status.set("Новый черновик")

    def _open(self) -> None:
        result = open_world_dialog(self._get_global_catalogs())
        if result is None:
            return
        self._draft, selected = result
        self._load_form()
        self._refresh_catalogs()
        self._status.set(f"Открыт: {selected}")

    def _save_draft(self) -> None:
        self._store_form()
        path = save_draft_dialog(self._draft)
        if path is not None:
            self._status.set(f"Сохранено: {path}")

    def _publish(self) -> None:
        self._store_form()
        path = publish_dialog(self._draft, self._get_global_catalogs())
        if path is not None:
            self._status.set(f"Опубликовано: {path}")

    def _preview(self) -> None:
        try:
            self._store_form()
            show_preview(self, self._draft, self._get_global_catalogs())
        except ValueError as error:
            messagebox.showerror("Предпросмотр невозможен", str(error))
