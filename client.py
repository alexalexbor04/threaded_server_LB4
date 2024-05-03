import socket
from threading import Thread

connection_alive = True

def check_message(message=''):
    a = input(message)
    if a in ['exit', '/stop']:
        exit()
    return a

def receive_messages():
    global connection_alive
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            print(data)
        except (ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError) as error:
            connection_alive = False
            print(error)
            break


def send_text(conn, message):
    message = message.encode('utf-8')
    conn.send(message)

try:
    print("Для использования настроек по умолчанию ничего не вводите")
    IP = input('Введите ip адрес для подключения (если ничего ен вводить, значение по умолчанию - 127.0.0.1): ')
    if IP == '':
        IP = '127.0.0.1'
    port = input('Введите порт для подключения (если ничего не вводить, значение по умолчанию - 12345): ')
    if port == '':
        port = 12345
    else:
        port = int(port)
except ValueError:
    print("Неверно указан порт! Попробуйте еще раз!")
try:
    client_socket = socket.socket()
    client_socket.connect((IP, port))
    print(f'Соединение с {IP}:{port} успешно установлено')
except (socket.gaierror, ConnectionRefusedError) as error:
    print(f"Не удается подключиться к {IP}:{port} ({error})!")

Thread(target=receive_messages, daemon=True).start()

while True:
    while True:
        message_from_server = check_message()
        if connection_alive:
            client_socket.sendall(message_from_server.encode())
        else:
            client_socket.close()
            break