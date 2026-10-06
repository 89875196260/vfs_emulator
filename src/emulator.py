import json
import os
import platform
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
        return {"type": "dir", "children": {}}
    try:
        with open(vfs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"type": "dir", "children": {}}


def find_node(vfs_data, path_str: str):
    """Ищет узел внутри структуры VFS по текстовому пути."""
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


def cmd_cd(vfs_data, current_path: str, arg: str):
    """Реализация команды cd с поддержкой перехода вверх."""
    if not arg or arg == "/":
        return "/"
    if arg == "..":
        if current_path == "/":
            return "/"
        parts = [p for p in current_path.split("/") if p]
        parts.pop()
        return "/" + "/".join(parts)
    target = (
        arg if arg.startswith("/") else f"{current_path}/{arg}".replace("//", "/")
    )
    node = find_node(vfs_data, target)
    return target if node and node.get("type") == "dir" else current_path


def cmd_uniq(vfs_data, current_path: str, arg: str):
    """Реализация команды uniq для удаления дубликатов строк в файле."""
    if not arg:
        return
    node = find_node(vfs_data, f"{current_path}/{arg}".replace("//", "/"))
    if not node or node.get("type") != "file":
        return
    lines = node.get("content", "").splitlines()
    last = None
    for line in lines:
        if line != last:
            print(line)
            last = line


def handle_command(cmd_line: str, vfs_data, current_path: str):
    """Маршрутизатор доступных команд для Этапа 4."""
    processed = os.path.expandvars(cmd_line.strip())
    if not processed:
        return True, current_path
    parts = processed.split()
    cmd, args = parts[0], parts[1:]
    if cmd == "exit":
        return False, current_path
    elif cmd == "ls":
        cmd_ls(vfs_data, current_path)
        return True, current_path
    elif cmd == "cd":
        new_p = cmd_cd(vfs_data, current_path, args[0] if args else "/")
        return True, new_p
    elif cmd == "uname":
        print(f"{platform.system()} {platform.node()} emulator-vfs")
        return True, current_path
    elif cmd == "uniq":
        cmd_uniq(vfs_data, current_path, args[0] if args else None)
        return True, current_path
    return True, current_path


def main() -> None:
    """Главная точка входа в эмулятор для Этапа 4."""
    vfs_path, _ = parse_args()
    vfs_data = load_vfs(vfs_path)
    vfs_name = os.path.basename(vfs_path) if vfs_path else DEFAULT_VFS
    current_path = "/"
    while True:
        try:
            inp = input(f"{vfs_name}:{current_path}> ")
            run, current_path = handle_command(inp, vfs_data, current_path)
            if not run:
                break
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()













        
