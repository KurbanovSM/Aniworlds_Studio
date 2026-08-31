"""Publication checks for complete, scoped generation cards."""

# ruff: noqa: RUF001 - Russian validation messages.

import re

from aniworlds_studio.foundation_models import UniverseDraft


def validate_npc_generation(draft: UniverseDraft) -> None:
    collections = (draft.npc_name_sets, draft.npc_biographies, draft.npc_generation_rules)
    if not any(collections):
        return  # Existing worlds remain readable without fabricated defaults.
    if not all(collections) or len(draft.npc_biographies) > 30:
        raise ValueError("NPC: нужны имена, 1–30 биографий и правила появления.")
    for entries in collections:
        identifiers = [entry.id for entry in entries]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("NPC: повторяется ID карточки.")
        for entry in entries:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry.id) or not entry.name.strip():
                raise ValueError("NPC: у карточки должен быть ID и название.")
    for pool in draft.npc_name_sets:
        for names in (pool.male_names, pool.female_names, pool.surnames):
            if not names or any(not name.strip() or name != name.strip() for name in names):
                raise ValueError("NPC: заполните все три списка без пустых имён.")
            if len({name.casefold() for name in names}) != len(names):
                raise ValueError("NPC: в списке повторяется имя или фамилия.")
        if (
            max(map(len, pool.male_names + pool.female_names)) + 1 + max(map(len, pool.surnames))
            > 20
        ):
            raise ValueError("NPC: сочетание имени и фамилии не должно превышать 20 символов.")
    if any(not b.text.strip() or len(b.text) > 250 for b in draft.npc_biographies):
        raise ValueError("NPC: биография должна содержать от 1 до 250 символов.")
    periods = {p.id: set(p.location_ids) for p in draft.periods}
    kinds = {k.id: k for k in draft.creature_kinds}
    names = {n.id for n in draft.npc_name_sets}
    biographies = {b.id for b in draft.npc_biographies}
    for rule in draft.npc_generation_rules:
        if not (0 <= rule.age_min <= rule.age_max <= 10000 and 1 <= rule.weight <= 100):
            raise ValueError("NPC: неверный возраст или частота появления.")
        if not rule.sexes or not set(rule.sexes) <= {"male", "female"}:
            raise ValueError("NPC: выберите допустимый пол.")
        if rule.role and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", rule.role):
            raise ValueError("NPC: роль — ID латиницей либо пустое поле.")
        if rule.name_set_id not in names or not rule.biography_ids or not rule.trait_ids:
            raise ValueError("NPC: выберите имена, биографии и возможные черты.")
        if not set(rule.biography_ids) <= biographies:
            raise ValueError("NPC: биография не найдена.")
        kind = kinds.get(rule.creature_kind_id)
        if kind is None or not rule.period_ids or not rule.location_ids:
            raise ValueError("NPC: выберите вид, периоды и локации.")
        if not set(rule.period_ids) <= set(kind.period_ids):
            raise ValueError("NPC: вид недоступен в выбранном периоде.")
        if kind.habitat_location_ids and not set(rule.location_ids) <= set(
            kind.habitat_location_ids
        ):
            raise ValueError("NPC: локация не входит в места обитания вида.")
        for period in rule.period_ids:
            if period not in periods or not set(rule.location_ids) <= periods[period]:
                raise ValueError("NPC: локация недоступна в выбранном периоде.")
    for period, locations in periods.items():
        for location in locations:
            fallback = [
                r
                for r in draft.npc_generation_rules
                if not r.role and period in r.period_ids and location in r.location_ids
            ]
            if len(fallback) != 1:
                raise ValueError("NPC: каждой локации периода нужно одно обычное правило без роли.")
