"""Expand Naruto v4 items and author personal resources for every prepared character."""

# ruff: noqa: RUF001 - Russian authored content is intentional.

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from aniworlds_studio.foundation_export import load_draft, publish_foundation, save_draft
from aniworlds_studio.foundation_models import (
    EquipmentDraft,
    ShopPolicyDraft,
    StartingKitItemDraft,
)
from aniworlds_studio.global_catalogs import (
    load_global_catalogs,
    publish_global_catalogs,
    save_global_catalogs,
)

ROOT = Path(__file__).resolve().parents[1]
SECTION_ID = "Narutov4"

MEDICAL_ITEM_IDS = {
    "antidote",
    "bandage",
    "medical-kit",
    "poison-kit",
    "soldier-pill",
}
FOOD_ITEM_IDS = {"ration-pack", "water-flask"}
TOOL_AND_SCROLL_ITEM_IDS = {
    "blank-scroll",
    "chakra-paper",
    "explosive-tag",
    "field-map",
    "ink-set",
    "radio",
    "rope",
    "sealing-scroll",
    "smoke-bomb",
    "spyglass",
    "tool-pouch",
    "wire",
}
GENERAL_STORE_ITEM_IDS = {
    "camping-blanket",
    "field-map",
    "ink-set",
    "ration-pack",
    "rope",
    "tool-pouch",
    "water-flask",
}
WEAPON_SHOP_EXTRA_ITEM_IDS = {"explosive-tag", "smoke-bomb", "tool-pouch", "wire"}
SHOP_POLICIES = (
    ShopPolicyDraft("general_store", 3, 7),
    ShopPolicyDraft("weapon_shop", 3, 8),
    ShopPolicyDraft("armor_shop", 3, 8),
    ShopPolicyDraft("clothing_shop", 3, 8),
    ShopPolicyDraft("pharmacy", 2, 5),
    ShopPolicyDraft("tool_and_scroll_shop", 3, 8),
    ShopPolicyDraft("food_shop", 1, 2),
    ShopPolicyDraft("forge", 3, 8),
)


def _item(
    identifier: str,
    name: str,
    description: str,
    category: str,
    *,
    slot: str | None = None,
    protection: str = "none",
    price: int = 100,
    weight: int = 5,
) -> EquipmentDraft:
    shops = ["forge"] if category in {"weapon", "armor"} else ["general_store"]
    return EquipmentDraft(
        id=identifier,
        name=name,
        description=description,
        category=category,
        properties=[],
        limitations=[],
        allowed_shop_kinds=shops,
        base_price=price,
        appearance_weight=weight,
        equipment_slot=slot,
        protection_level=protection,
        section_id=SECTION_ID,
    )


