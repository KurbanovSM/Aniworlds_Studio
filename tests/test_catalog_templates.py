from aniworlds_studio.catalog_templates import CATALOG_SECTIONS, new_catalog_entry


def test_every_catalog_section_has_an_independent_template() -> None:
    first_entries = [new_catalog_entry(section[0]) for section in CATALOG_SECTIONS]
    second_entries = [new_catalog_entry(section[0]) for section in CATALOG_SECTIONS]

    assert all(isinstance(entry, dict) for entry in first_entries)
    assert first_entries == second_entries
    assert all(
        first is not second for first, second in zip(first_entries, second_entries, strict=True)
    )
