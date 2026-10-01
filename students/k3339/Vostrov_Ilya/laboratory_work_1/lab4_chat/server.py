"""Задание 4. Многопользовательский чат
Каждое подключение обслуживается отдельным потоком, поэтому сервер
может одновременно работать с несколькими клиентами
"""

import socket
import threading

HOST = '127.0.0.1'
PORT = 9097


class ChatRoom:

    def __init__(self):
        self.members = {}          # {сокет: имя}
        self.guard = threading.Lock()

    def join(self, connection, nickname, address):
        with self.guard:
            self.members[connection] = nickname
        print(f'{nickname} вошёл в чат с {address[0]}:{address[1]}')
        self.notify(f'* {nickname} присоединился', exclude=connection)

    def leave(self, connection, nickname):
        with self.guard:
            was_present = self.members.pop(connection, None) is not None
        connection.close()
        if was_present:
            print(f'{nickname} покинул чат')
            self.notify(f'* {nickname} покинул чат', exclude=connection)

    def notify(self, text, exclude=None):
        with self.guard:
            targets = [conn for conn in self.members if conn != exclude]
        for target in targets:
            try:
                target.sendall((text + '\n').encode('utf-8'))
            except OSError:
                pass  # отвалившийся клиент уберёт сам себя в своём потоке


room = ChatRoom()


def chat_session(connection, address):
    reader = connection.makefile('r', encoding='utf-8')
    nickname = reader.readline().strip()
    if not nickname:
        connection.close()
        return

    room.join(connection, nickname, address)
    try:
        for line in reader:
            text = line.strip()
            if text == '/quit':
                break
            if text:
                print(f'{nickname}: {text}')
                room.notify(f'{nickname}: {text}', exclude=connection)
    finally:
        room.leave(connection, nickname)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f'Чат-сервер запущен: {HOST}:{PORT}')

    while True:
        connection, address = server.accept()
        threading.Thread(
            target=chat_session, args=(connection, address), daemon=True
        ).start()


if __name__ == '__main__':
    main()
