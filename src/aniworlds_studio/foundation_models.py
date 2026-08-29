"""Editable Studio models for one published world foundation."""

# ruff: noqa: RUF001

from dataclasses import asdict, dataclass, field
from typing import Any, Final

FOUNDATION_SCHEMA_VERSION: Final = 4
FOUNDATION_ARTIFACT_TYPE: Final = "aniworlds.world_foundation"
MIN_STARTING_KIT_COUNT: Final = 1
MAX_STARTING_KIT_COUNT: Final = 10
MIN_APPEARANCE_FREQUENCY: Final = 1
MAX_APPEARANCE_FREQUENCY: Final = 100


@dataclass(slots=True)
class GameplayConfig:
    currency_id: str = "currency"
    currency_name: str = "Валюта"
    currency_symbol: str = ""
    strength_name: str = "Запас сил"


@dataclass(slots=True)
class LocationDraft:
    id: str = "start"
    name: str = "Стартовая локация"
    description: str = "Описание стартовой локации"
    price_coefficient: float = 1.0


# Old callers used this name while locations were nested in periods.
StartingLocationDraft = LocationDraft


@dataclass(slots=True)
class PeriodConnectionDraft:
    location_id: str
    connected_location_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StartingKitItemDraft:
    item_id: str
    quantity: int = 1


@dataclass(slots=True)
class StartingKitDraft:
    id: str
    name: str
    description: str
    starting_currency_amount: int = 0
    items: list[StartingKitItemDraft] = field(default_factory=list)


def default_starting_kits() -> list[StartingKitDraft]:
    return [StartingKitDraft("kit-1", "Набор 1", "Описание набора")]


@dataclass(slots=True)
class PeriodDraft:
    id: str = "period"
    name: str = "Период"
    description: str = "Краткое описание периода"
    lore: str = "Лор периода"
    initial_situation: str = "Начальная ситуация"
    location_ids: list[str] = field(default_factory=lambda: ["start"])
    starting_location_ids: list[str] = field(default_factory=lambda: ["start"])
    location_connections: list[PeriodConnectionDraft] = field(default_factory=list)
    starting_kits: list[StartingKitDraft] = field(default_factory=default_starting_kits)


@dataclass(slots=True)
class CreatureKindDraft:
    id: str = ""
    name: str = ""
    description: str = ""
    category: str = "race"
    cognition: str = "sapient"
    communication_modes: list[str] = field(default_factory=lambda: ["speech", "writing"])
    default_languages: list[dict[str, Any]] = field(default_factory=list)
    physical_features: list[str] = field(default_factory=list)
    habitat_location_ids: list[str] = field(default_factory=list)
    period_ids: list[str] = field(default_factory=lambda: ["period"])
    parent_kind_id: str | None = None


@dataclass(slots=True)
class LanguageDraft:
    id: str = ""
    name: str = ""
    has_spoken_form: bool = True
    has_written_form: bool = True


@dataclass(slots=True)
class GroupDraft:
    id: str = "group"
    name: str = "Объединение"
    group_type: str = "organization"
    description: str = "Описание объединения"
    location_ids: list[str] = field(default_factory=list)
    ally_ids: list[str] = field(default_factory=list)
    enemy_ids: list[str] = field(default_factory=list)
    period_states: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ItemDraft:
    id: str = "item"
    name: str = "Предмет"
    description: str = "Описание предмета"
    category: str = "common"
    uniqueness: str = "ordinary"
    properties: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    allowed_shop_kinds: list[str] = field(default_factory=list)
    base_price: int = 0
    appearance_weight: int = 1
    maximum_created_instances: int | None = None


@dataclass(slots=True)
class ShopPolicyDraft:
    shop_kind: str = "general_store"
    minimum_assortment_size: int = 1
    maximum_assortment_size: int = 5


@dataclass(slots=True)
class AbilityDraft:
    id: str = "ability"
    name: str = "Способность"
    short_description: str = "Краткое описание"
    description: str = "Полное описание способности"
    kind: str = "ordinary"


@dataclass(slots=True)
class CharacterDraft:
    id: str = "character"
    name: str = "Персонаж"
    sex: str = "male"
    age: int = 18
    biography: str = "Биография персонажа"
    origin_location_id: str = "start"
    creature_kind_id: str = ""
    cognition_override: str | None = None
    trait_ids: list[str] = field(default_factory=list)
    abilities: list[AbilityDraft] = field(default_factory=list)
    group_ids: list[str] = field(default_factory=list)
    leader_group_ids: list[str] = field(default_factory=list)
    period_ids: list[str] = field(default_factory=lambda: ["period"])
    language_knowledge: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class UniverseDraft:
    id: str = "new-universe"
    name: str = "Новая вселенная"
    description: str = "Краткое описание вселенной"
    world_rules: str = "Правила мира"
    power_systems: str = "Системы сил"
    gameplay: GameplayConfig = field(default_factory=GameplayConfig)
    periods: list[PeriodDraft] = field(default_factory=lambda: [PeriodDraft()])
    locations: list[LocationDraft] = field(default_factory=lambda: [LocationDraft()])
    creature_kinds: list[CreatureKindDraft] = field(default_factory=list)
    languages: list[LanguageDraft] = field(default_factory=list)
    groups: list[GroupDraft] = field(default_factory=list)
    items: list[ItemDraft] = field(default_factory=list)
    shop_policies: list[ShopPolicyDraft] = field(default_factory=list)
    characters: list[CharacterDraft] = field(default_factory=list)

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)
