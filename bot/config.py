"""Конфигурация магазина для парсинга"""

class ShopConfig:
    def __init__(self, name: str, supplier_id: int, search_queries: list, categories: list):
        self.name = name
        self.supplier_id = supplier_id
        self.search_queries = search_queries
        self.categories = categories

# Магазин LOWENGRASS
LOWENGRASS = ShopConfig(
    name="LOWENGRASS",
    supplier_id=4424601,
    search_queries=[
        "пароочиститель LOWENGRASS",
        "аэрогриль LOWENGRASS",
        "паровая швабра LOWENGRASS",
        "LOWENGRASS Steam Max",
        "LOWENGRASS Steam Pro"
    ],
    categories=["Пароочистители", "Аэрогрили", "Паровые швабры"]
)

# Активная конфигурация
ACTIVE_SHOP = LOWENGRASS
