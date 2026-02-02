"""Единый источник игровых данных."""
from tabulate import tabulate

# Баланс и инвентарь — управляются через game_state, здесь только начальные значения
balance = 15000
inventory = {}

farm_zone = ["Равнина", "Поле", "Ферма"]
available_farm_zone = ["Равнина", "Поле"]  # по мере изучения добавлять
culture_for_farm = ["Пшеница", "Морковь", "Картофель"]
available_culture_for_farm = ["Пшеница", "Морковь", "Картофель"]
zones = ["Горы", "Равнина", "Поле", "Лес", "Море"]
resources = ["Камень", "Железная руда", "Уголь", "Дерево", "Песок"]

laws = []
may_laws = []
regions = {"север": "Северный регион", "юг": "Южный регион", "восток": "Восточный регион"}
invest = []
production = {"завод": "Завод металлов", "фабрика": "Текстильная фабрика"}
alliances = []
available_production = ["Металл", "Ткань"]
prodused_on_production = []
in_war = []

# Ресурсы для торговли (англ. названия для совместимости)
available_resources_for_sell = ["Coal", "Iron", "Stone", "Wood", "Wheat", "Carrot", "Potato"]
available_resources_for_buy = ["Coal", "Iron", "Stone", "Wood", "Wheat", "Carrot", "Potato"]
Coal_coast = 50
Iron_coast = 120
Stone_coast = 30
Wood_coast = 40
country = ["Россия", "США", "Китай", "Германия", "Франция"]


def table_of_country(countries_data: list) -> str:
    """Отображает информацию о странах в виде таблицы."""
    if not countries_data:
        return "Нет данных"
    headers = ["Страна", "Территории", "Баланс", "Альянсы", "Войны"]
    return tabulate(countries_data, headers=headers, tablefmt="grid")