ADDED_ITEMS = (
    _item(
        "mesh-underlayer",
        "Сетчатое нижнее бельё",
        "Эластичный нижний слой шиноби.",
        "clothing",
        slot="underwear",
        price=80,
    ),
    _item(
        "insulated-underwear",
        "Утеплённое нижнее бельё",
        "Тёплый нижний слой для холодных земель.",
        "clothing",
        slot="underwear",
        price=120,
    ),
    _item(
        "shinobi-bandana",
        "Бандана шиноби",
        "Тканевая повязка без металлической пластины.",
        "clothing",
        slot="head",
        price=60,
    ),
    _item(
        "straw-hat",
        "Соломенная шляпа",
        "Широкая шляпа от солнца и дождя.",
        "clothing",
        slot="head",
        price=45,
    ),
    _item(
        "sand-veil",
        "Пустынная вуаль",
        "Защищает лицо от песка и сухого ветра.",
        "clothing",
        slot="head",
        price=90,
    ),
    _item(
        "hunter-mask",
        "Маска охотника-нина",
        "Прочная маска, скрывающая лицо.",
        "armor",
        slot="head",
        protection="light",
        price=420,
        weight=2,
    ),
    _item(
        "samurai-helmet",
        "Шлем самурая",
        "Тяжёлый металлический шлем Страны Железа.",
        "armor",
        slot="head",
        protection="heavy",
        price=1200,
        weight=2,
    ),
    _item(
        "rain-hood",
        "Капюшон Страны Дождя",
        "Водостойкий глубокий капюшон.",
        "clothing",
        slot="head",
        protection="light",
        price=150,
    ),
    _item(
        "academy-uniform",
        "Форма Академии",
        "Повседневная форма преподавателя или ученика Академии.",
        "clothing",
        slot="torso",
        price=180,
    ),
    _item(
        "medic-coat",
        "Куртка медика",
        "Светлая рабочая куртка с карманами для инструментов.",
        "clothing",
        slot="torso",
        protection="light",
        price=320,
    ),
    _item(
        "anbu-vest",
        "Жилет АНБУ",
        "Защитный жилет для скрытых операций.",
        "armor",
        slot="torso",
        protection="medium",
        price=1350,
        weight=2,
    ),
    _item(
        "akatsuki-cloak",
        "Плащ Акацуки",
        "Чёрный дорожный плащ с красными облаками.",
        "clothing",
        slot="torso",
        protection="light",
        price=900,
        weight=2,
    ),
    _item(
        "sand-robe",
        "Одеяние Сунагакуре",
        "Свободная одежда для жаркого пустынного климата.",
        "clothing",
        slot="torso",
        protection="light",
        price=280,
    ),
    _item(
        "cloud-combat-vest",
        "Боевой жилет Кумогакуре",
        "Плотный жилет шиноби Страны Молнии.",
        "armor",
        slot="torso",
        protection="medium",
        price=1450,
        weight=3,
    ),
    _item(
        "mist-combat-vest",
        "Боевой жилет Киригакуре",
        "Влагостойкий жилет шиноби Тумана.",
        "armor",
        slot="torso",
        protection="medium",
        price=1400,
        weight=3,
    ),
    _item(
        "stone-combat-vest",
        "Боевой жилет Ивагакуре",
        "Усиленный жилет шиноби Камня.",
        "armor",
        slot="torso",
        protection="medium",
        price=1500,
        weight=3,
    ),
    _item(
        "samurai-cuirass",
        "Кираса самурая",
        "Тяжёлая пластинчатая броня Страны Железа.",
        "armor",
        slot="torso",
        protection="heavy",
        price=2600,
        weight=2,
    ),
    _item(
        "noble-kimono",
        "Кимоно главы клана",
        "Качественное официальное кимоно знатного дома.",
        "clothing",
        slot="torso",
        price=700,
        weight=2,
    ),
    _item(
        "training-top",
        "Тренировочная куртка",
        "Лёгкая куртка для тайдзюцу и ежедневных тренировок.",
        "clothing",
        slot="torso",
        protection="light",
        price=240,
    ),
    _item(
        "mesh-shirt",
        "Сетчатая рубаха",
        "Гибкая защитная рубаха под верхнюю одежду.",
        "clothing",
        slot="torso",
        protection="light",
        price=360,
    ),
    _item(
        "medic-gloves",
        "Перчатки медика",
        "Тонкие перчатки для лечения и операций.",
        "clothing",
        slot="hands",
        price=130,
    ),
    _item(
        "armored-gauntlets",
        "Латные перчатки",
        "Тяжёлые перчатки с металлическими пластинами.",
        "armor",
        slot="hands",
        protection="heavy",
        price=900,
        weight=2,
    ),
    _item(
        "chakra-gloves",
        "Чакропроводящие перчатки",
        "Перчатки с проводящей чакру тканью.",
        "armor",
        slot="hands",
        protection="light",
        price=650,
        weight=3,
    ),
    _item(
        "puppet-bracers",
        "Наручи кукловода",
        "Защитные наручи с креплениями для нитей чакры.",
        "armor",
        slot="hands",
        protection="light",
        price=540,
        weight=2,
    ),
    _item(
        "academy-trousers",
        "Штаны Академии",
        "Простые форменные штаны для занятий.",
        "clothing",
        slot="legs",
        price=150,
    ),
    _item(
        "medic-trousers",
        "Штаны медика",
        "Удобные рабочие штаны полевого врача.",
        "clothing",
        slot="legs",
        price=190,
    ),
    _item(
        "combat-shorts",
        "Боевые шорты",
        "Лёгкая одежда, не мешающая быстрым движениям.",
        "clothing",
        slot="legs",
        protection="light",
        price=170,
    ),
    _item(
        "sand-trousers",
        "Пустынные штаны",
        "Свободные штаны из плотной светлой ткани.",
        "clothing",
        slot="legs",
        protection="light",
        price=230,
    ),
    _item(
        "cloud-trousers",
        "Штаны Кумогакуре",
        "Усиленные форменные штаны Страны Молнии.",
        "armor",
        slot="legs",
        protection="light",
        price=420,
    ),
    _item(
        "mist-trousers",
        "Штаны Киригакуре",
        "Влагостойкие форменные штаны Тумана.",
        "armor",
        slot="legs",
        protection="light",
        price=410,
    ),
    _item(
        "stone-trousers",
        "Штаны Ивагакуре",
        "Плотные штаны с защитными вставками.",
        "armor",
        slot="legs",
        protection="medium",
        price=560,
    ),
    _item(
        "samurai-greaves",
        "Поножи самурая",
        "Тяжёлые металлические поножи.",
        "armor",
        slot="legs",
        protection="heavy",
        price=1100,
        weight=2,
    ),
    _item(
        "academy-sandals",
        "Сандалии Академии",
        "Простые сандалии для тренировок.",
        "clothing",
        slot="feet",
        price=90,
    ),
    _item(
        "reinforced-sandals",
        "Усиленные сандалии",
        "Сандалии с защитными накладками.",
        "armor",
        slot="feet",
        protection="light",
        price=280,
    ),
    _item(
        "medic-sandals",
        "Сандалии медика",
        "Мягкая рабочая обувь медика-ниндзя.",
        "clothing",
        slot="feet",
        price=140,
    ),
    _item(
        "samurai-boots",
        "Сапоги самурая",
        "Тяжёлые сапоги с металлической защитой.",
        "armor",
        slot="feet",
        protection="heavy",
        price=950,
        weight=2,
    ),
    _item(
        "desert-boots",
        "Пустынные сапоги",
        "Закрытая обувь для горячего песка.",
        "clothing",
        slot="feet",
        protection="light",
        price=300,
    ),
    _item(
        "mist-boots",
        "Сапоги Киригакуре",
        "Нескользящие водостойкие сапоги.",
        "clothing",
        slot="feet",
        protection="light",
        price=320,
    ),
    _item(
        "senbon",
        "Сэнбон",
        "Тонкие метательные иглы шиноби.",
        "weapon",
        slot="active_weapon",
        price=70,
    ),
    _item(
        "fuma-shuriken",
        "Фума-сюрикен",
        "Крупный складной метательный сюрикен.",
        "weapon",
        slot="active_weapon",
        price=480,
        weight=3,
    ),
    _item(
        "giant-shuriken",
        "Гигантский сюрикен",
        "Тяжёлый метательный клинок большого размера.",
        "weapon",
        slot="active_weapon",
        price=520,
        weight=2,
    ),
    _item(
        "katana",
        "Катана",
        "Длинный меч с однолезвийным клинком.",
        "weapon",
        slot="active_weapon",
        price=900,
        weight=4,
    ),
    _item(
        "wakizashi",
        "Вакидзаси",
        "Короткий меч самурая.",
        "weapon",
        slot="active_weapon",
        price=650,
        weight=3,
    ),
    _item(
        "spear",
        "Копьё",
        "Древковое оружие с металлическим наконечником.",
        "weapon",
        slot="active_weapon",
        price=420,
        weight=4,
    ),
    _item(
        "naginata",
        "Нагината",
        "Длинное древковое оружие самураев.",
        "weapon",
        slot="active_weapon",
        price=1100,
        weight=2,
    ),
    _item(
        "kusarigama",
        "Кусаригама",
        "Серп с длинной цепью и грузом.",
        "weapon",
        slot="active_weapon",
        price=760,
        weight=2,
    ),
    _item(
        "iron-fan",
        "Железный веер",
        "Складной боевой веер с металлическими рёбрами.",
        "weapon",
        slot="active_weapon",
        price=540,
        weight=3,
    ),
    _item(
        "giant-war-fan",
        "Гигантский боевой веер",
        "Большой веер для усиления техник ветра.",
        "weapon",
        slot="active_weapon",
        price=1400,
        weight=2,
    ),
    _item(
        "chakra-blade",
        "Чакроклинок",
        "Клинок из металла, хорошо проводящего чакру.",
        "weapon",
        slot="active_weapon",
        price=1800,
        weight=2,
    ),
    _item(
        "trench-knives",
        "Парные траншейные ножи",
        "Пара коротких чакропроводящих клинков.",
        "weapon",
        slot="active_weapon",
        price=1500,
        weight=2,
    ),
    _item(
        "tonfa",
        "Тонфа",
        "Парное оружие ближнего боя для блоков и ударов.",
        "weapon",
        slot="active_weapon",
        price=460,
        weight=3,
    ),
    _item(
        "nunchaku",
        "Нунчаки",
        "Секционное оружие для мастера тайдзюцу.",
        "weapon",
        slot="active_weapon",
        price=430,
        weight=3,
    ),
    _item(
        "bow",
        "Лук",
        "Дальнобойное оружие со стрелами.",
        "weapon",
        slot="active_weapon",
        price=520,
        weight=3,
    ),
    _item(
        "crossbow",
        "Арбалет",
        "Механическое оружие для точной стрельбы болтами.",
        "weapon",
        slot="active_weapon",
        price=820,
        weight=2,
    ),
    _item(
        "war-hammer",
        "Боевой молот",
        "Тяжёлое ударное оружие.",
        "weapon",
        slot="active_weapon",
        price=720,
        weight=2,
    ),
    _item(
        "combat-claws",
        "Боевые когти",
        "Короткие лезвия, закрепляемые на кистях.",
        "weapon",
        slot="active_weapon",
        price=680,
        weight=2,
    ),
    _item(
        "puppet-blade",
        "Клинок кукловода",
        "Складной клинок для управления через нити чакры.",
        "weapon",
        slot="active_weapon",
        price=880,
        weight=2,
    ),
    _item(
        "paired-short-swords",
        "Комплект коротких мечей",
        "Несколько коротких клинков в общей перевязи.",
        "weapon",
        slot="active_weapon",
        price=1700,
        weight=2,
    ),
    _item("water-flask", "Фляга воды", "Прочная дорожная фляга.", "common", price=35),
    _item("rope", "Моток верёвки", "Крепкая верёвка для пути и ловушек.", "common", price=55),
    _item(
        "sealing-scroll",
        "Свиток запечатывания",
        "Свиток для хранения подготовленных предметов.",
        "common",
        price=280,
    ),
    _item(
        "blank-scroll", "Чистый свиток", "Пустой свиток для записей и печатей.", "common", price=40
    ),
    _item("ink-set", "Набор туши", "Тушь, кисти и небольшая чернильница.", "common", price=75),
    _item(
        "spyglass",
        "Подзорная труба",
        "Складная труба для дальней разведки.",
        "common",
        price=350,
        weight=3,
    ),
    _item(
        "camping-blanket",
        "Походное одеяло",
        "Плотное свёрнутое одеяло для ночлега.",
        "common",
        price=85,
    ),
    _item(
        "tool-pouch",
        "Подсумок шиноби",
        "Поясной подсумок для оружия и инструментов.",
        "common",
        price=110,
    ),
    _item(
        "poison-kit",
        "Набор ядов",
        "Закрытый набор для приготовления и хранения ядов.",
        "consumable",
        price=600,
        weight=2,
    ),
)


