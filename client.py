import socket

IP = input('Введите ip адрес для подключения (если ничего ен вводить, значение по умолчанию - 127.0.0.1): ')
if IP == None:
    IP = '127.0.0.1'

port = input('Введите порт для подключения (если ничего не вводить, значение по умолчанию - 12345): ')
if port == '':
    port = 12345
else:
    port = int(port)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, port))
print(f'Соединение с {IP}:{port} успешно установлено')

try:
    while True:
        message_from_server = client_socket.recv(1024).decode()
        print(f'Получено: {message_from_server}')

        message_from_client = input('Введите текст для отправки: ')

        client_socket.sendall(message_from_client.encode())
        print(f'Отправлено: {message_from_client}')

        if message_from_client == 'exit':
            break
except:
    print('Возникла непредвиденная ошибка, попробуйте снова.')
    client_socket.close()
client_socket.close()