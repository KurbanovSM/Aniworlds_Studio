"""File dialogs and preview windows for the world editor."""

# ruff: noqa: RUF001

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from aniworlds_studio.foundation_export import (
    load_draft,
    load_published_foundation,
    preview_foundation,
    publish_foundation,
    save_draft,
)
from aniworlds_studio.foundation_models import UniverseDraft
from aniworlds_studio.foundation_validation import InvalidFoundation
from aniworlds_studio.global_catalogs import GlobalCatalogDraft


def open_world_dialog(catalogs: GlobalCatalogDraft) -> tuple[UniverseDraft, str] | None:
    """Open either an unfinished draft or a published version-4 world."""
    selected = filedialog.askopenfilename(
        filetypes=[
            ("Миры и черновики Studio", "*.world.json *.draft.json"),
            ("Все JSON", "*.json"),
        ]
    )
    if not selected:
        return None
    try:
        path = Path(selected)
        draft = (
            load_published_foundation(path, catalogs)
            if path.name.endswith(".world.json")
            else load_draft(path, catalogs)
        )
        return draft, selected
    except (OSError, ValueError, TypeError) as error:
        messagebox.showerror("Не удалось открыть мир", str(error))
        return None


def save_draft_dialog(draft: UniverseDraft) -> Path | None:
    """Select a draft path and save it."""
    selected = filedialog.asksaveasfilename(
        title="Сохранить черновик",
        defaultextension=".draft.json",
    )
    if not selected:
        return None
    try:
        return save_draft(draft, Path(selected))
    except (ValueError, OSError) as error:
        messagebox.showerror("Не удалось сохранить", str(error))
        return None


def publish_dialog(draft: UniverseDraft, catalogs: GlobalCatalogDraft) -> Path | None:
    """Select the local worlds directory and publish one package."""
    selected = filedialog.askdirectory(title="Выберите локальную папку worlds")
    if not selected:
        return None
    try:
        path = publish_foundation(draft, catalogs, Path(selected))
    except (InvalidFoundation, ValueError, OSError) as error:
        messagebox.showerror("Публикация невозможна", str(error))
        return None
    messagebox.showinfo("Пакет готов", f"Файл создан:\n{path}")
    return path


def show_preview(
    owner: tk.Misc,
    draft: UniverseDraft,
    catalogs: GlobalCatalogDraft,
) -> None:
    """Validate and show the exact published JSON without writing it."""
    try:
        text = preview_foundation(draft, catalogs)
    except (InvalidFoundation, ValueError) as error:
        messagebox.showerror("Предпросмотр невозможен", str(error))
        return
    window = tk.Toplevel(owner)
    window.title("Предпросмотр опубликованного пакета")
    view = tk.Text(window, wrap="none", width=100, height=35)
    view.insert("1.0", text)
    view.configure(state="disabled")
    view.pack(fill="both", expand=True)
