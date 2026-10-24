#Server

import socket
import threading

import socket
import threading

# Налаштування мережі: слухаємо на всіх інтерфейсах порт 8080
HOST = '0.0.0.0'
PORT = 8080

# Список для зберігання активних підключень клієнтів
clients = []


def broadcast(data, exclude_socket=None):
    """Розсилає отримані дані всім підключеним клієнтам,

    окрім відправника (exclude_socket).
    """
    for client in clients:
        if client != exclude_socket:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"[ПОМИЛКА] Не вдалося надіслати повідомлення клієнту: {e}")


def handle_client(client_socket):
    """Обробляє повідомлення від окремого підключеного клієнта в реальному часі."""
    while True:
        try:
            # Отримуємо дані від клієнта (буфер на 4096 байт)
            data = client_socket.recv(4096)
            if not data:
                # Якщо дані порожні, значить клієнт розірвав з'єднання
                break
            # Транслюємо повідомлення решті учасників чату
            broadcast(data, exclude_socket=client_socket)
        except Exception:
            # У разі будь-якої помилки мережі припиняємо обробку
            break

    # Видаляємо клієнта зі списку активних, якщо він там є
    if client_socket in clients:
        clients.remove(client_socket)

    # Закриваємо сокет клієнта
    client_socket.close()
    print("[ІНФО] Клієнт відключився від чату.")


def main():
    """Головна функція запуску сервера."""
    # Створюємо TCP-сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Дозволяємо повторне використання порту (щоб уникнути помилки "Address already in use")
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Прив'язуємо сокет до хосту та порту
    server_socket.bind((HOST, PORT))

    # Переводимо сервер у режим прослуховування (черга до 5 підключень)
    server_socket.listen(5)
    print(f"[УСПІХ] Сервер успішно запущено та слухає на {HOST}:{PORT}")

    # Головний цикл прийняття нових клієнтів
    while True:
        # Чекаємо на нове підключення
        client_socket, addr = server_socket.accept()
        print(f"[ПОДІЯ] Підключився новий клієнт з адресою: {addr}")

        # Додаємо сокет клієнта до загального списку
        clients.append(client_socket)

        # Створюємо та запускаємо окремий потік для обслуговування цього клієнта
        t = threading.Thread(target=handle_client, args=(client_socket,))
        t.start()


if __name__ == "__main__":
    main()