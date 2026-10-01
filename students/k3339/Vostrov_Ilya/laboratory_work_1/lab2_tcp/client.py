"""Задание 2. Решение квадратного уравнения по TCP

Пользователь вводит коэффициенты a, b, c, клиент упаковывает их в JSON и отправляет серверу. Ответ с корнями выводится на экран.
"""

import json
import socket

SERVER = ('127.0.0.1', 9096)
PROMPT = 'Уравнение a*x^2 + b*x + c = 0'


def read_number(label):
    while True:
        raw = input(f'{label} = ').strip().replace(',', '.')
        try:
            return float(raw)
        except ValueError:
            print('Нужно ввести число, попробуйте ещё раз.')


def main():
    print(PROMPT)
    a = read_number('a')
    b = read_number('b')
    c = read_number('c')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(SERVER)
        request = json.dumps({'a': a, 'b': b, 'c': c}) + '\n'
        client.sendall(request.encode('utf-8'))

        reply = client.makefile('r', encoding='utf-8').readline()

    if not reply:
        print('Сервер не ответил.')
        return

    answer = json.loads(reply)
    if 'error' in answer:
        print('Ошибка:', answer['error'])
        return

    if answer['discriminant'] is None:
        print('Уравнение линейное, единственный корень:', answer['roots'][0])
    else:
        print('Дискриминант:', answer['discriminant'])
        print('Корни:', ', '.join(answer['roots']))


if __name__ == '__main__':
    main()
