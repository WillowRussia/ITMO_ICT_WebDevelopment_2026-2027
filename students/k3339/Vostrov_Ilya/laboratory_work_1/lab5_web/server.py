"""Задание 5. Простой веб-сервер для GET и POST

GET  /  — страница с формой и журналом всех оценок по дисциплинам.
POST /  — принять дисциплину и оценку из формы и сохранить в журнал.
Прочие пути и методы — 404 и 405.
"""

import socket
from concurrent.futures import ThreadPoolExecutor
from html import escape
from http import HTTPStatus

HOST = '127.0.0.1'
PORT = 9086


def unquote(text):
    decoded = bytearray()
    i = 0
    while i < len(text):
        if text[i] == '+':
            decoded.append(0x20)
            i += 1
        elif (
            text[i] == '%'
            and i + 2 < len(text)
            and all(c in '0123456789abcdefABCDEF' for c in text[i + 1:i + 3])
        ):
            decoded.append(int(text[i + 1:i + 3], 16))
            i += 3
        else:
            decoded.extend(text[i].encode('utf-8'))
            i += 1
    return decoded.decode('utf-8')


def parse_form(raw):
    fields = {}
    for pair in raw.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            fields[key] = unquote(value)
    return fields


class GradebookServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.grades = {}   # дисциплина -> список оценок

    def _read_request(self, connection):
        raw = b''
        while b'\r\n\r\n' not in raw:
            chunk = connection.recv(1024)
            if not chunk:
                raise ConnectionError('запрос оборван')
            raw += chunk

        head, _, body = raw.partition(b'\r\n\r\n')
        parts = head.decode('utf-8').split()
        method = parts[0] if parts else 'GET'
        path = parts[1] if len(parts) > 1 else '/'

        headers = {}
        for line in head.decode('utf-8').split('\r\n')[1:]:
            if ':' in line:
                name, value = line.split(':', 1)
                headers[name.strip().lower()] = value.strip()

        length = int(headers.get('content-length', 0))
        while len(body) < length:
            chunk = connection.recv(1024)
            if not chunk:
                break
            body += chunk
        return method, path, body[:length].decode('utf-8')

    @staticmethod
    def _response(status, body):
        payload = body.encode('utf-8')
        head = (
            f'HTTP/1.1 {status.value} {status.phrase}\r\n'
            'Content-Type: text/html; charset=utf-8\r\n'
            f'Content-Length: {len(payload)}\r\n'
            'Connection: close\r\n'
            '\r\n'
        )
        return head.encode('utf-8') + payload

    def handle_get(self):
        return self._response(HTTPStatus.OK, self.render_page())

    def handle_post(self, body):
        fields = parse_form(body)
        subject = fields.get('discipline', '').strip()
        grade = fields.get('grade', '').strip()

        if not subject or not grade:
            return self._response(
                HTTPStatus.OK,
                self.render_page(notice='Заполнены не все поля!'),
            )

        self.grades.setdefault(subject, []).append(grade)
        print(f'Внесено в журнал: {subject} — {grade}')
        return self._response(HTTPStatus.OK, self.render_page())

    def handle_connection(self, connection, address):
        try:
            method, path, body = self._read_request(connection)
            print(f'{address[0]}: {method} {path}')

            if path == '/' and method == 'GET':
                response = self.handle_get()
            elif path == '/' and method == 'POST':
                response = self.handle_post(body)
            elif path != '/':
                response = self._response(
                    HTTPStatus.NOT_FOUND,
                    '<h1>404 — такой страницы нет</h1><p><a href="/">На главную</a></p>',
                )
            else:
                response = self._response(
                    HTTPStatus.METHOD_NOT_ALLOWED,
                    '<h1>405 — метод не поддерживается</h1>',
                )

            connection.sendall(response)
        except ConnectionError as error:
            print(f'{address[0]}: {error}')
        finally:
            connection.close()


    def render_page(self, notice=''):
        rows = ''
        for subject, marks in self.grades.items():
            items = ''.join(f'<li>{escape(mark)}</li>' for mark in marks)
            rows += (
                f'<tr><td>{escape(subject)}</td>'
                f'<td><ol>{items}</ol></td>'
                f'<td>{len(marks)}</td></tr>'
            )

        if rows:
            table = (
                '<table>'
                '<tr><th>Дисциплина</th><th>Оценки</th><th>Количество</th></tr>'
                f'{rows}</table>'
            )
        else:
            table = '<p class="hint">Журнал пока пуст — добавьте первую оценку.</p>'

        alert = f'<p class="alert">{escape(notice)}</p>' if notice else ''
        return f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Журнал успеваемости</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 680px; margin: 40px auto; color: #2b2b2b; }}
    h1 {{ color: #0b5cad; }}
    form {{ background: #f2f6fb; padding: 16px; border-radius: 8px; }}
    input {{ padding: 6px 8px; margin-right: 8px; }}
    button {{ padding: 6px 14px; cursor: pointer; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 14px; }}
    th, td {{ border: 1px solid #b9c6d4; padding: 8px; text-align: left; }}
    th {{ background: #e7eef7; }}
    ol {{ margin: 0; padding-left: 18px; }}
    .alert {{ color: #c0392b; font-weight: bold; }}
    .hint {{ color: #7f8c8d; }}
  </style>
</head>
<body>
  <h1>Журнал успеваемости</h1>
  {alert}
  <form method="post" action="/">
    <p>Дисциплина: <input name="discipline" placeholder="например, Математика" required></p>
    <p>Оценка: <input name="grade" placeholder="например, 5" required></p>
    <p><button type="submit">Внести оценку</button></p>
  </form>
  <h2>Все оценки по дисциплинам</h2>
  {table}
</body>
</html>'''

    def serve_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f'Веб-сервер журнала запущен: http://{self.host}:{self.port}/')

        with ThreadPoolExecutor(max_workers=8) as pool:
            while True:
                connection, address = server.accept()
                pool.submit(self.handle_connection, connection, address)


if __name__ == '__main__':
    GradebookServer(HOST, PORT).serve_forever()
