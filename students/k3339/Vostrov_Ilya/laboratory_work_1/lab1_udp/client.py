"""Задание 1. Обмен сообщениями по UDP.
Клиент отправляет приветствие, затем ждёт ответ
"""

import socket

SERVER = ('127.0.0.1', 9095)
MESSAGE = 'Hello, server'
BUFFER_SIZE = 1024


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)
        client.sendto(MESSAGE.encode('utf-8'), SERVER)
        print(f'Отправлено серверу: {MESSAGE}')

        try:
            data, _ = client.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print('Ответа не дождались: сервер, похоже, не запущен(((')
        else:
            print(f'Ответ сервера: {data.decode("utf-8")}')


if __name__ == '__main__':
    main()
