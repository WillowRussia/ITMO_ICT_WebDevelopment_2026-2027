"""Задание 1. Обмен сообщениями по UDP.
Сервер лишь привязывается к адресу и отвечает отправителю, указывая полученный адрес клиента.
"""

import socket

HOST = '0.0.0.0'
PORT = 9095
BUFFER_SIZE = 1024
REPLY = 'Hello, client'


def serve():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        print(f'UDP-сервер запущен на порту {PORT}')

        while True:
            data, client = server.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            print(f'Получено от {client[0]}:{client[1]}: {message}')

            server.sendto(REPLY.encode('utf-8'), client)
            print(f'Отправлено в ответ: {REPLY}')


if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        print('\nСервер остановлен.')
