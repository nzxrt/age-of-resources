from data import (
    balance, inventory, farm_zone, available_farm_zone,
    culture_for_farm, available_culture_for_farm,
    zones, laws, may_laws, regions, invest, production,
    available_production, in_war,
    available_resources_for_sell, available_resources_for_buy,
    Coal_coast, Iron_coast,
)
from random_1 import sell_or_not

current_country = None


def sell_resource(bordering_countries=None):
    global balance, inventory

    name = input("Название товара для продажи: -> ")
    if name == ":sell_coast_rec":
        print(f"Рекомендуемая цена: уголь {Coal_coast}, железо {Iron_coast}")
        return
    if name not in available_resources_for_sell:
        print(f"Ресурс {name} недоступен для продажи")
        return
    if name not in inventory or inventory.get(name, 0) <= 0:
        print(f"У вас нет {name} для продажи")
        return
    try:
        current_stock = inventory[name]
        print(f"У вас есть: {current_stock} кг {name}")
        price = int(input(f"Цена продажи за кг: -> "))
        qty = int(input(f"Количество (макс {current_stock}): -> "))
        if qty > current_stock or qty <= 0:
            print("Некорректное количество")
            return
        total = qty * price
        print(f"Вы продаёте {qty} кг {name} по {price}. Итого: {total}")
        confirm = input("Напишите ';confirm' для подтверждения: ")
        if confirm == ";confirm":
            seller_agrees = sell_or_not(price, qty)
            if seller_agrees:
                balance += total
                inventory[name] -= qty
                if inventory[name] == 0:
                    del inventory[name]
                print(f"✅ Продано {qty} кг {name}. Баланс: {balance}")
            else:
                print("Покупатель отказался.")
        else:
            print("Продажа отменена")
    except ValueError:
        print("Ошибка: введите число")


def buy_resource(bordering_countries=None):
    global balance, inventory

    name = input("Название товара для покупки: -> ")
    if name not in available_resources_for_buy:
        print(f"Ресурс {name} недоступен для покупки")
        return
    try:
        price = int(input("Предложите цену за кг: -> "))
        qty = int(input("Количество: -> "))
        if qty <= 0:
            print("Количество должно быть положительным")
            return
        total = price * qty
        print(f"Итого: {total}")
        seller_agrees = sell_or_not(price, qty)
        confirm = input("Напишите ';confirm' для подтверждения: ")
        if confirm == ";confirm" and seller_agrees:
            if balance >= total:
                balance -= total
                inventory[name] = inventory.get(name, 0) + qty
                print(f"✅ Куплено {qty} кг {name}. Баланс: {balance}")
            else:
                print("❌ Недостаточно средств")
        else:
            print("Покупка отменена или продавец отказался")
    except ValueError:
        print("Ошибка: введите число")


def farming():
    farm_set = False
    where_set = input("Куда вы хотите высадить? (Ферма, Равнина, Поле): -> ").strip().capitalize()
    if where_set not in farm_zone:
        print(f"{where_set} не подходит для посадки")
        return
    if where_set not in available_farm_zone:
        print(f"{where_set} ещё не освоена")
        return
    what_set = input("Что вы хотите высадить?: -> ").strip().capitalize()
    if what_set not in culture_for_farm:
        print(f"{what_set} нет в доступных культурах")
        return
    if what_set not in available_culture_for_farm:
        print(f"{what_set} ещё не изучена")
        return
    if what_set in inventory and inventory.get(what_set, 0) > 0:
        inventory[what_set] = inventory.get(what_set, 0) - 1
        print(f"{what_set} успешно высажено на {where_set}")
        farm_set = True
    else:
        print(f"Нет семян {what_set}")


def discover():
    global balance
    what = input("Что вы хотите изучить?: -> ")
    where = input("Где? (зона через ;zone): -> ")
    try:
        cost = int(input("Сколько потратить?: -> "))
        if cost > balance:
            print("Недостаточно денег")
            return
        balance -= cost
        if where.lower() in ["равнина", "поле"] and where not in available_farm_zone:
            available_farm_zone.append(where.capitalize())
        if what.lower() in ["пшеница", "морковь", "картофель"] and what not in available_culture_for_farm:
            available_culture_for_farm.append(what.capitalize())
        print("Ресурс изучен!")
    except ValueError:
        print("Ошибка: введите число")


def zone():
    print("Доступные зоны: Горы, Равнина, Поле, Лес, Море")


