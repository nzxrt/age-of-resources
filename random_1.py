# random_1.py
from random import randint

def sell_or_not(offered_price, quantity):
    # Продавец соглашается с 60% вероятностью
    if randint(1, 100) <= 60:
        print("✅ Продавец согласился!")
        return True
    else:
        print("❌ Продавец отказался.")
        return False