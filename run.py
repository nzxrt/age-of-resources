import os
import sys


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        import launcher
        launcher.update_if_needed()

        import main_game
        print("✅ main_game загружен")
        main_game.run_game()
        print("⚠️ run_game завершилась")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        input("👆 Нажми Enter, чтобы закрыть...")