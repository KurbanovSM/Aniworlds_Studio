"""Build the authored Naruto v4 draft and immutable upload package from v3."""

# ruff: noqa: RUF001 - Russian authored world content is intentional.

from pathlib import Path

from aniworlds_studio.foundation_export import load_draft, publish_foundation, save_draft
from aniworlds_studio.foundation_models import CharacterDraft, LocationDraft
from aniworlds_studio.global_catalogs import load_global_catalogs

ROOT = Path(__file__).resolve().parents[1]


def profession_for(biography: str) -> str:
    """Give every authored character an explicit short occupation."""
    folded = biography.casefold()
    for marker, profession in (
        ("хокаге", "Хокаге"),
        ("казекаге", "Казекаге"),
        ("цучикаге", "Цучикаге"),
        ("мизукаге", "Мизукаге"),
        ("райкаге", "Райкаге"),
        ("саннин", "Саннин"),
        ("медик", "Медик-ниндзя"),
        ("самура", "Самурай"),
        ("кукловод", "Кукловод"),
        ("мечник", "Мечник"),
        ("учитель академии", "Учитель Академии"),
        ("телохранитель", "Телохранитель"),
        ("стратег", "Военный стратег"),
        ("куноити", "Куноити"),
        ("шиноби", "Шиноби"),
    ):
        if marker in folded:
            return profession
    return "Шиноби"


POSITIONS = {
    "konoha-gates": (170, 300),
    "konoha-center": (290, 300),
    "hokage-residence": (290, 160),
    "training-ground-seven": (160, 440),
    "konoha-hospital": (410, 210),
    "land-of-fire-road": (520, 390),
    "hidden-sand": (820, 560),
    "hidden-rain": (680, 300),
    "akatsuki-hideout": (760, 190),
    "hidden-cloud": (850, 90),
    "hidden-stone": (900, 330),
    "allied-headquarters": (780, 400),
    "fourth-division-front": (800, 500),
    "island-turtle": (970, 80),
    "mountain-graveyard": (960, 500),
    "ichiraku-ramen": (410, 300),
    "uchiha-district": (430, 430),
    "hyuga-estate": (430, 350),
    "nara-forest": (70, 500),
    "ninja-academy": (290, 400),
    "chunin-exam-arena": (290, 500),
    "valley-of-the-end": (520, 560),
    "great-naruto-bridge": (650, 560),
    "tanzaku-town": (520, 230),
    "mount-myoboku": (470, 70),
    "ryuchi-cave": (590, 70),
    "hidden-mist": (700, 80),
    "hidden-grass": (650, 430),
    "land-of-iron": (970, 230),
    "tenchi-bridge": (650, 500),
}

NEW_LOCATIONS = (
    (
        "ichiraku-ramen",
        "Ичираку Рамен",
        "Небольшая раменная в центре Конохи, где встречаются шиноби и жители деревни.",
    ),
    (
        "uchiha-district",
        "Квартал Учиха",
        "Тихий квартал Конохи с полицейским управлением и домами клана Учиха.",
    ),
    (
        "hyuga-estate",
        "Поместье Хьюга",
        "Закрытая территория главной и побочной ветвей клана Хьюга.",
    ),
    (
        "nara-forest",
        "Лес клана Нара",
        "Охраняемый лес с лекарственными растениями и стадами оленей.",
    ),
    (
        "ninja-academy",
        "Академия ниндзя",
        "Учебное здание Конохи с классами, двором и тренировочными площадками.",
    ),
    (
        "chunin-exam-arena",
        "Арена экзамена на чунина",
        "Большая круглая арена для официальных поединков и испытаний.",
    ),
    (
        "valley-of-the-end",
        "Долина Завершения",
        "Ущелье с водопадом и огромными статуями Хаширамы и Мадары.",
    ),
    (
        "great-naruto-bridge",
        "Великий мост Наруто",
        "Мост Страны Волн, соединяющий остров с материком.",
    ),
    ("tanzaku-town", "Город Танзаку", "Оживлённый город гостиниц, рынков и игорных заведений."),
    (
        "mount-myoboku",
        "Гора Мьёбоку",
        "Скрытая земля жаб среди гор, водопадов и исполинских растений.",
    ),
    (
        "ryuchi-cave",
        "Пещера Рьючи",
        "Удалённое священное место змей с запутанными подземными залами.",
    ),
    ("hidden-mist", "Киригакуре", "Деревня Скрытого Тумана на островах Страны Воды."),
    ("hidden-grass", "Кусагакуре", "Пограничная деревня Страны Травы среди лесов и каньонов."),
    ("land-of-iron", "Страна Железа", "Заснеженная страна самураев с укреплёнными крепостями."),
    ("tenchi-bridge", "Мост Тэнти", "Каменный мост в лесистой пограничной области Страны Травы."),
)

