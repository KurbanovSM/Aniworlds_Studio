"""Visual pages used by the world editor shell."""

# ruff: noqa: RUF001

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from aniworlds_studio.studio_theme import ACCENT, LINE, MUTED, SURFACE, SURFACE_ALT, TEXT
from aniworlds_studio.world_editor_scroll import bind_form_mousewheel
from aniworlds_studio.world_editor_shell import build_page_heading


def build_basics_page(
    parent: ttk.Frame,
    eyebrow: str = "Раздел",
    title: str = "Основное",
    description: str = "Основные значения мира.",
) -> ttk.Frame:
    build_page_heading(
        parent,
        eyebrow,
        title,
        description,
    )
    canvas = tk.Canvas(parent, highlightthickness=0, background="#090a0e")
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    form = ttk.Frame(canvas, padding=(10, 10, 22, 24))
    window = canvas.create_window((0, 0), window=form, anchor="nw")
    form.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    bind_form_mousewheel(form, lambda units: canvas.yview_scroll(units, "units"))
    return form


def build_overview_page(parent: ttk.Frame) -> None:
    build_page_heading(
        parent,
        "Проект мира",
        "Соберите основу мира по шагам",
        "Studio проверит связи и подготовит локальный пакет для ручной загрузки.",
    )
    grid = ttk.Frame(parent)
    grid.pack(fill="both", expand=True)
    preview = _panel(grid)
    preview.pack(side="left", fill="both", expand=True, padx=(0, 8))
    banner = tk.Frame(preview, background="#b68d25", width=170)
    banner.pack(side="left", fill="y")
    banner.pack_propagate(False)
    tk.Label(
        banner,
        text="+",
        background="#b68d25",
        foreground=TEXT,
        font=("Segoe UI Light", 44),
    ).pack(expand=True)
    copy = tk.Frame(preview, background=SURFACE, padx=22, pady=22)
    copy.pack(side="left", fill="both", expand=True)
    _card_label(copy, "КАРТОЧКА ОСНОВЫ", ACCENT, ("Segoe UI Semibold", 9))
    _card_label(copy, "Новая вселенная", TEXT, ("Segoe UI Semibold", 20), pady=(10, 8))
    _card_label(
        copy,
        "Начните с основных правил, затем заполните каждый каталог слева.",
        MUTED,
        ("Segoe UI", 10),
        wraplength=330,
    )
    checklist = _panel(grid, padx=18, pady=18)
    checklist.pack(side="left", fill="both", expand=True, padx=(8, 0))
    _card_label(checklist, "ПОРЯДОК РАБОТЫ", ACCENT, ("Segoe UI Semibold", 9))
    _card_label(
        checklist,
        "Что заполнить",
        TEXT,
        ("Segoe UI Semibold", 17),
        pady=(8, 12),
    )
    for number, text in enumerate(
        (
            "Заполните основные правила вселенной",
            "Настройте периоды, локации и наборы",
            "Добавьте каталоги мира",
            "Проверьте и опубликуйте пакет",
        ),
        start=1,
    ):
        tk.Label(
            checklist,
            text=f"{number}   {text}",
            background=SURFACE_ALT,
            foreground=MUTED,
            anchor="w",
            padx=10,
            pady=9,
        ).pack(fill="x", pady=3)


def build_review_page(
    parent: ttk.Frame,
    preview: Callable[[], None],
    publish: Callable[[], None],
) -> None:
    build_page_heading(
        parent,
        "Финальная проверка",
        "Готовность основы мира",
        "Предпросмотр и публикация используют те же строгие проверки связей и полей.",
    )
    panel = ttk.LabelFrame(parent, text="Проверка структуры", padding=22)
    panel.pack(fill="x")
    ttk.Label(
        panel,
        text=(
            "Сначала откройте предпросмотр. Если ошибок нет, опубликуйте пакет. "
            "Существующий файл Studio молча не перезапишет."
        ),
        style="SurfaceMuted.TLabel",
        wraplength=700,
    ).pack(anchor="w", pady=(0, 18))
    actions = ttk.Frame(panel, style="Surface.TFrame")
    actions.pack(anchor="w")
    ttk.Button(actions, text="Предпросмотр", command=preview).pack(side="left")
    ttk.Button(
        actions,
        text="Опубликовать",
        command=publish,
        style="Primary.TButton",
    ).pack(side="left", padx=(10, 0))


def _panel(parent: ttk.Widget, *, padx: int = 0, pady: int = 0) -> tk.Frame:
    return tk.Frame(
        parent,
        background=SURFACE,
        highlightbackground=LINE,
        highlightthickness=1,
        padx=padx,
        pady=pady,
    )


def _card_label(
    parent: tk.Widget,
    text: str,
    foreground: str,
    font: tuple[str, int] | tuple[str, int, str],
    *,
    pady: tuple[int, int] = (0, 0),
    wraplength: int = 0,
) -> None:
    tk.Label(
        parent,
        text=text,
        background=SURFACE,
        foreground=foreground,
        font=font,
        justify="left",
        wraplength=wraplength,
    ).pack(anchor="w", pady=pady)