OUTFITS = {
    "standard": (
        "shinobi-underwear",
        "forehead-protector",
        "shinobi-jacket",
        "fingerless-gloves",
        "shinobi-trousers",
        "shinobi-sandals",
    ),
    "academy": (
        "shinobi-underwear",
        "shinobi-bandana",
        "academy-uniform",
        "fingerless-gloves",
        "academy-trousers",
        "academy-sandals",
    ),
    "medic": (
        "mesh-underlayer",
        "forehead-protector",
        "medic-coat",
        "medic-gloves",
        "medic-trousers",
        "medic-sandals",
    ),
    "sand": (
        "wrapped-underwear",
        "sand-veil",
        "sand-robe",
        "fingerless-gloves",
        "sand-trousers",
        "desert-boots",
    ),
    "cloud": (
        "mesh-underlayer",
        "forehead-protector",
        "cloud-combat-vest",
        "chakra-gloves",
        "cloud-trousers",
        "reinforced-sandals",
    ),
    "mist": (
        "mesh-underlayer",
        "hunter-mask",
        "mist-combat-vest",
        "fingerless-gloves",
        "mist-trousers",
        "mist-boots",
    ),
    "stone": (
        "insulated-underwear",
        "forehead-protector",
        "stone-combat-vest",
        "armored-gauntlets",
        "stone-trousers",
        "travel-boots",
    ),
    "samurai": (
        "insulated-underwear",
        "samurai-helmet",
        "samurai-cuirass",
        "armored-gauntlets",
        "samurai-greaves",
        "samurai-boots",
    ),
    "akatsuki": (
        "mesh-underlayer",
        "rain-hood",
        "akatsuki-cloak",
        "fingerless-gloves",
        "shinobi-trousers",
        "shinobi-sandals",
    ),
}