def government():
    global balance, invest
    import data
    regions = data.regions if isinstance(data.regions, dict) else {"1": "Регион 1", "2": "Регион 2"}
    production = data.production if isinstance(data.production, dict) else {"завод": "Завод", "фабрика": "Фабрика"}
    print("1.Принять закон  2.Создать закон  3.Отклонить закон")
    print("4.Инвестировать в регион  5.Просмотреть законы  6.Просмотреть инвестиции")
    print("7.Инвестировать в производство")
    try:
        action = input("Действие (цифра): -> ")
        if action == "1":
            if may_laws:
                print(f"Законы на рассмотрении: {may_laws}")
                law = input("Какой принять?: -> ")
                if law in may_laws:
                    laws.append(law)
                    may_laws.remove(law)
                    print("Закон принят")
            else:
                print("Нет законов на рассмотрении")
        elif action == "2":
            name = input("Название закона: -> ")
            may_laws.append(name)
            print("Законопроект внесён")
        elif action == "3":
            if may_laws:
                law = input("Какой отклонить?: -> ")
                if law in may_laws:
                    may_laws.remove(law)
                    print("Законопроект отклонён")
        elif action == "4":
            if regions:
                print(f"Регионы: {list(regions.keys())}")
                reg = input("Регион: -> ")
                if reg in regions:
                    try:
                        amt = int(input("Сумма: -> "))
                        if amt <= balance:
                            balance -= amt
                            invest.append([regions[reg], amt])
                            print(f"Инвестировано {amt} в {regions[reg]}")
                        else:
                            print("Недостаточно средств")
                    except ValueError:
                        print("Введите число")
        elif action == "5":
            print("Законы:", laws if laws else "нет")
        elif action == "6":
            print("Инвестиции:", invest if invest else "нет")
        elif action == "7":
            if production:
                print(f"Производства: {list(production.keys())}")
                prod = input("Производство: -> ")
                if prod in production:
                    try:
                        amt = int(input("Сумма: -> "))
                        if amt <= balance:
                            balance -= amt
                            invest.append([production[prod], amt])
                            print(f"Инвестировано {amt} в {production[prod]}")
                        else:
                            print("Недостаточно средств")
                    except ValueError:
                        print("Введите число")
    except (ValueError, KeyError):
        print("Ошибка ввода")


def production_start():
    if production and available_production:
        print(f"Производства: {production}, Товары: {available_production}")
        prod = input("Производство: -> ")
        prod_name = input("Что производить: -> ")
        if prod in production and prod_name in available_production:
            prodused_on_production.append([prod, prod_name])
            print(f"Производство {prod_name} на {prod} начато")
        else:
            print("Неверные данные")
    else:
        print("Нет доступных производств")


def war():
    global in_war
    from data import country
    print(f"Страны: {country}")
    target = input("Кому объявить войну?: -> ")
    if target in country:
        if target not in in_war:
            in_war.append(target)
            print(f"Война объявлена {target}")
        else:
            print(f"Уже в войне с {target}")
    else:
        print("Страна не найдена")


def show_war():
    print("Войны:", in_war if in_war else "нет")


def end_war():
    global in_war
    from data import country
    if not in_war:
        print("Вы не ведёте войн")
        return
    print(f"Текущие войны: {in_war}")
    target = input("С кем заключить мир?: -> ")
    if target in in_war:
        in_war.remove(target)
        print(f"Мир заключён с {target}")
    else:
        print("Страна не найдена в списке войн")


def logistic():
    global inventory
    from data import country
    if not isinstance(inventory, dict):
        print("Инвентарь повреждён")
        return
    res = input("Что отправить?: -> ")
    if res not in inventory or inventory.get(res, 0) <= 0:
        print(f"Нет {res} в инвентаре")
        return
    try:
        qty = int(input("Количество: -> "))
        if qty <= 0 or qty > inventory.get(res, 0):
            print("Некорректное количество")
            return
        target = input("В какую страну?: -> ")
        if target in country and target != current_country:
            inventory[res] -= qty
            if inventory[res] == 0:
                del inventory[res]
            print(f"Отправлено {qty} кг {res} в {target}")
        else:
            print("Страна не найдена")
    except ValueError:
        print("Введите число")


def country_select():
    global current_country
    from data import country
    print(f"Доступные страны: {country}")
    choice = input("Выберите страну: -> ")
    if choice in country:
        current_country = choice
        print(f"Вы играете за {choice}")
    else:
        print("Страна не найдена")


def form_alliance():
    import data
    from data import country
    if not hasattr(data, "alliances"):
        data.alliances = []
    print(f"Страны: {country}")
    target = input("С кем заключить союз?: -> ")
    if target in country and target != current_country:
        if target not in data.alliances:
            data.alliances.append(target)
            print(f"Союз с {target} заключён")
        else:
            print("Уже в союзе с этой страной")
    else:
        print("Страна не найдена")


def break_alliance():
    import data
    allies = data.alliances if hasattr(data, "alliances") else []
    if not allies:
        print("Нет союзов")
        return
    print(f"Союзники: {allies}")
    target = input("С кем расторгнуть союз?: -> ")
    if target in allies:
        data.alliances.remove(target)
        print(f"Союз с {target} расторгнут")
    else:
        print("Страна не найдена")
