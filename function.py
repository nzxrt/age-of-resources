import time
from lists import *
from data import *
from random_1 import *
import requests 
import os 
import shutil 
import sys 


def sell_resource():  # функция продажи ресурсов
    global balance, inventory  # ← ОБЯЗАТЕЛЬНО!

    name_of_resource_for_sell = input("Название товара для продажи: -> ")
    if name_of_resource_for_sell == ":sell_coast_rec":
        print(f"Рекомендуемая цена продажи для угля: {Coal_coast}, для железа: {Iron_coast}")
        return
    if name_of_resource_for_sell not in available_resources_for_sell:
        print(f"Ресурс {name_of_resource_for_sell} недоступен для продажи")
        return
    if name_of_resource_for_sell not in inventory or inventory[name_of_resource_for_sell] <=0:
        print(f"У вас нет {name_of_resource_for_sell} для продажи")
        return
    try:
        current_stock = inventory[name_of_resource_for_sell]
        print(f"У вас есть: {current_stock} кг {name_of_resource_for_sell}")

        resource_coast_for_sell = int(input(f"Цена продажи ( за кг ) {name_of_resource_for_sell} -> "))
        quantity_of_resource_for_sell = int(input(f"Количество для продажи ( максимум {current_stock} ) -> "))
        if quantity_of_resource_for_sell > current_stock:
            print("Вы не можете продать больше, чем у вас есть")
            return
        if quantity_of_resource_for_sell <= 0:
            print("Количество должно быть положительным")
            return
        all_coast = quantity_of_resource_for_sell * resource_coast_for_sell
        print(f"Вы продаете: {quantity_of_resource_for_sell} кг {name_of_resource_for_sell} по цене {resource_coast_for_sell}")
        print(f"Общая стоимость: {all_coast} ")
        confirm = input("Напишите ';confirm'")
        if confirm == ";confirm":
            balance += all_coast
            inventory[name_of_resource_for_sell] -= quantity_of_resource_for_sell

            if inventory[name_of_resource_for_sell] == 0:
                del inventory[name_of_resource_for_sell]
            print(f'✅ Вы успешно продали {quantity_of_resource_for_sell} кг {name_of_resource_for_sell}')
            print(f'💰 Ваш баланс: {balance}')
            if name_of_resource_for_sell in inventory:
                print(f'📦 Осталось: {inventory[name_of_resource_for_sell]} кг')

        else:
            print("Продажа отменена")
    except ValueError:
        print("Ошибка: введите число")


def buy_resource(): #функция покупки ресурсов
    global balance, inventory  # ← ОБЯЗАТЕЛЬНО!

    name_of_resource_for_buy = input("Название товара для покупки -> ")
    if name_of_resource_for_buy not in available_resources_for_buy:
        print(f"Ресурс {name_of_resource_for_buy} недоступен для покупки")
        return
    try:
        offered_price = int(input("Предложите цену за кг -> "))
        quantity_of_resource_for_buy = int(input(f"Введите количество для покупки {name_of_resource_for_buy} -> "))
        if quantity_of_resource_for_buy <= 0:
            print("Число должно быть положительным")
            return
        total_cost = offered_price * quantity_of_resource_for_buy
        print(f"Общая стоимость: {total_cost}")
        print("Ожидаем ответа от продавца...")
        seller_agrees = sell_or_not(offered_price, quantity_of_resource_for_buy)
        confirm = input("Если вы удовлетворены ответом продавца, напишите ';confirm'")
        if confirm == ";confirm" and seller_agrees:
            if balance >= total_cost:
                balance -= total_cost
                if name_of_resource_for_buy in inventory:
                    inventory[name_of_resource_for_buy] += quantity_of_resource_for_buy
                else:
                    inventory[name_of_resource_for_buy] = quantity_of_resource_for_buy

                print(f'✅ Вы купили {quantity_of_resource_for_buy} кг {name_of_resource_for_buy} по цене {offered_price} за кг')
                print(f'💰 Баланс: {balance}')
                print(f'📦 Теперь у вас: {inventory[name_of_resource_for_buy]} кг {name_of_resource_for_buy}')
            else:
                print("❌ Недостаточно средств для покупки!")
        elif confirm == ";unconfirm":
            print("Покупка отменена")
        else:
            print("Продавец не согласился или вы не подтвердили")

    except ValueError:
        print("Ошибка: Введите число")