WEAPONS = {
    "rock-lee": "nunchaku",
    "might-guy": "nunchaku",
    "killer-b": "paired-short-swords",
    "sasuke-before-pain": "katana",
    "sasuke-fourth-war": "chakra-blade",
    "pain": "chakra-blade",
    "konan": "senbon",
    "obito-fourth-war": "kusarigama",
    "kabuto-fourth-war": "senbon",
    "temari-before-pain": "giant-war-fan",
    "kankuro-before-pain": "puppet-blade",
    "genma-before-pain": "senbon",
    "mifune-fourth-war": "katana",
    "chojuro-fourth-war": "paired-short-swords",
    "jiraiya": "bo-staff",
    "shikaku-before-pain": "trench-knives",
    "darui-fourth-war": "chakra-blade",
    "onoki-fourth-war": "bo-staff",
}

SPECIAL_OUTFITS = {
    "naruto-before-pain": "standard",
    "naruto-fourth-war": "standard",
    "tsunade": "medic",
    "jiraiya": "standard",
    "gaara": "sand",
    "killer-b": "cloud",
    "sasuke-before-pain": "standard",
    "sasuke-fourth-war": "standard",
    "pain": "akatsuki",
    "konan": "akatsuki",
    "obito-fourth-war": "akatsuki",
    "kabuto-fourth-war": "medic",
    "mifune-fourth-war": "samurai",
}


