"""Display options for references between Studio catalog cards."""

from collections.abc import Iterable
from typing import Any


def reference_options(draft: object, source: str) -> tuple[tuple[str, str], ...]:
    """Return display label and stable ID without exposing raw JSON references."""
    values: Iterable[Any]
    if source == "periods":
        values = getattr(draft, "periods", ())
    elif source == "locations":
        values = getattr(draft, "locations", ())
    elif source == "groups":
        values = getattr(draft, "groups", ())
    elif source == "items":
        values = getattr(draft, "items", ())
    elif source == "kinds":
        values = getattr(draft, "creature_kinds", ())
    elif source == "languages":
        values = getattr(draft, "languages", ())
    elif source == "traits":
        values = getattr(draft, "traits", ())
    else:
        return ()
    return tuple((f"{item.name} ({item.id})", item.id) for item in values)


def entry_title(entry: Any, identity_field: str) -> tuple[str, str]:
    identity = str(getattr(entry, identity_field, ""))
    return str(getattr(entry, "name", identity)), identity
