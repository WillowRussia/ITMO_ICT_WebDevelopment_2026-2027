"""Задание 2. Решение квадратного уравнения по TCP
Вариант 2. Уравнение a*x^2 + b*x + c = 0 решается через дискриминант.
Обмен данными — одной строкой JSON на запрос, где клиент присылает коэффициенты, сервер возвращает корни и дискриминант.
"""

import json
import math
import socket
from dataclasses import dataclass
from typing import Optional

HOST = '127.0.0.1'
PORT = 9096
BACKLOG = 5


@dataclass
class Outcome:
    discriminant: Optional[float]
    roots: list


def solve(a, b, c):
    if a == 0:
        if b == 0:
            return None, 'Уравнение вырождено: переменная x отсутствует'
        return Outcome(discriminant=None, roots=[-c / b]), None

    d = b * b - 4 * a * c
    if d > 0:
        root = math.sqrt(d)
        roots = [(-b - root) / (2 * a), (-b + root) / (2 * a)]
    elif d == 0:
        roots = [-b / (2 * a)]
    else:
        # дискриминант отрицателен: корни комплексные, сопряжённые
        real = -b / (2 * a) + 0.0
        imaginary = math.sqrt(-d) / (2 * a)
        roots = [complex(real, imaginary), complex(real, -imaginary)]

    return Outcome(discriminant=d, roots=roots), None


def handle(connection, address):
    print(f'Подключился {address[0]}:{address[1]}')
    try:
        request = connection.makefile('r', encoding='utf-8').readline()
    except UnicodeDecodeError:
        response = {'error': 'Тело запроса должно быть текстом JSON'}
    else:
        if not request:
            return  # клиент закрыл соединение, ничего не прислав
        response = process(json.loads(request))
    connection.sendall((json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8'))
    connection.close()


def process(payload):
    try:
        a = float(payload['a'])
        b = float(payload['b'])
        c = float(payload['c'])
    except (KeyError, TypeError, ValueError):
        return {'error': 'Ожидались числа: a, b, c'}

    outcome, error = solve(a, b, c)
    if error:
        return {'error': error}
    return {
        'discriminant': outcome.discriminant,
        # комплексные корни в JSON не сериализуются напрямую
        'roots': [str(root) for root in outcome.roots],
    }


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(BACKLOG)
    print(f'Сервер вычислений запущен: {HOST}:{PORT}')

    while True:
        connection, address = server.accept()
        handle(connection, address)


if __name__ == '__main__':
    main()