def _outfit_for(character) -> str:
    special = SPECIAL_OUTFITS.get(character.id)
    if special:
        return special
    profession = character.profession.casefold()
    location = character.origin_location_id
    if "медик" in profession:
        return "medic"
    if "учитель" in profession or location == "ninja-academy":
        return "academy"
    if location == "hidden-sand":
        return "sand"
    if location == "hidden-cloud":
        return "cloud"
    if location == "hidden-mist":
        return "mist"
    if location == "hidden-stone":
        return "stone"
    if "самура" in profession or location == "land-of-iron":
        return "samurai"
    return "standard"


def _extras_for(character) -> tuple[str, ...]:
    profession = character.profession.casefold()
    if "медик" in profession or character.id in {"sakura-haruno", "tsunade", "shizune-before-pain"}:
        return ("medical-kit", "bandage", "antidote")
    if "стратег" in profession or character.id in {"shikamaru-nara", "inoichi-before-pain"}:
        return ("field-map", "radio", "blank-scroll")
    if "кукловод" in profession:
        return ("tool-pouch", "poison-kit", "wire")
    if character.origin_location_id in {"land-of-fire-road", "island-turtle"}:
        return ("water-flask", "ration-pack", "camping-blanket")
    return ("tool-pouch", "bandage")


def _money_for(character_id: str) -> int:
    return 300 + int.from_bytes(sha256(character_id.encode()).digest()[:4], "big") % 9701


