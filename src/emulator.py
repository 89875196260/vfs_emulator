import os
import sys

DEFAULT_VFS_NAME = "root_vfs"


def expand_env(text: str) -> str:
    """Раскрывает переменные окружения реальной ОС (например, $HOME)."""
    return os.path.expandvars(text)


def handle_command(cmd_line: str) -> bool:
    """Разбирает и выполняет команду пользователя."""
    processed_line = expand_env(cmd_line.strip())
    if not processed_line:
        return True

    parts = processed_line.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "exit":
        print("Завершение работы эмулятора.")
        return False
    elif cmd in ("ls", "cd"):
        print(f"[Заглушка] Вызвана команда: {cmd}, аргументы: {args}")
        return True
    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")
        return True


def main() -> None:
    """Главный цикл REPL эмулятора."""
    vfs_name = DEFAULT_VFS_NAME
    print("--- Эмулятор командной строки (Вариант 10) ---")
    while True:
        try:
            prompt = f"{vfs_name}> "
            user_input = input(prompt)
            if not handle_command(user_input):
                break
        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы.")
            break


if __name__ == "__main__":
    main()

















        
