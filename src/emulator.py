import json
import os
import sys

DEFAULT_VFS = "root_vfs"


def parse_args():
    """Считывает аргументы командной строки --vfs и --script."""
    vfs_path, script_path = None, None
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "--vfs" and i + 1 < len(sys.argv):
            vfs_path = sys.argv[i + 1]
        elif sys.argv[i] == "--script" and i + 1 < len(sys.argv):
            script_path = sys.argv[i + 1]
    return vfs_path, script_path


def load_vfs(vfs_path: str):
    """Загружает виртуальную файловую систему из JSON-файла."""
    if not vfs_path or not os.path.exists(vfs_path):
        print("Ошибка загрузки VFS. Создана пустая VFS.")
        return {"type": "dir", "children": {}}
    try:
        with open(vfs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"type": "dir", "children": {}}


def main() -> None:
    """Главная точка входа в эмулятор."""
    vfs_path, script_path = parse_args()
    vfs_data = load_vfs(vfs_path)
    vfs_name = os.path.basename(vfs_path) if vfs_path else DEFAULT_VFS
    print(f"--- Эмулятор с поддержкой VFS ({vfs_name}) ---")
    print("Загруженная структура:", vfs_data)


if __name__ == "__main__":
    main()













        
