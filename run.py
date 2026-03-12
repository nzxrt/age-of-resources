import os
import sys
import pygame

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import main_game
        print("✅ main_game загружен")
        main_game.run_game()
        print("⚠️ run_game завершилась")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        input("👆 Нажми Enter, чтобы закрыть...")