CHARACTERS = (
    (
        "iruka-before-pain",
        "Ирука Умино",
        "male",
        26,
        "Учитель Академии, преданный ученикам и Конохе.",
        "ninja-academy",
        ["konoha"],
        ["kind", "responsible"],
    ),
    (
        "kurenai-before-pain",
        "Куренай Юхи",
        "female",
        28,
        "Опытная куноичи и наставница команды Восемь.",
        "konoha-center",
        ["konoha"],
        ["calm", "protective"],
    ),
    (
        "choji-before-pain",
        "Чоджи Акимичи",
        "male",
        18,
        "Добродушный шиноби клана Акимичи, дорожащий друзьями.",
        "konoha-center",
        ["konoha"],
        ["kind", "loyal"],
    ),
    (
        "ino-before-pain",
        "Ино Яманака",
        "female",
        18,
        "Решительная куноичи клана Яманака и специалист по разуму.",
        "konoha-center",
        ["konoha"],
        ["confident", "empathetic"],
    ),
    (
        "shino-before-pain",
        "Шино Абураме",
        "male",
        18,
        "Сдержанный шиноби, сражающийся с помощью насекомых.",
        "konoha-center",
        ["konoha"],
        ["reserved", "observant"],
    ),
    (
        "kiba-before-pain",
        "Киба Инузука",
        "male",
        18,
        "Энергичный следопыт клана Инузука и напарник Акамару.",
        "konoha-center",
        ["konoha"],
        ["energetic", "competitive"],
    ),
    (
        "temari-before-pain",
        "Темари",
        "female",
        19,
        "Расчётливая куноичи Сунагакуре, владеющая боевым веером.",
        "hidden-sand",
        ["sunagakure"],
        ["strategic", "strict"],
    ),
    (
        "kankuro-before-pain",
        "Канкуро",
        "male",
        20,
        "Опытный кукловод Сунагакуре и брат Гаары.",
        "hidden-sand",
        ["sunagakure"],
        ["cautious", "loyal"],
    ),
    (
        "ebisu-before-pain",
        "Эбису",
        "male",
        30,
        "Токубецу-джонин Конохи и наставник молодых шиноби.",
        "ninja-academy",
        ["konoha"],
        ["disciplined", "responsible"],
    ),
    (
        "shizune-before-pain",
        "Шизуне",
        "female",
        28,
        "Помощница Хокаге и квалифицированный медик.",
        "hokage-residence",
        ["konoha"],
        ["responsible", "cautious"],
    ),
    (
        "anko-before-pain",
        "Анко Митараши",
        "female",
        24,
        "Смелая токубецу-джонин с тяжёлым прошлым ученицы Орочимару.",
        "chunin-exam-arena",
        ["konoha"],
        ["brave", "unpredictable"],
    ),
    (
        "genma-before-pain",
        "Генма Ширануи",
        "male",
        30,
        "Спокойный токубецу-джонин и надёжный охранник Конохи.",
        "konoha-gates",
        ["konoha"],
        ["calm", "watchful"],
    ),
    (
        "raido-before-pain",
        "Райдо Намиаши",
        "male",
        31,
        "Опытный телохранитель Хокаге, сохранивший верность деревне.",
        "hokage-residence",
        ["konoha"],
        ["loyal", "disciplined"],
    ),
    (
        "ibiki-before-pain",
        "Ибики Морино",
        "male",
        32,
        "Строгий глава отдела допросов Конохи.",
        "hokage-residence",
        ["konoha"],
        ["strict", "perceptive"],
    ),
    (
        "inoichi-before-pain",
        "Иноичи Яманака",
        "male",
        42,
        "Глава клана Яманака и специалист разведки Конохи.",
        "konoha-center",
        ["konoha"],
        ["perceptive", "responsible"],
    ),
    (
        "shikaku-before-pain",
        "Шикаку Нара",
        "male",
        41,
        "Глава клана Нара и выдающийся стратег.",
        "nara-forest",
        ["konoha"],
        ["strategic", "calm"],
    ),
    (
        "choza-before-pain",
        "Чоза Акимичи",
        "male",
        42,
        "Глава клана Акимичи и ветеран Конохи.",
        "konoha-center",
        ["konoha"],
        ["brave", "loyal"],
    ),
    (
        "hiashi-before-pain",
        "Хиаши Хьюга",
        "male",
        42,
        "Глава клана Хьюга, строгий хранитель его традиций.",
        "hyuga-estate",
        ["konoha"],
        ["authoritative", "strict"],
    ),
    (
        "aoba-before-pain",
        "Аоба Ямаширо",
        "male",
        30,
        "Джонин Конохи, внимательный к деталям и опасностям.",
        "konoha-gates",
        ["konoha"],
        ["observant", "cautious"],
    ),
    (
        "baki-before-pain",
        "Баки",
        "male",
        30,
        "Опытный джонин Сунагакуре и наставник команды Гаары.",
        "hidden-sand",
        ["sunagakure"],
        ["disciplined", "watchful"],
    ),
    (
        "darui-fourth-war",
        "Даруи",
        "male",
        26,
        "Командир дивизии Объединённых сил и правая рука Райкаге.",
        "hidden-cloud",
        ["kumogakure", "allied-shinobi-forces"],
        ["calm", "responsible"],
    ),
    (
        "onoki-fourth-war",
        "Ооноки",
        "male",
        79,
        "Третий Цучикаге, опытный и упрямый ветеран множества войн.",
        "hidden-stone",
        ["iwagakure", "allied-shinobi-forces"],
        ["authoritative", "resolute"],
    ),
    (
        "mei-fourth-war",
        "Мэй Теруми",
        "female",
        31,
        "Пятая Мизукаге, реформирующая Киригакуре после кровавой эпохи.",
        "hidden-mist",
        ["kirigakure", "allied-shinobi-forces"],
        ["authoritative", "determined"],
    ),
    (
        "a-fourth-war",
        "Эй",
        "male",
        47,
        "Четвёртый Райкаге, прямолинейный лидер Кумогакуре.",
        "hidden-cloud",
        ["kumogakure", "allied-shinobi-forces"],
        ["authoritative", "impulsive"],
    ),
    (
        "mifune-fourth-war",
        "Мифунэ",
        "male",
        65,
        "Генерал самураев Страны Железа и союзник армии шиноби.",
        "land-of-iron",
        ["allied-shinobi-forces"],
        ["disciplined", "resolute"],
    ),
    (
        "kitsuchi-fourth-war",
        "Кицучи",
        "male",
        44,
        "Командир дивизии и могучий шиноби Ивагакуре.",
        "fourth-division-front",
        ["iwagakure", "allied-shinobi-forces"],
        ["brave", "responsible"],
    ),
    (
        "kurotsuchi-fourth-war",
        "Куроцучи",
        "female",
        20,
        "Решительная куноичи Ивагакуре и участница Объединённых сил.",
        "hidden-stone",
        ["iwagakure", "allied-shinobi-forces"],
        ["confident", "determined"],
    ),
    (
        "chojuro-fourth-war",
        "Чоджуро",
        "male",
        19,
        "Скромный мечник Киригакуре, охраняющий Мизукаге.",
        "hidden-mist",
        ["kirigakure", "allied-shinobi-forces"],
        ["loyal", "reserved"],
    ),
)


