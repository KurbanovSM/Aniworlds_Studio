"""File dialogs and preview windows for the world editor."""

# ruff: noqa: RUF001

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from aniworlds_studio.foundation_export import (
    load_draft,
    preview_foundation,
    publish_foundation,
    save_draft,
)
from aniworlds_studio.foundation_models import UniverseDraft
from aniworlds_studio.foundation_validation import InvalidFoundation


def open_draft_dialog() -> tuple[UniverseDraft, str] | None:
    """Select and load a Studio draft."""
    selected = filedialog.askopenfilename(filetypes=[("Черновик Studio", "*.draft.json")])
    if not selected:
        return None
    try:
        return load_draft(Path(selected)), selected
    except (OSError, ValueError, TypeError) as error:
        messagebox.showerror("Не удалось открыть черновик", str(error))
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


def publish_dialog(draft: UniverseDraft) -> Path | None:
    """Select the local worlds directory and publish one package."""
    selected = filedialog.askdirectory(title="Выберите локальную папку worlds")
    if not selected:
        return None
    try:
        path = publish_foundation(draft, Path(selected))
    except (InvalidFoundation, ValueError, OSError) as error:
        messagebox.showerror("Публикация невозможна", str(error))
        return None
    messagebox.showinfo("Пакет готов", f"Файл создан:\n{path}")
    return path


def show_preview(owner: tk.Misc, draft: UniverseDraft) -> None:
    """Validate and show the exact published JSON without writing it."""
    try:
        text = preview_foundation(draft)
    except (InvalidFoundation, ValueError) as error:
        messagebox.showerror("Предпросмотр невозможен", str(error))
        return
    window = tk.Toplevel(owner)
    window.title("Предпросмотр опубликованного пакета")
    view = tk.Text(window, wrap="none", width=100, height=35)
    view.insert("1.0", text)
    view.configure(state="disabled")
    view.pack(fill="both", expand=True)
