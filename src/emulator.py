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
    print("--- [ОТЛАДКА] Параметры запуска ---")
    print(f"Путь к VFS: {vfs_path}\nПуть к скрипту: {script_path}")
    print("----------------------------------\n")
    return vfs_path, script_path


def handle_command(cmd_line: str) -> bool:
    """Разбирает строку ввода и имитирует выполнение команды."""
    processed = os.path.expandvars(cmd_line.strip())
    if not processed:
        return True
    parts = processed.split()
    cmd, args = parts[0], parts[1:]
    if cmd == "exit":
        print("Завершение работы эмулятора.")
        return False
    elif cmd in ("ls", "cd"):
        print(f"[Заглушка] Команда: {cmd}, аргументы: {args}")
        return True
    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")
        return True


def run_start_script(script_path: str) -> None:
    """Последовательно выполняет команды из стартового скрипта."""
    if not os.path.exists(script_path):
        print(f"Ошибка: Стартовый скрипт '{script_path}' не найден.")
        return
    print("--- Выполнение стартового скрипта ---")
    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line:
                continue
            print(f"script_cmd> {clean_line}")
            if not handle_command(clean_line):
                break
    print("--- Стартовый скрипт завершен ---\n")


def main() -> None:
    """Главная точка входа в эмулятор."""
    vfs_path, script_path = parse_args()
    vfs_name = os.path.basename(vfs_path) if vfs_path else DEFAULT_VFS
    if script_path:
        run_start_script(script_path)
    print("--- Интерактивный режим (REPL) ---")
    while True:
        try:
            user_input = input(f"{vfs_name}> ")
            if not handle_command(user_input):
                break
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()















        