def farming(): #функция высаживания культуры
    where_set = input("Куда вы хотите высадить? (Ферма, Равнина, Поле) -> ")
    where_set = where_set.lower()
    if where_set in farm_zone and available_farm_zone:
        print(f"Что вы хотите высадить на {where_set}? -> ")
        what_set = input("-> ")
        what_set = what_set.lower()
        if what_set in culture_for_farm and available_culture_for_farm:
            print(f"Вы хотите высадить {what_set} на {where_set}")
            if what_set in inventory:
                print(f"{what_set} успешно высажено")
                farm_set = True
            else:
                farm_set = False
        else: 
            print(f"{what_set} нет в доступных ")
    else:
        print(f"{where_set} не подходит для {what_set}")
        farm_set = False

def discover(): #функция изучения ресурсов
    what_discover = input("Что вы хотите изучить? -> ")
    where_discover = input("Где вы хотите изучить? (зона, можно посмотреть через ';zone') -> ")
    how_much_money = int(input("Сколько денег вы хотите потратить на изучение? -> "))
    if how_much_money <= balance:
        #дописать рандомизатор
        print("Вы успешно изучили ресурс")
    else:
        print("Недостаточно денег")

def zone(): #функция просмотра зон
    print("Все доступные зоны: ")
    print("     - Горы")
    print("     - Равнина")
    print("     - Поле")
    print("     - Лес")
    print("     - Море")
    print("     - Лес")
    print("     - Море")

def government(): #правительство
    print("     - 1.Принять закон")
    print("     - 2.Создать закон")
    print("     - 3.Отклонить закон")
    print("     - 4.Инвестировать в регион")
    print("     - 5.Просмотреть законы")
    print("     - 6.Просмотреть инвестиции")
    print("     - 7.Инвестировать в производство")
    government_action = input("Что вы хотите сделать в правителстве? ( Введите цифру ) -> ")
    if government_action == "1":
        action = input(f"Какой закон вы хотите принять {may_laws}? -> ")
    if government_action == "2":
        print("Пример оформления закона:")
        print("Название закона:")
        print("Описание закона:")
        print("Статья закона:")
        print("Время действия закона:")
        print("Наказание в случае нарушения закона:")
        action = input("Введите название закона -> ")
        action = input("Введите описание закона -> ")
        action = input("Введите статью закона -> ")
        action = input("Введите время действия закона -> ")
        action = input("Введите наказание в случае нарушения закона -> ")
        sure = input(f"Вы прделагаете законопроект: {action}. Если вы готовы напишите ';confirm' в противном случае напишите ';unconfirm' -> ")
        if sure == ";confirm":
            may_laws.append(action)
        else:
            print("Вы отказались от внесения законопроекта")
    if government_action == "3":
        action = input(f"Какой законоепроект вы хотите отклонить {may_laws}? -> ")
        may_laws.remove(action)
    if government_action == "4":
        action = input(f"В какой регион вы хотите инвестировать? Доступные регионы: {regions} -> ")
        how_much_money = input("Сколько денег вы хотите инвестировать? -> ")
        if how_much_money <= balance:
            print(f"Вы инвестировали {how_much_money} в {regions[action]}")
            invest.append([regions[action], how_much_money])
    if government_action == "5":
        print(laws)
    if government_action == "6":
        print(invest)            
    if government_action == "7":
        action = input(f"В какое производство вы хотите инвестировать? Доступные производства: {production} -> ")
        how_much_money = input("Сколько денег вы хотите инвестировать? -> ")
        if how_much_money <= balance:
            print(f"Вы инвестировали {how_much_money} в {production[action]}")
            invest.append([production[action], how_much_money])
def production_start():
    action = input(f"На каком производстве и что вы хотите произвести? Доступные производства: {production} -> ")
    what_produce = input(f"Что вы хотите произвести? Доступные товары производства: {available_production} -> ")
    if action in production and what_produce in available_production:
        print(f"Вы начали производство {what_produce} на {action}")
        prodused_on_production.append([action, what_produce])
    else:
        print(f"Вы не можете начать производство {what_produce} на {action}")
def war():
    global in_war, country # Объявляем in_war и country глобальными, если они изменяются

    action = input(f"Кому вы хотите объявить войну? Страны: {country} -> ")

    if action in country:
        if action not in in_war:
            print(f"Вы объявили войну {action}")
            in_war.append(action)
        else:
            print(f"Вы уже ведете войну с {action}!")
    else:
        print(f"Страна {action} не найдена")

def show_war(): 
    print(in_war)

def logistic():
    action1 = input("Что вы хотите отправить? -> ")
    action2 = input("Выберите страну в которую вы хотите доставить -> ")
    if action1 in inventory and action2 in country:
        print(f"Вы отправили {action1} в {action2}")
        inventory.remove(action1)
    else:
        print(f"Вы не можете отправить {action1} в {action2}")
