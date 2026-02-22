from random import randint

def sell_or_not(offered_price, quantity):
    if randint(1, 100) <= 60:
        print("✅ Продавец согласился!")
        return True
    else:
        print("❌ Продавец отказался.")
        return False