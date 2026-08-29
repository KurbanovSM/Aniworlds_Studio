"""Display options for references between Studio catalog cards."""

from collections.abc import Iterable
from typing import Any

from aniworlds_studio.foundation_models import UniverseDraft


def reference_options(draft: UniverseDraft, source: str) -> tuple[tuple[str, str], ...]:
    """Return display label and stable ID without exposing raw JSON references."""
    values: Iterable[Any]
    if source == "periods":
        values = draft.periods
    elif source == "locations":
        values = draft.locations
    elif source == "groups":
        values = draft.groups
    elif source == "items":
        values = draft.items
    elif source == "kinds":
        values = draft.creature_kinds
    elif source == "languages":
        values = draft.languages
    else:
        return ()
    return tuple((f"{item.name} ({item.id})", item.id) for item in values)


def entry_title(entry: Any, identity_field: str) -> tuple[str, str]:
    identity = str(getattr(entry, identity_field, ""))
    return str(getattr(entry, "name", identity)), identity
