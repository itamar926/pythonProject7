import socket
import threading
from crypto_utils import Crypto

class Node:
    CLIENT_PORTS = [9100, 9101, 9102]  # כל הפורטים של הקליינטים

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
            # Forward to next node
            encrypted = Crypto.xor(decrypted, self.key)
            try:
                s = socket.socket()
                s.connect(self.next)
                s.send(encrypted)
                s.close()
                print(f"{self.name} forwarded message")
            except:
                print(f"{self.name} failed to forward")
        else:
            # Node אחרון - שולח לכל הקליינטים
            for client_port in self.CLIENT_PORTS:
                try:
                    s = socket.socket()
                    s.connect(("127.0.0.1", client_port))
                    s.send(decrypted)
                    s.close()
                except:
                    continue
            print(f"{self.name} delivered message to all clients")
