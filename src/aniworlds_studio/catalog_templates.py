"""Editable JSON templates for every complete Studio catalog section."""

# ruff: noqa: RUF001

from dataclasses import asdict

from aniworlds_studio.foundation_models import (
    CharacterDraft,
    CreatureKindDraft,
    GroupDraft,
    ItemDraft,
    LanguageDraft,
    LocationDraft,
    PeriodDraft,
    ShopPolicyDraft,
)
from aniworlds_studio.global_catalogs import CharacterTraitDraft
from aniworlds_studio.npc_generation_models import (
    NpcBiographyDraft,
    NpcGenerationRuleDraft,
    NpcNameSetDraft,
)

CATALOG_SECTIONS = (
    ("npc_name_sets", "Имена новых NPC", NpcNameSetDraft, "id"),
    ("npc_biographies", "Биографии новых NPC", NpcBiographyDraft, "id"),
    ("npc_generation_rules", "Появление новых NPC", NpcGenerationRuleDraft, "id"),
    ("periods", "Периоды", PeriodDraft, "id"),
    ("locations", "Локации", LocationDraft, "id"),
    ("creature_kinds", "Виды и расы", CreatureKindDraft, "id"),
    ("languages", "Языки", LanguageDraft, "id"),
    ("groups", "Объединения", GroupDraft, "id"),
    ("items", "Предметы", ItemDraft, "id"),
    ("shop_policies", "Магазины", ShopPolicyDraft, "shop_kind"),
    ("characters", "Персонажи и NPC", CharacterDraft, "id"),
    ("traits", "Черты характера", CharacterTraitDraft, "id"),
)

CATALOG_HINTS = {
    "npc_name_sets": "Мужские имена, женские имена и фамилии: по одному варианту на строке.",
    "npc_biographies": "Короткие биографии без выдачи способностей и имущества; до 30 карточек.",
    "npc_generation_rules": "Вид, роль, места, периоды и источники для заполнения пропусков.",
    "periods": "Название, описание, лор и начальная ситуация периода.",
    "locations": "Локации создаются отдельно; состав периода и переходы задаются ниже.",
    "groups": "Укажите участников у персонажей; здесь хранятся состояния, места и отношения групп.",
    "creature_kinds": (
        "Доступность, мышление, общение, языки, особенности, места и родительский вид."
    ),
    "languages": "ID, название и наличие устной/письменной формы.",
    "items": "Категория, свойства, ограничения, цена, магазины, вес и предел экземпляров.",
    "shop_policies": "Диапазон первичного ассортимента для магазина или кузницы.",
    "characters": "Анкета, периоды, языки, черты, способности, объединения и лидерство.",
    "traits": "Название, объяснение поведения и несовместимые сочетания.",
}


def new_catalog_entry(field_name: str) -> dict:
    for name, _title, factory, _identity in CATALOG_SECTIONS:
        if name == field_name:
            return asdict(factory())
    raise ValueError(f"Неизвестный раздел каталога: {field_name}")
