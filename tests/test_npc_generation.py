from pathlib import Path

import pytest

from aniworlds_studio.foundation_export import (
    load_draft,
    load_published_foundation,
    publication_payload,
    universe_from_mapping,
)
from aniworlds_studio.global_catalogs import load_global_catalogs
from aniworlds_studio.npc_generation_forms import NPC_FORM_SPECS
from aniworlds_studio.npc_generation_validation import validate_npc_generation

ROOT = Path(__file__).parents[1]


def test_authored_naruto_generation_cards_round_trip_and_publish() -> None:
    catalogs = load_global_catalogs(ROOT / "content/global-catalogs.studio.json")
    draft = load_draft(ROOT / "content/drafts/naruto-npc-generation.draft.json", catalogs)

    validate_npc_generation(draft)
    assert len(draft.npc_name_sets[0].male_names) == 50
    assert len(draft.npc_name_sets[0].female_names) == 50
    assert len(draft.npc_name_sets[0].surnames) == 50
    restored = universe_from_mapping(draft.to_mapping())
    assert restored.npc_generation_rules == draft.npc_generation_rules
    universe = publication_payload(draft, catalogs)["universe"]
    assert universe["npc_generation_rules"] and universe["npc_biographies"]
    restored_release = load_published_foundation(
        ROOT / "content/releases/npc-generation/naruto-shinobi-world-v2.world.json", catalogs
    )
    assert restored_release.npc_name_sets == draft.npc_name_sets


def test_generation_cards_require_one_location_fallback() -> None:
    catalogs = load_global_catalogs(ROOT / "content/global-catalogs.studio.json")
    draft = load_draft(ROOT / "content/drafts/naruto-npc-generation.draft.json", catalogs)
    draft.npc_generation_rules = [r for r in draft.npc_generation_rules if r.id != "common-peace"]

    with pytest.raises(ValueError, match="одно обычное правило"):
        validate_npc_generation(draft)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.npc_name_sets.clear(),
        lambda d: setattr(d.npc_biographies[1], "id", d.npc_biographies[0].id),
        lambda d: setattr(d.npc_biographies[0], "id", "Bad ID"),
        lambda d: d.npc_name_sets[0].male_names.clear(),
        lambda d: d.npc_name_sets[0].male_names.append(d.npc_name_sets[0].male_names[0]),
        lambda d: d.npc_name_sets[0].male_names.append("x" * 20),
        lambda d: setattr(d.npc_biographies[0], "text", ""),
        lambda d: setattr(d.npc_generation_rules[0], "age_min", 10001),
        lambda d: d.npc_generation_rules[0].sexes.clear(),
        lambda d: setattr(d.npc_generation_rules[0], "role", "Bad role"),
        lambda d: setattr(d.npc_generation_rules[0], "name_set_id", "missing"),
        lambda d: setattr(d.npc_generation_rules[0], "creature_kind_id", "missing"),
        lambda d: d.npc_generation_rules[0].period_ids.append("missing"),
        lambda d: d.npc_generation_rules[0].location_ids.append("hidden-cloud"),
        lambda d: d.npc_generation_rules[0].biography_ids.append("missing"),
    ],
)
def test_invalid_generation_card_is_rejected(mutate) -> None:
    catalogs = load_global_catalogs(ROOT / "content/global-catalogs.studio.json")
    draft = load_draft(ROOT / "content/drafts/naruto-npc-generation.draft.json", catalogs)
    mutate(draft)

    with pytest.raises(ValueError):
        validate_npc_generation(draft)


def test_all_three_generation_card_forms_are_declared() -> None:
    assert set(NPC_FORM_SPECS) == {
        "npc_name_sets", "npc_biographies", "npc_generation_rules",
    }
