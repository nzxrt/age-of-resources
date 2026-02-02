"""Консольный режим игры. Запуск: python terminal.py"""
from function import (
    sell_resource, buy_resource, zone, government,
    war, show_war, end_war, logistic, country_select,
    form_alliance, break_alliance, farming, discover, production_start,
)
from data import balance, inventory, country

# Основной игровой цикл (консольный)
while True:
    try:
        command = input('-> ').strip()

        if command == ";help":
            print(";sell - продать ресурс  ;buy - купить ресурс")
            print(";balance - баланс  ;inventory - инвентарь")
            print(";zone - зоны  ;government - правительство")
            print(";war - объявить войну  ;show_war - текущие войны  ;end_war - заключить мир")
            print(";alliance - заключить союз  ;break_alliance - расторгнуть союз")
            print(";country_select - выбор страны  ;countryinfo - список стран")
            print(";farming - фермерство  ;discover - изучить ресурс")
            print(";logistic - отправить груз  ;production - производство")
            print(";exit - выход")

        elif command == ";exit":
            print("Выход из игры...")
            break

        elif command == ";sell":
            sell_resource()
        elif command == ";buy":
            buy_resource()
        elif command == ";balance":
            print(f"Ваш баланс: {balance}")
        elif command == ";inventory":
            if inventory:
                for k, v in inventory.items():
                    print(f"  {k}: {v} кг")
            else:
                print("Инвентарь пуст")
        elif command == ";zone":
            zone()
        elif command == ";government":
            government()
        elif command == ";war":
            war()
        elif command == ";show_war":
            show_war()
        elif command == ";end_war":
            end_war()
        elif command == ";alliance":
            form_alliance()
        elif command == ";break_alliance":
            break_alliance()
        elif command == ";country_select":
            country_select()
        elif command == ";countryinfo":
            print(f"Страны: {', '.join(country)}")
        elif command == ";farming":
            farming()
        elif command == ";discover":
            discover()
        elif command == ";logistic":
            logistic()
        elif command == ";production":
            production_start()
        else:
            print(f"Неизвестная команда: {command}. ;help для справки.")

    except EOFError:
        print("Выход из игры...")
        break
    except Exception as e:
        print(f"Ошибка: {e}")