def connect(period, source: str, target: str) -> None:
    links = {entry.location_id: entry for entry in period.location_connections}
    for left, right in ((source, target), (target, source)):
        if right not in links[left].connected_location_ids:
            links[left].connected_location_ids.append(right)


def main() -> None:
    catalogs = load_global_catalogs(ROOT / "content/upload/catalogs/global-catalogs.catalog.json")
    draft = load_draft(ROOT / "content/worlds/naruto-v3.draft.json", catalogs)
    draft.id = "naruto-shinobi-world-v4"
    draft.name = "Наруто: расширенный мир шиноби"
    draft.gameplay.npc_starting_currency_min = 0
    draft.gameplay.npc_starting_currency_max = 10_000
    for location in draft.locations:
        location.map_x, location.map_y = POSITIONS[location.id]
    draft.locations.extend(
        LocationDraft(identifier, name, description, 1.0, *POSITIONS[identifier])
        for identifier, name, description in NEW_LOCATIONS
    )
    new_ids = [identifier for identifier, _, _ in NEW_LOCATIONS]
    next(kind for kind in draft.creature_kinds if kind.id == "human").habitat_location_ids.extend(
        new_ids
    )
    for rule in draft.npc_generation_rules:
        if rule.id in {"common-peace", "common-war"}:
            rule.location_ids.extend(new_ids)
    for period in draft.periods:
        period.location_ids.extend(new_ids)
        period.location_connections.extend(
            type(period.location_connections[0])(identifier, []) for identifier in new_ids
        )
        for source, target in (
            ("konoha-center", "ichiraku-ramen"),
            ("konoha-center", "ninja-academy"),
            ("konoha-center", "uchiha-district"),
            ("konoha-center", "hyuga-estate"),
            ("konoha-center", "nara-forest"),
            ("ninja-academy", "chunin-exam-arena"),
            ("land-of-fire-road", "valley-of-the-end"),
            ("land-of-fire-road", "great-naruto-bridge"),
            ("land-of-fire-road", "tanzaku-town"),
            ("land-of-fire-road", "mount-myoboku"),
            ("land-of-fire-road", "ryuchi-cave"),
            ("land-of-fire-road", "hidden-mist"),
            ("land-of-fire-road", "hidden-grass"),
            ("land-of-fire-road", "land-of-iron"),
            ("hidden-grass", "tenchi-bridge"),
        ):
            connect(period, source, target)
    draft.characters.extend(
        CharacterDraft(
            id=identifier,
            name=name,
            sex=sex,
            age=age,
            biography=biography,
            profession=profession_for(biography),
            origin_location_id=origin,
            creature_kind_id="human",
            trait_ids=traits,
            group_ids=groups,
            period_ids=["fourth-war" if identifier.endswith("fourth-war") else "before-pain"],
        )
        for identifier, name, sex, age, biography, origin, groups, traits in CHARACTERS
    )
    for character in draft.characters:
        character.profession = profession_for(character.biography)
    assert len(draft.locations) == 30
    assert len(draft.characters) == 50
    save_draft(draft, ROOT / "content/worlds/naruto-v4.draft.json")
    publish_foundation(draft, catalogs, ROOT / "content/upload/worlds")


if __name__ == "__main__":
    main()
