import subprocess
import sys
from pathlib import Path

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    # Читаем список пакетов для удаления
    with open('packages_to_remove.txt', 'r') as f:
        packages = [line.strip() for line in f.readlines() if line.strip()]

    # Создаем резервную копию текущих зависимостей
    success, output = run_command('pip freeze > requirements_backup.txt')
    if not success:
        print("Ошибка при создании резервной копии:", output)
        return

    print("Начинаем удаление пакетов...")
    
    # Удаляем пакеты по одному
    for package in packages:
        print(f"Удаление {package}...")
        success, output = run_command(f'pip uninstall -y {package}')
        if not success:
            print(f"Ошибка при удалении {package}:", output)
            continue
        print(f"Успешно удален {package}")

    print("\nПроверка оставшихся пакетов...")
    success, output = run_command('pip freeze')
    if success:
        print("\nОставшиеся пакеты:")
        print(output)

    print("\nОчистка завершена!")
    print("Резервная копия зависимостей сохранена в requirements_backup.txt")

if __name__ == '__main__':
    main() 