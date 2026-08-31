"""Editable universe-owned sources; no built-in lore or identity pools."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class NpcNameSetDraft:
    id: str = "names"
    name: str = "Имена и фамилии"
    male_names: list[str] = field(default_factory=list)
    female_names: list[str] = field(default_factory=list)
    surnames: list[str] = field(default_factory=list)


@dataclass(slots=True)
class NpcBiographyDraft:
    id: str = "biography"
    name: str = "Биография"
    text: str = ""


@dataclass(slots=True)
class NpcGenerationRuleDraft:
    id: str = "npc-rule"
    name: str = "Правило появления NPC"
    role: str = ""
    period_ids: list[str] = field(default_factory=list)
    location_ids: list[str] = field(default_factory=list)
    creature_kind_id: str = ""
    weight: int = 1
    age_min: int = 18
    age_max: int = 60
    sexes: list[str] = field(default_factory=lambda: ["male", "female"])
    name_set_id: str = ""
    biography_ids: list[str] = field(default_factory=list)
    trait_ids: list[str] = field(default_factory=list)


NPC_BUILDERS = {
    "npc_name_sets": NpcNameSetDraft,
    "npc_biographies": NpcBiographyDraft,
    "npc_generation_rules": NpcGenerationRuleDraft,
}
