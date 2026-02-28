import os
import requests
from packaging.version import Version
import json
import shutil
import tempfile
import zipfile
import subprocess
import sys
import time

REPO_OWNER = "ELC-901"
REPO_NAME = "age-of-resources"
BRANCH = "main"
GITHUB_RELEASES_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

def get_github_headers():
    headers = {'Accept': 'application/vnd.github.v3+json'}
    return headers

def get_current_version(version_file="version.txt"):
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "1.0.0"
def get_latest_release_info():
    try:
        response = requests.get(GITHUB_RELEASES_API, headers=get_github_headers())
        response.raise_for_status()
        release_info = response.json()
        return release_info
    except requests.exceptions.RequestException as e:
        error_message = f"Ошибка при получении информации о релизе с GitHub: {e}"
        if e.response is not None:
            error_message += f" (Status: {e.response.status_code})"
        print(error_message)
        return None

FOLDERS_TO_PRESERVE = ["saves", "configs"]

def backup_folders(temp_dir, folders_to_preserve):
    print("Создание резервных копий важных папок...")
    for folder in folders_to_preserve:
        if os.path.exists(folder):
            try:
                shutil.move(folder, os.path.join(temp_dir, folder))
                print(f"Папка '{folder}' успешно скопирована в '{temp_dir}'.")
            except shutil.Error as e:
                print(f"Ошибка при копировании папки '{folder}': {e}")
        else:
            print(f"Папка '{folder}' не найдена, пропускаю резервное копирование.")

def restore_folders(temp_dir, folders_to_preserve):
    print("Восстановление важных папок...")
    for folder in folders_to_preserve:
        temp_folder_path = os.path.join(temp_dir, folder)
        if os.path.exists(temp_folder_path):
            try:
                shutil.move(temp_folder_path, folder)
                print(f"Папка '{folder}' успешно восстановлена из '{temp_dir}'.")
            except shutil.Error as e:
                print(f"Ошибка при восстановлении папки '{folder}': {e}")
    shutil.rmtree(temp_dir)
    print("Временная директория удалена.")

def download_and_extract_release(zipball_url, extract_to_dir="."):
    print(f"Скачиваю обновление с: {zipball_url}")
    temp_zip_path = os.path.join(tempfile.gettempdir(), "update.zip")
    temp_extract_path = tempfile.mkdtemp()
    try:
        response = requests.get(zipball_url, headers=get_github_headers(), stream=True)
        response.raise_for_status()

        with open(temp_zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("Обновление скачано. Распаковываю...")
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_path)

        extracted_content = os.listdir(temp_extract_path)
        if len(extracted_content) == 1 and os.path.isdir(os.path.join(temp_extract_path, extracted_content[0])):
            root_folder_in_zip = os.path.join(temp_extract_path, extracted_content[0])
            print(f"Найдена корневая папка в архиве: {root_folder_in_zip}")

            for item in os.listdir(root_folder_in_zip):
                s = os.path.join(root_folder_in_zip, item)
                d = os.path.join(extract_to_dir, item)

                if item == os.path.basename(__file__) or item == os.path.basename(temp_extract_path) or item in FOLDERS_TO_PRESERVE:
                    print(f"Пропускаю файл/папку лаунчера/резервной копии: {item}")
                    continue
                
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            print("Файлы обновления успешно перемещены.")
        else:
            print("Ошибка: Неожиданная структура ZIP-архива. Ожидалась одна корневая папка.")
            return False

        time.sleep(0.1)
        os.remove(temp_zip_path)
        print("Обновление успешно распаковано.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании обновления: {e}")
    except zipfile.BadZipFile:
        print("Ошибка: скачанный файл не является корректным ZIP-архивом.")
    except Exception as e:
        print(f"Неизвестная ошибка при распаковке обновления: {e}")
    finally:
        if os.path.exists(temp_extract_path):
            shutil.rmtree(temp_extract_path)
    return False

def launch_game(game_script="main_game.py"):
    action = input("Вы хотите запустить игру? (y/n) -> ")
    if action == "y" or "н":
        print(f"Запуск игры: {game_script}")
    else:
        print("Закрытие...")
        sys.exit()

    try:
        subprocess.run(["python", game_script])
    except FileNotFoundError:
        print(f"Ошибка: Файл '{game_script}' не найден. Убедитесь, что он существует и Python установлен в PATH.")
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")

if __name__ == "__main__":
    current_version_str = get_current_version()
    print(f"Текущая версия игры: {current_version_str}")

    release_info = get_latest_release_info()
    if release_info:
        latest_version_str = release_info.get('tag_name', '').lstrip('v')
        print(f"Последняя версия на GitHub (из релиза): {latest_version_str}")

        if latest_version_str:
            try:
                current_version = Version(current_version_str)
                latest_version = Version(latest_version_str)

                if latest_version > current_version:
                    print("Доступно обновление! Начинаю загрузку...")
                    temp_backup_dir = tempfile.mkdtemp()
                    try:
                        backup_folders(temp_backup_dir, FOLDERS_TO_PRESERVE)
                        zipball_url = release_info.get('zipball_url')
                        if zipball_url:
                            if download_and_extract_release(zipball_url):
                                restore_folders(temp_backup_dir, FOLDERS_TO_PRESERVE)
                                print("Обновление завершено. Перезапустите игру для применения изменений.")
                                launch_game()
                            else:
                                print("Не удалось установить обновление.")
                        else:
                            print("Не удалось найти URL для скачивания обновления.")
                    finally:
                        if os.path.exists(temp_backup_dir):
                            shutil.rmtree(temp_backup_dir)
                else:
                    print("У вас установлена последняя версия. Запуск игру...")
                    launch_game()
            except Exception as e:
                print(f"Ошибка при сравнении версий: {e}")
                print("Запуск игру с текущей версией.")
                launch_game()
        else:
            print("Не удалось определить версию последнего релиза. Запуск игру с текущей версией.")
            launch_game()
    else:
        print("Не удалось получить информацию о релизе с GitHub. Запуск игру с текущей версией.")
        launch_game()