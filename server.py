import socket
import logging
import hashlib
from threading import Thread
import json

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s')

Users = {}
ip_list = []
password_hashing = 'hashing'.encode('utf-8')

сhatHistory = open("logs/chat_history.log", "w")
сhatHistory.write('\n***История чата***\n')
сhatHistory.close()

class Thread_client(Thread):
    def __init__(self, connection, address):
        super().__init__(daemon=True)
        self.connected = True
        self.conn = connection
        self.addr = address
        self.username = None
        self.enter()

    def enter(self): 
        self.send_message('Введите имя пользователя')
        name = self.receive_message()
        self.username = name
        if name in Users.keys():
            self.send_message('Введите пароль')
            if Users[name]['password'] == get_password_hash(self.receive_message()):
                self.successful_enterance()
            else:
                self.chat_leaving('Неправильный пароль')
        else:
            self.send_message('Установите новый пароль')
            Users.update({name: {'password': get_password_hash(self.receive_message())}})
            save_users()

    def successful_enterance(self):
        self.send_message(f'Вход выполнен успешно')
        save_users()

    def chat_leaving(self, reason=''):
        logging.info(f'Соединение закрыто {self.addr} {" - " + reason if reason else ""}')
        self.connected = False
        message_to_all_users(f"{self.username} покинул сервер", ip_list)
        if self in ip_list:
            ip_list.remove(self)

    def send_message(self, message):
        if self.connected:
            send_text(self.conn, message)

    def receive_message(self):
        if not self.connected:
            return
        try:
            return receive_text(self.conn)
        except ConnectionResetError:
            self.chat_leaving('Ошибка соединения')

    def run(self):
        ip_list.append(self)
        self.send_message(f'Добро пожаловать, {self.username}')
        message_service(self, 'присоединился к серверу')
        while True and self.connected:
            message = self.receive_message()
            if message == 'exit':
                self.chat_leaving('Пользователь отключился от сервера')
                break
            message_to_all_users(f'{self.username}: {message}')

def save_users():
    with open('users.json', 'w') as f:
        json.dump(Users, f, indent=4)

def message_to_all_users(message):
    for i in ip_list:
        i.send_message(message)
    
    with open("logs/chat_history.log", "a") as chatHistory:
        chatHistory.write(message + '\n')

def message_service(user, message):
    for i in ip_list:
        if i != user:
            i.send_message(f'{user.username} {message}')

def get_password_hash(password):
    return hashlib.sha512(password.encode('utf-8') + password_hashing).hexdigest()

def receive_text(conn):
    return conn.recv(1024).decode('utf-8')

def send_text(conn, message):
    message = message.encode('utf-8')
    conn.send(message)

def start_server(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                sock.bind((host, port))
                break
            except OSError:
                logging.info(f'Порт {port} уже занят, пробуем следующий порт...')
                port += 1
        sock.listen(10)
        print('Сервер запущен')
        logging.info(f'Сервер запущен на {host}:{port}')
        try:
            with open('users.json', 'r') as file:
                Users = json.load(file)
        except json.decoder.JSONDecodeError:
            Users = {}
        while True:
            conn, addr = sock.accept()
            print(f'Открыто соединение {addr} ')
            logging.info(f'Открыто соединение {addr} ')
            thread = Thread_client(conn, addr)
            thread.start()

if __name__ == '__main__':
    IP = input("Введите IP-адрес сервера (по умолчанию 127.0.0.1): ")
    if IP == '':
        IP = "127.0.0.1"

    port = input('Введите порт для внешнего подключения (по умолчанию 12345): ')
    if port == '':
        port = 12345
    else:
        port = int(port) 
    
    start_server(IP, port)