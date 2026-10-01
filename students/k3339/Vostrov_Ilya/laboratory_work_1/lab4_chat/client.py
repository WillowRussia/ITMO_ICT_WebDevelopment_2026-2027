"""Задание 4. Многопользовательский чат
Один и тот же скрипт запускают все пользователи в своих терминалах
"""

import socket
import threading

SERVER = ('127.0.0.1', 9097)
LEAVE_COMMAND = '/quit'


def listener(reader):
    for line in reader:
        print(f'\r  {line.strip()}\n> ', end='', flush=True)
    print('\nСвязь с сервером прервана.')


def main():
    nickname = input('Введите имя: ').strip()
    if not nickname:
        print('Имя не может быть пустым.')
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(SERVER)
        # построчно буферизованный поток для записи,
        # чтобы каждое сообщение уходило отдельной строкой
        writer = client.makefile('w', encoding='utf-8', buffering=1)
        writer.write(nickname + '\n')

        threading.Thread(
            target=listener,
            args=(client.makefile('r', encoding='utf-8'),),
            daemon=True,
        ).start()

        print(f'Вы в чате {SERVER[0]}:{SERVER[1]}. Команда {LEAVE_COMMAND} — выход.')
        while True:
            text = input('> ')
            writer.write(text + '\n')
            if text.strip() == LEAVE_COMMAND:
                break

    print('Вы вышли из чата.')


if __name__ == '__main__':
    main()
