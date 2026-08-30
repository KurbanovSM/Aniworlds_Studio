"""Dependency-ordered card sections inside the world editor."""

from collections.abc import Callable
from tkinter import ttk

from aniworlds_studio.catalog_editor import CatalogEditor
from aniworlds_studio.catalog_form_specs import WORLD_GROUP_FIELDS, WORLD_KIND_FIELDS
from aniworlds_studio.foundation_models import UniverseDraft
from aniworlds_studio.period_child_editor import PeriodChildEditor
from aniworlds_studio.period_location_editor import PeriodLocationEditor
from aniworlds_studio.shared_catalog_selection import SharedCatalogSelectionEditor
from aniworlds_studio.world_editor_shell import WorldEditorShell, build_page_heading


def build_catalog_views(
    shell: WorldEditorShell,
    get_draft: Callable[[], UniverseDraft],
    get_global_catalogs,
    on_changed: Callable[[], None],
) -> list:
    """Build sections in the order in which their references become available."""
    editors: list = []
    editors.append(
        _add_catalog(shell, "periods", "Периоды", "Эпохи и ситуации", 6, get_draft, on_changed)
    )
    editors.extend(_add_locations(shell, 7, get_draft, on_changed))
    editors.append(
        _add_catalog(
            shell,
            "shop_policies",
            "Магазины",
            "Ассортимент и кузницы",
            8,
            get_draft,
            on_changed,
        )
    )
    editors.append(
        _add_catalog(
            shell, "items", "Предметы", "Свойства, цены и количество", 9, get_draft, on_changed
        )
    )
    editors.append(_add_kits(shell, 10, get_draft, on_changed))
    editors.append(
        _add_shared(
            shell,
            "creature_kinds",
            "Расы и виды мира",
            "Выбор из общих каталогов",
            11,
            get_draft,
            get_global_catalogs,
            on_changed,
            WORLD_KIND_FIELDS,
        )
    )
    editors.append(
        _add_shared(
            shell,
            "languages",
            "Языки мира",
            "Выбор из общих каталогов",
            12,
            get_draft,
            get_global_catalogs,
            on_changed,
        )
    )
    editors.append(
        _add_shared(
            shell,
            "groups",
            "Объединения мира",
            "Выбор и мировое состояние",
            13,
            get_draft,
            get_global_catalogs,
            on_changed,
            WORLD_GROUP_FIELDS,
        )
    )
    editors.append(
        _add_catalog(
            shell,
            "characters",
            "Персонажи и NPC",
            "Анкеты и знания",
            14,
            get_draft,
            on_changed,
            get_reference_draft=get_global_catalogs,
        )
    )
    return editors


def _add_catalog(
    shell,
    field_name,
    title,
    subtitle,
    number,
    get_draft,
    on_changed,
    get_reference_draft=None,
):
    holder = {}

    def build(parent) -> None:
        build_page_heading(parent, f"Раздел {number}", title, subtitle)
        editor = CatalogEditor(
            parent,
            field_name=field_name,
            identity_field="shop_kind" if field_name == "shop_policies" else "id",
            get_draft=get_draft,
            on_changed=on_changed,
            get_reference_draft=get_reference_draft,
        )
        editor.pack(fill="both", expand=True)
        holder["editor"] = editor

    shell.add_view(field_name, title, subtitle, build, marker=str(number))
    return holder["editor"]


def _add_locations(shell, number, get_draft, on_changed) -> list:
    holder = {}

    def build(parent) -> None:
        build_page_heading(
            parent,
            f"Раздел {number}",
            "Локации",
            "Сначала создайте локации, затем добавьте их в периоды и настройте переходы.",
        )
        panes = ttk.Panedwindow(parent, orient="vertical")
        panes.pack(fill="both", expand=True)
        catalog_host = ttk.Frame(panes)
        period_host = ttk.Frame(panes)
        panes.add(catalog_host, weight=1)
        panes.add(period_host, weight=1)
        catalog = CatalogEditor(
            catalog_host,
            field_name="locations",
            identity_field="id",
            get_draft=get_draft,
            on_changed=on_changed,
        )
        catalog.pack(fill="both", expand=True)
        period = PeriodLocationEditor(period_host, get_draft=get_draft, on_changed=on_changed)
        period.pack(fill="both", expand=True)
        holder["editors"] = [catalog, period]

    shell.add_view("locations", "Локации", "Карта, периоды и переходы", build, marker=str(number))
    return holder["editors"]


def _add_kits(shell, number, get_draft, on_changed):
    holder = {}

    def build(parent) -> None:
        build_page_heading(
            parent,
            f"Раздел {number}",
            "Стартовые наборы",
            "Наборы создаются после предметов и используют только существующий каталог.",
        )
        editor = PeriodChildEditor(
            parent,
            child="starting_kits",
            get_draft=get_draft,
            on_changed=on_changed,
        )
        editor.pack(fill="both", expand=True)
        holder["editor"] = editor

    shell.add_view(
        "starting_kits",
        "Стартовые наборы",
        "От одного до десяти",
        build,
        marker=str(number),
    )
    return holder["editor"]


def _add_shared(
    shell,
    field_name,
    title,
    subtitle,
    number,
    get_draft,
    get_global_catalogs,
    on_changed,
    world_fields=(),
):
    holder = {}

    def build(parent) -> None:
        build_page_heading(parent, f"Раздел {number}", title, subtitle)
        editor = SharedCatalogSelectionEditor(
            parent,
            field_name=field_name,
            get_draft=get_draft,
            get_catalogs=get_global_catalogs,
            on_changed=on_changed,
            world_fields=world_fields,
        )
        editor.pack(fill="both", expand=True)
        holder["editor"] = editor

    shell.add_view(field_name, title, subtitle, build, marker=str(number))
    return holder["editor"]
