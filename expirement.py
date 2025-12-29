from tabulate import tabulate

# Данные для таблички
data = [
    ["Имя", "Возраст", "Пол"],
    ["Петр", 25, "Мужчина"],
    ["Анастасия", 30, "Женщина"],
    ["Иван", 20, "Мужчина"],
    ["Мария", 28, "Женщина"]
]

# Заголовки столбцов
headers = data[0]
data = data[1:]

# Вывод таблички
print(tabulate(data, headers=headers, tablefmt="grid"))