def _assign_character_resources(draft, item_ids: set[str]) -> None:
    for character in draft.characters:
        equipment = list(OUTFITS[_outfit_for(character)])
        weapon = WEAPONS.get(character.id, "kunai")
        if character.id == "gaara":
            weapon = "iron-fan"
        identifiers = [*equipment, weapon, *_extras_for(character)]
        identifiers = list(dict.fromkeys(identifiers))[:10]
        missing = set(identifiers) - item_ids
        if missing:
            raise ValueError(f"unknown personal items for {character.id}: {sorted(missing)}")
        character.items = [StartingKitItemDraft(item_id, 1) for item_id in identifiers]
        character.starting_currency_amount = _money_for(character.id)


def _shop_kinds_for(item: EquipmentDraft) -> list[str]:
    kinds: list[str] = []
    if item.id in GENERAL_STORE_ITEM_IDS:
        kinds.append("general_store")
    if item.category == "weapon" or item.id in WEAPON_SHOP_EXTRA_ITEM_IDS:
        kinds.append("weapon_shop")
    if item.category == "armor":
        kinds.append("armor_shop")
    if item.category == "clothing":
        kinds.append("clothing_shop")
    if item.id in MEDICAL_ITEM_IDS:
        kinds.append("pharmacy")
    if item.id in TOOL_AND_SCROLL_ITEM_IDS:
        kinds.append("tool_and_scroll_shop")
    if item.id in FOOD_ITEM_IDS:
        kinds.append("food_shop")
    if item.category in {"weapon", "armor"}:
        kinds.append("forge")
    if not kinds:
        kinds.append("general_store")
    return kinds


def main() -> None:
    catalog_path = ROOT / "content/global-catalogs.studio.json"
    world_path = ROOT / "content/worlds/naruto-v4.draft.json"
    catalogs = load_global_catalogs(catalog_path)
    draft = load_draft(world_path, catalogs)
    by_id = {item.id: item for item in catalogs.equipment}
    for item in ADDED_ITEMS:
        by_id[item.id] = item
    catalogs.equipment[:] = sorted(by_id.values(), key=lambda item: (item.section_id, item.id))
    naruto_items = [item for item in catalogs.equipment if item.section_id == SECTION_ID]
    for item in naruto_items:
        item.allowed_shop_kinds = _shop_kinds_for(item)
    category_counts = {
        "wearable": sum(item.category in {"clothing", "armor"} for item in naruto_items),
        "weapon": sum(item.category == "weapon" for item in naruto_items),
        "other": sum(item.category not in {"clothing", "armor", "weapon"} for item in naruto_items),
    }
    if category_counts != {"wearable": 52, "weapon": 25, "other": 20}:
        raise ValueError(f"unexpected Naruto v4 catalog counts: {category_counts}")
    _assign_character_resources(draft, {item.id for item in naruto_items})
    draft.shop_policies = list(SHOP_POLICIES)
    if len(draft.characters) != 50 or any(not character.items for character in draft.characters):
        raise ValueError("every one of the 50 Naruto v4 characters needs personal belongings")

    with TemporaryDirectory(dir=ROOT) as temporary_name:
        temporary = Path(temporary_name)
        saved_catalog = save_global_catalogs(catalogs, temporary)
        published_catalog = publish_global_catalogs(catalogs, temporary)
        saved_world = save_draft(draft, temporary / "naruto-v4.draft.json")
        published_world = publish_foundation(draft, catalogs, temporary)
        saved_catalog.replace(catalog_path)
        published_catalog.replace(ROOT / "content/upload/catalogs/global-catalogs.catalog.json")
        saved_world.replace(world_path)
        published_world.replace(ROOT / "content/upload/worlds/naruto-shinobi-world-v4.world.json")


if __name__ == "__main__":
    main()
