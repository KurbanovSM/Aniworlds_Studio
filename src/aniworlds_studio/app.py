"""Tkinter desktop interface for the offline promo-code exporter."""

import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from aniworlds_studio.clipboard_shortcuts import install_clipboard_shortcuts
from aniworlds_studio.global_settings_editor import GlobalSettingsFrame
from aniworlds_studio.promo_export import (
    MAX_ACTIVATIONS,
    MAX_TURNS,
    MIN_ACTIVATIONS,
    MIN_TURNS,
    InvalidPromoExport,
    PromoExport,
    build_subscription_promo,
    build_turn_promo,
    export_promo,
    generate_promo_code,
)
from aniworlds_studio.shared_catalogs_editor import SharedCatalogsFrame
from aniworlds_studio.studio_theme import configure_studio_theme
from aniworlds_studio.window_layout import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MINIMUM_WINDOW_HEIGHT,
    MINIMUM_WINDOW_WIDTH,
    fitted_window_size,
)
from aniworlds_studio.world_editor import WorldEditorFrame


class PromoStudioApp:
    """Small offline UI that exposes only product-approved editable values."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._code = tk.StringVar(value=generate_promo_code())
        self._subscription_activations = tk.StringVar(value="10")
        self._turns = tk.StringVar(value="10")
        self._turn_activations = tk.StringVar(value="10")
        self._expiration = tk.StringVar()
        self._status = tk.StringVar(value="Готово к созданию файла")
        self._configure_window()
        self._build_layout()
        self._root.after_idle(self._fit_window_to_content)

    def _configure_window(self) -> None:
        self._root.title("Aniworlds Studio")
        self._root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self._root.minsize(MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT)
        self._root.option_add("*Font", ("Segoe UI", 10))
        install_clipboard_shortcuts(self._root)
        configure_studio_theme(self._root)

    def _build_layout(self) -> None:
        container = ttk.Frame(self._root)
        container.pack(fill="both", expand=True)
        header = ttk.Frame(container, padding=(22, 12))
        header.pack(fill="x")
        ttk.Label(header, text="AW", style="Accent.TLabel").pack(side="left", padx=(0, 12))
        brand = ttk.Frame(header)
        brand.pack(side="left")
        ttk.Label(brand, text="Aniworlds Studio", font=("Segoe UI Semibold", 16)).pack(anchor="w")
        ttk.Label(
            brand,
            text="Автономный редактор · без подключения к VPS",
            style="Muted.TLabel",
        ).pack(anchor="w")
        ttk.Separator(container).pack(fill="x")
        sections = ttk.Notebook(container)
        sections.pack(fill="both", expand=True)
        sections.add(GlobalSettingsFrame(sections), text="Глобальные настройки")
        shared_catalogs = SharedCatalogsFrame(sections)
        sections.add(shared_catalogs, text="Общие каталоги")
        world_editor = WorldEditorFrame(
            sections,
            get_global_catalogs=lambda: shared_catalogs.catalogs,
        )
        sections.add(world_editor, text="Миры")
        sections.bind("<<NotebookTabChanged>>", lambda _event: world_editor.refresh())
        promo = ttk.Frame(sections, padding=24)
        sections.add(promo, text="Промокоды")
        self._build_code_row(promo)
        tabs = ttk.Notebook(promo)
        tabs.pack(fill="both", expand=True, pady=(12, 0))
        subscription_tab = ttk.Frame(tabs, padding=(20, 16))
        turns_tab = ttk.Frame(tabs, padding=(20, 16))
        tabs.add(subscription_tab, text="Подписка")
        tabs.add(turns_tab, text="Ходы")
        self._build_subscription_tab(subscription_tab)
        self._build_turns_tab(turns_tab)
        ttk.Label(promo, textvariable=self._status).pack(anchor="w", pady=(8, 0))

    def _build_code_row(self, parent: ttk.Frame) -> None:
        row = ttk.LabelFrame(parent, text="Автоматический код", padding=12)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self._code, state="readonly", width=24).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(row, text="Новый код", command=self._replace_code).pack(
            side="left", padx=(12, 0), ipadx=8, ipady=4
        )

    def _build_subscription_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="Промокод выдаёт один стандартный период подписки Aniworlds AI.",
            wraplength=560,
        ).pack(anchor="w", pady=(0, 16))
        self._add_number_field(
            parent,
            "Количество активаций",
            self._subscription_activations,
            MIN_ACTIVATIONS,
            MAX_ACTIVATIONS,
        )
        ttk.Label(
            parent,
            text="Другие параметры подписки здесь не редактируются.",
        ).pack(anchor="w", pady=(8, 22))
        ttk.Button(
            parent,
            text="Сохранить промокод подписки",
            command=self._save_subscription,
            style="Primary.TButton",
        ).pack(anchor="w", pady=(2, 0))

    def _build_turns_tab(self, parent: ttk.Frame) -> None:
        self._add_number_field(parent, "Количество ходов", self._turns, MIN_TURNS, MAX_TURNS)
        self._add_number_field(
            parent,
            "Количество активаций",
            self._turn_activations,
            MIN_ACTIVATIONS,
            MAX_ACTIVATIONS,
        )
        ttk.Label(parent, text="Окончание действия, необязательно (ISO 8601)").pack(
            anchor="w", pady=(10, 4)
        )
        ttk.Entry(parent, textvariable=self._expiration, width=40).pack(anchor="w")
        ttk.Label(parent, text="Пример: 2027-01-01T00:00:00+03:00").pack(anchor="w", pady=(4, 18))
        ttk.Button(
            parent,
            text="Сохранить промокод ходов",
            command=self._save_turns,
            style="Primary.TButton",
        ).pack(anchor="w", pady=(2, 0))

    @staticmethod
    def _add_number_field(
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        minimum: int,
        maximum: int,
    ) -> None:
        ttk.Label(parent, text=label).pack(anchor="w", pady=(0, 4))
        ttk.Spinbox(parent, from_=minimum, to=maximum, textvariable=variable, width=12).pack(
            anchor="w", pady=(0, 8)
        )

    def _replace_code(self) -> None:
        self._code.set(generate_promo_code())
        self._status.set("Создан новый код")

    def _fit_window_to_content(self) -> None:
        """Keep controls visible when Windows applies display scaling."""
        self._root.update_idletasks()
        current_width = self._root.winfo_width()
        current_height = self._root.winfo_height()
        width, height, minimum_width, minimum_height = fitted_window_size(
            current_width,
            current_height,
            self._root.winfo_reqwidth(),
            self._root.winfo_reqheight(),
        )
        self._root.minsize(minimum_width, minimum_height)
        if width != current_width or height != current_height:
            self._root.geometry(f"{width}x{height}")

    def _save_subscription(self) -> None:
        self._save(
            lambda: build_subscription_promo(
                int(self._subscription_activations.get()),
                code=self._code.get(),
            )
        )

    def _save_turns(self) -> None:
        self._save(
            lambda: build_turn_promo(
                int(self._turns.get()),
                int(self._turn_activations.get()),
                expires_at=self._expiration.get(),
                code=self._code.get(),
            )
        )

    def _save(self, build: Callable[[], PromoExport]) -> None:
        try:
            promo = build()
        except (InvalidPromoExport, ValueError) as error:
            messagebox.showerror("Проверьте значения", str(error))
            return
        selected = filedialog.askdirectory(title="Выберите папку для файла промокода")
        if not selected:
            return
        try:
            path = export_promo(promo, Path(selected))
        except FileExistsError:
            messagebox.showerror("Файл уже существует", "Создайте новый код и повторите экспорт.")
            return
        except OSError as error:
            messagebox.showerror("Не удалось сохранить файл", str(error))  # noqa: RUF001
            return
        self._status.set(f"Сохранено: {path}")
        messagebox.showinfo("Промокод сохранён", f"Файл создан:\n{path}")


def main() -> None:
    root = tk.Tk()
    PromoStudioApp(root)
    root.mainloop()
