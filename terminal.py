import function
from lists import *
from inventory import *
from random import randint
from random_1 import sell_or_not
from function import *
from data import *


# Глобальные переменные
balance = 15000


# Основной игровой цикл (консольный)
while True:
    try:
        command = input('-> ')

        if command == ";help":
            print("HELP: Для продажи ресурса напишите ;sell")
            print("HELP: Для покупки ресурса напишите ;buy")
            print("HELP: Для просмотра баланса напишите ;balance")
            print("HELP: Для просмотра инвентаря напишите ;resources_inv")
            print("HELP: Для получения информации о стране напишите ;countryinfo")
            print("HELP: Для выбора страны напишите ;country_select")
            print("HELP: Для выхода из игры напишите ;exit")

        elif command == ";exit":
            print("Выход из игры...")
            break

        elif command == ";sell":
            sell_resource()
        elif command == ";buy":
            buy_resource()
        elif command == ";balance":
            print(f"Ваш баланс: {balance}")
        elif command == ";countryinfo":
            print(f"Все доступные страны: {', '.join(country)}")
            print("Чтобы посмотреть информацию об определённой стране, напишите: ;info <имя_страны>")
        elif command == ";zone": # Добавляем вызов функций
            zone()
        elif command == ";government":
            government()
        elif command == ";war":
            war()
        elif command == ";show_war":
            show_war()
        elif command == ";country_select":
            country_select()

        else:
            print(f"Неизвестная команда: {command}. Напишите ;help для справки.")
        if command == ";show_war":
            show_war()
        if command == ";inventory":
            elemets = len(inventory)
            if elemets > 1:
                print(f"Ваше хранилище {inventory}")
            else:
                print("Ваше хранилище пусто")
        elif command == ";logistic":
            logistic()
                
    
    except EOFError:
        print("Выход из игры...")
        break
    except Exception as e:
        print(f"Ошибка при обработке команды: {e}")
