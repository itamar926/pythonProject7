import socket
import threading
from crypto_utils import Crypto

class Node:
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
            print(f"{self.name} forwarded message")
        else:
            payload, target_port = decrypted.rsplit(b"|", 1)
            target_port = int(target_port.decode())

            s = socket.socket()
            s.connect(("127.0.0.1", target_port))
            s.send(payload)
            s.close()

            print(f"{self.name} delivered message to client")
