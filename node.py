import socket
import threading
from crypto_utils import Crypto
from packet import Packet

class Node:
    clients = {}  # username -> port

    def __init__(self, name, host, port, next_host, next_port, key, visualizer=None):
        self.name = name
        self.host = host
        self.port = port
        self.next = (next_host, next_port) if next_host else None
        self.key = key
        self.vis = visualizer

    def start(self):
        server = socket.socket()
        server.bind((self.host, self.port))
        server.listen()
        print(f"{self.name} listening on {self.host}:{self.port}")

        while True:
            conn, _ = server.accept()
            threading.Thread(target=self.handle, args=(conn,), daemon=True).start()

    def handle(self, conn):
        data = conn.recv(4096)
        conn.close()

        if self.vis:
            self.vis.flash(self.name)

        decrypted = Crypto.xor(data, self.key)

        if self.next:
            encrypted = Crypto.xor(decrypted, self.key)
            s = socket.socket()
            s.connect(self.next)
            s.send(encrypted)
            s.close()
        else:
            sender, target, msg = Packet.decode(decrypted)

            # רישום משתמש
            if msg.startswith("REGISTER:"):
                port = int(msg.split(":")[1])
                Node.clients[sender] = port
                print("Registered:", Node.clients)
                return

            # שליחה לכולם
            if target == "ALL":
                for user, port in Node.clients.items():
                    self.send_to_client(port, decrypted)
            else:
                # שליחה פרטית
                if target in Node.clients:
                    self.send_to_client(Node.clients[target], decrypted)

    def send_to_client(self, port, data):
        try:
            s = socket.socket()
            s.connect(("127.0.0.1", port))
            s.send(data)
            s.close()
        except:
            pass
