



import json
import os
import platform
import sys

DEFAULT_VFS = "root_vfs"


def parse_args():
    """Считывает аргументы командной строки --vfs and --script."""
    vfs_path = None
    script_path = None

    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "--vfs" and i + 1 < len(sys.argv):
            vfs_path = sys.argv[i + 1]
        elif sys.argv[i] == "--script" and i + 1 < len(sys.argv):
            script_path = sys.argv[i + 1]

    print("--- [ОТЛАДКА] Параметры запуска ---")
    print(f"Путь к VFS: {vfs_path}")
    print(f"Путь к скрипту: {script_path}")
    print("----------------------------------\n")

    return vfs_path, script_path


def load_vfs(vfs_path: str):
    """Загружает виртуальную файловую систему из JSON-файла."""
    if not vfs_path:
        print("[Предупреждение] Путь к VFS не указан. Создана пустая VFS.")
        return {"type": "dir", "children": {}}

    if not os.path.exists(vfs_path):
        print(f"Ошибка загрузки VFS: Файл '{vfs_path}' не найден.")
        return {"type": "dir", "children": {}}

    try:
        with open(vfs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Ошибка загрузки VFS: Неверный формат JSON в '{vfs_path}'.")
        return {"type": "dir", "children": {}}


def find_node(vfs_data, path_str: str):
    """Ищет узел (папку или файл) внутри структуры VFS по текстовому пути."""
    if path_str == "/" or not path_str:
        return vfs_data

    parts = [p for p in path_str.split("/") if p]
    current = vfs_data

    for part in parts:
        if current.get("type") != "dir" or "children" not in current:
            return None
        if part in current["children"]:
            current = current["children"][part]
        else:
            return None
    return current


def cmd_ls(vfs_data, current_path: str):
    """Реализация команды ls."""
    node = find_node(vfs_data, current_path)
    if node and node.get("type") == "dir" and "children" in node:
        for name in node["children"].keys():
            print(name)
    else:
        print("Ошибка: невозможно прочитать текущую директорию.")


def cmd_cd(vfs_data, current_path: str, arg: str):
    """Реализация команды cd с поддержкой перехода вверх."""
    if not arg or arg == "/":
        return "/"

    if arg == "..":
        if current_path == "/":
            return "/"
        parts = [p for p in current_path.split("/") if p]
        if not parts:
            return "/"
        parts.pop()
        return "/" + "/".join(parts)

    target_path = (
        arg if arg.startswith("/") else f"{current_path}/{arg}".replace("//", "/")
    )
    target_node = find_node(vfs_data, target_path)
    if target_node and target_node.get("type") == "dir":
        return target_path
    else:
        print(f"cd: ноу суч файл ор директори: {arg}")
        return current_path


def cmd_uniq(vfs_data, current_path: str, arg: str):
    """Реализация команды uniq для файлов из VFS (удаление дубликатов)."""
    if not arg:
        print("uniq: пропущен аргумент с именем файла")
        return

    target_path = f"{current_path}/{arg}".replace("//", "/")
    node = find_node(vfs_data, target_path)

    if not node or node.get("type") != "file":
        print(f"uniq: {arg}: Нет такого файла")
        return

    lines = node.get("content", "").splitlines()
    last_line = None
    for line in lines:
        if line != last_line:
            print(line)
            last_line = line


def cmd_mkdir(vfs_data, current_path: str, arg: str):
    """Этап 5: Создает новую директорию в памяти VFS."""
    if not arg:
        print("mkdir: пропущен аргумент")
        return

    parent_node = find_node(vfs_data, current_path)
    if parent_node and parent_node.get("type") == "dir":
        if arg in parent_node["children"]:
            print(f"mkdir: невозможно создать директорию '{arg}': Файл существует")
        else:
            parent_node["children"][arg] = {"type": "dir", "children": {}}
    else:
        print("mkdir: ошибка текущей директории")


def cmd_touch(vfs_data, current_path: str, arg: str):
    """Этап 5: Создает пустой файл в памяти VFS."""
    if not arg:
        print("touch: пропущен аргумент")
        return

    parent_node = find_node(vfs_data, current_path)
    if parent_node and parent_node.get("type") == "dir":
        if arg not in parent_node["children"]:
            parent_node["children"][arg] = {"type": "file", "content": ""}
    else:
        print("touch: ошибка текущей директории")


def handle_command(cmd_line: str, vfs_data, current_path: str):
    """Маршрутизатор всех доступных команд эмулятора."""
    processed = os.path.expandvars(cmd_line.strip())
    if not processed:
        return True, current_path

    parts = processed.split()
    cmd = parts
    args = parts[1:]

    if cmd == "exit":
        print("Завершение работы эмулятора.")
        return False, current_path
    elif cmd == "ls":
        cmd_ls(vfs_data, current_path)
        return True, current_path
    elif cmd == "cd":
        new_path = cmd_cd(vfs_data, current_path, args if args else "/")
        return True, new_path
    elif cmd == "uname":
        print(f"{platform.system()} {platform.node()} emulator-vfs")
        return True, current_path
    elif cmd == "uniq":
        cmd_uniq(vfs_data, current_path, args if args else None)
        return True, current_path
    elif cmd == "mkdir":
        cmd_mkdir(vfs_data, current_path, args if args else None)
        return True, current_path
    elif cmd == "touch":
        cmd_touch(vfs_data, current_path, args if args else None)
        return True, current_path
    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")
        return True, current_path


def run_start_script(script_path: str, vfs_data, current_path: str):
    """Выполняет стартовый скрипт построчно, игнорируя ошибки."""
    if not os.path.exists(script_path):
        print(f"Ошибка: Стартовый скрипт '{script_path}' не найден.")
        return current_path

    print("--- Выполнение стартового скрипта ---")
    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line:
                continue
            print(f"script_cmd> {clean_line}")
            keep_running, current_path = handle_command(
                clean_line, vfs_data, current_path
            )
            if not keep_running:
                sys.exit(0)
    print("--- Стартовый скрипт завершен ---\n")
    return current_path


def main() -> None:
    """Главный цикл работы приложения."""
    vfs_path, script_path = parse_args()
    vfs_data = load_vfs(vfs_path)
    vfs_name = os.path.basename(vfs_path) if vfs_path else DEFAULT_VFS
    current_path = "/"

    if script_path:
        current_path = run_start_script(script_path, vfs_data, current_path)

    print("--- Интерактивный режим (REPL) ---")
    while True:
        try:
            prompt = f"{vfs_name}:{current_path}> "
            user_input = input(prompt)
            keep_running, current_path = handle_command(
                user_input, vfs_data, current_path
            )
            if not keep_running:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы.")
            break


if __name__ == "__main__":
    main()

























