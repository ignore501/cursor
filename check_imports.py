import ast
import importlib
import pkg_resources
from pathlib import Path
from typing import Dict, List, Set

def get_installed_packages() -> Set[str]:
    """Получить список установленных пакетов."""
    return {pkg.key for pkg in pkg_resources.working_set}

def get_requirements_packages() -> Set[str]:
    """Получить список пакетов из requirements.txt."""
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    packages = set()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            package = line.split('==')[0].lower()
            packages.add(package)
    
    return packages

def find_imports(file_path: Path) -> Set[str]:
    """Найти все импорты в файле."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")
        return set()

def main():
    # Получаем списки пакетов
    installed = get_installed_packages()
    required = get_requirements_packages()
    
    # Находим все Python файлы, исключая виртуальное окружение
    python_files = []
    for path in Path('.').rglob('*.py'):
        if 'venv' not in str(path) and 'site-packages' not in str(path):
            python_files.append(path)
    
    # Собираем все импорты
    all_imports = set()
    for file in python_files:
        imports = find_imports(file)
        all_imports.update(imports)
    
    # Удаляем стандартные библиотеки Python
    stdlib_modules = set(importlib.stdlib_module_names())
    all_imports = all_imports - stdlib_modules
    
    # Проверяем импорты
    missing_in_requirements = all_imports - required
    unused_in_requirements = required - all_imports
    
    print("\nИмпорты, которых нет в requirements.txt:")
    for imp in sorted(missing_in_requirements):
        print(f"- {imp}")
    
    print("\nПакеты в requirements.txt, которые не используются:")
    for pkg in sorted(unused_in_requirements):
        print(f"- {pkg}")
    
    print("\nВсего импортов:", len(all_imports))
    print("Всего пакетов в requirements:", len(required))

if __name__ == '__main__':
    main() 