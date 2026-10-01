"""Задание 3. HTTP-сервер, раздающий страницу из файла index.html

HTTP-ответ собирается вручную: строка статуса, заголовки Content-Type и Content-Length, пустая строка, тело. Длина тела считается в байтах — именно её указывает заголовок Content-Length.
"""

import socket
from http import HTTPStatus

HOST = '127.0.0.1'
PORT = 9085
PAGE_FILE = 'index.html'


class StaticServer:
    def __init__(self, host, port, page_path):
        self.host = host
        self.port = port
        with open(page_path, 'rb') as source:
            self.page = source.read()

    @staticmethod
    def _request_line(connection):
        raw = b''
        while not raw.endswith(b'\r\n'):
            chunk = connection.recv(64)
            if not chunk:
                raise ConnectionError('соединение закрыто')
            raw += chunk
        return raw.decode('utf-8').strip()

    @staticmethod
    def _response(status, body):
        head = (
            f'HTTP/1.1 {status.value} {status.phrase}\r\n'
            'Content-Type: text/html; charset=utf-8\r\n'
            f'Content-Length: {len(body)}\r\n'
            'Connection: close\r\n'
            '\r\n'
        )
        return head.encode('utf-8') + body

    def _handle(self, connection, address):
        try:
            line = self._request_line(connection)
            print(f'{address[0]}: {line}')

            parts = line.split()
            path = parts[1] if len(parts) > 1 else '/'

            if path in ('/', '/index.html'):
                reply = self._response(HTTPStatus.OK, self.page)
            else:
                body = ('<h1>404 — страница не найдена</h1>'
                        '<p><a href="/">Вернуться на главную</a></p>').encode('utf-8')
                reply = self._response(HTTPStatus.NOT_FOUND, body)

            connection.sendall(reply)
        except ConnectionError as error:
            print(f'{address[0]}: {error}')
        finally:
            connection.close()

    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(5)
            print(f'HTTP-сервер запущен: http://{self.host}:{self.port}/')

            while True:
                connection, address = server.accept()
                self._handle(connection, address)


if __name__ == '__main__':
    StaticServer(HOST, PORT, PAGE_FILE).serve_forever()
