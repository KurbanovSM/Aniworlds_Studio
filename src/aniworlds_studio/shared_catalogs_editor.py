"""Reusable authoring catalogs selected by individual worlds."""

# ruff: noqa: RUF001

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from aniworlds_studio.catalog_editor import CatalogEditor
from aniworlds_studio.catalog_form_specs import GLOBAL_CATALOG_FORM_SPECS
from aniworlds_studio.global_catalogs import (
    GLOBAL_CATALOG_FILE_NAME,
    GlobalCatalogDraft,
    load_global_catalogs,
    load_initial_global_catalogs,
    preview_global_catalogs,
    publish_global_catalogs,
    replace_global_catalog_entries,
    save_global_catalogs,
)


class SharedCatalogsFrame(ttk.Frame):
    """Edit shared content referenced by every authored world."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._catalogs = load_initial_global_catalogs()
        self._editors: list[CatalogEditor] = []
        self._status = tk.StringVar(value="Каталоги ещё не сохранены")
        self._build()

    @property
    def catalogs(self) -> GlobalCatalogDraft:
        return self._catalogs

    def _build(self) -> None:
        ttk.Label(self, text="ОБЩИЕ КАТАЛОГИ", style="Accent.TLabel").pack(anchor="w")
        ttk.Label(self, text="Данные для добавления в миры", font=("Segoe UI Semibold", 24)).pack(
            anchor="w", pady=(4, 4)
        )
        ttk.Label(
            self,
            text=(
                "Основная карточка создаётся здесь один раз. В мире выбирается нужная "
                "запись и настраиваются только периоды, локации и другие мировые связи."
            ),
            style="Muted.TLabel",
            wraplength=900,
        ).pack(anchor="w", pady=(0, 14))
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True)
        for field_name, title in (
            ("creature_kinds", "Расы и виды"),
            ("languages", "Языки"),
            ("groups", "Объединения"),
            ("traits", "Черты характера"),
        ):
            page = ttk.Frame(tabs, padding=8)
            tabs.add(page, text=title)
            editor = CatalogEditor(
                page,
                field_name=field_name,
                identity_field="id",
                get_draft=lambda: self._catalogs,
                on_changed=self._changed,
                fields=GLOBAL_CATALOG_FORM_SPECS[field_name],
                replace_entries=replace_global_catalog_entries,
            )
            editor.pack(fill="both", expand=True)
            self._editors.append(editor)
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(12, 0))
        ttk.Button(controls, text="Открыть каталоги", command=self._load).pack(side="left")
        ttk.Button(
            controls,
            text="Сохранить общие каталоги",
            command=self._save,
        ).pack(side="left", padx=8)
        ttk.Button(controls, text="Предпросмотр", command=self._preview).pack(side="left")
        ttk.Button(
            controls,
            text="Опубликовать для сервера",
            style="Primary.TButton",
            command=self._publish,
        ).pack(side="left", padx=8)
        ttk.Label(controls, textvariable=self._status, style="Muted.TLabel").pack(side="left")

    def _changed(self) -> None:
        self._status.set("Общие каталоги изменены")

    def _save(self) -> None:
        selected = filedialog.askdirectory(title="Выберите папку для общих каталогов")
        if not selected:
            return
        target = Path(selected) / GLOBAL_CATALOG_FILE_NAME
        replace = target.exists() and messagebox.askyesno(
            "Заменить общие каталоги?",
            "В выбранной папке уже есть файл общих каталогов. Заменить его?",
        )
        if target.exists() and not replace:
            return
        try:
            path = save_global_catalogs(self._catalogs, Path(selected), replace_existing=replace)
        except (ValueError, OSError) as error:
            messagebox.showerror("Не удалось сохранить", str(error))
            return
        self._status.set(f"Сохранено: {path}")

    def _load(self) -> None:
        selected = filedialog.askopenfilename(
            title="Откройте черновик или опубликованные общие каталоги",
            filetypes=(("Общие каталоги", "*.json"),),
        )
        if not selected:
            return
        try:
            self._catalogs = load_global_catalogs(Path(selected))
        except (ValueError, OSError) as error:
            messagebox.showerror("Не удалось открыть", str(error))
            return
        for editor in self._editors:
            editor.refresh()
        self._status.set(f"Открыто: {selected}")

    def _preview(self) -> None:
        try:
            text = preview_global_catalogs(self._catalogs)
        except ValueError as error:
            messagebox.showerror("Предпросмотр невозможен", str(error))
            return
        window = tk.Toplevel(self)
        window.title("Предпросмотр общих каталогов для сервера")
        view = tk.Text(window, wrap="none", width=100, height=35)
        view.insert("1.0", text)
        view.configure(state="disabled")
        view.pack(fill="both", expand=True)

    def _publish(self) -> None:
        selected = filedialog.askdirectory(title="Выберите локальную папку catalogs")
        if not selected:
            return
        try:
            path = publish_global_catalogs(self._catalogs, Path(selected))
        except (ValueError, OSError) as error:
            messagebox.showerror("Публикация невозможна", str(error))
            return
        self._status.set(f"Опубликовано: {path}")
        messagebox.showinfo("Каталоги готовы", f"Файл создан:\n{path}")
