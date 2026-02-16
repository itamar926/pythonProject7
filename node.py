import socket
import threading
from crypto_utils import Crypto
from packet import Packet


class Node:
    clients = {}

    def __init__(self, name, host, port, next_host, next_port, key):
        self.name = name
        self.host = host
        self.port = port
        self.next = (next_host, next_port) if next_host else None
        self.key = key

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"{self.name} listening on {self.host}:{self.port}")

        while True:
            conn, addr = server.accept()
            threading.Thread(
                target=self.handle,
                args=(conn, addr),
                daemon=True
            ).start()

    def handle(self, conn, addr):
        client_ip = addr[0]

        data = conn.recv(4096)
        conn.close()

        if not data:
            return

        print(f"{self.name} received")

        decrypted = Crypto.xor(data, self.key)

        if self.next:
            s = socket.socket()
            s.connect(self.next)
            s.send(decrypted)
            s.close()
        else:
            sender, target, msg = Packet.decode(decrypted)

            print("FINAL NODE:", sender, target, msg)

            if msg.startswith("REGISTER:"):
                port = int(msg.split(":")[1])
                Node.clients[sender] = (client_ip, port)
                print("REGISTERED:", Node.clients)
                return

            if target == "ALL":
                for info in Node.clients.values():
                    self.send_to_client(info, decrypted)
            else:
                if target in Node.clients:
                    self.send_to_client(Node.clients[target], decrypted)

    def send_to_client(self, client_info, data):
        ip, port = client_info
        s = socket.socket()
        s.connect((ip, port))
        s.send(data)
        s.close()
