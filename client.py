import socket
import threading
from crypto_utils import Crypto
from packet import Packet


class Client:

    def __init__(self, name, server_host, server_port, listen_port):
        self.name = name
        self.server_host = server_host
        self.server_port = server_port
        self.listen_port = listen_port

        # סדר שכבות Onion
        self.keys = [33, 22, 11]

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        self.register()

    def register(self):
        packet = Packet(self.name, "ALL", f"REGISTER:{self.listen_port}")
        data = packet.encode()

        for k in self.keys:
            data = Crypto.xor(data, k)

        self.send_raw(data)

    def send_message(self, target, message):
        packet = Packet(self.name, target, message)
        data = packet.encode()

        for k in self.keys:
            data = Crypto.xor(data, k)

        self.send_raw(data)

    def send_raw(self, data):
        s = socket.socket()
        s.connect((self.server_host, self.server_port))
        s.send(data)
        s.close()

    # 🔥 אין פה שום XOR יותר!
    def listen(self):
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()

        while True:
            conn, _ = server.accept()
            data = conn.recv(4096)
            conn.close()

            try:
                sender, target, msg = Packet.decode(data)
            except:
                print("Decode error:", data)
                continue

            if hasattr(self, "on_message"):
                self.on_message(sender, msg)
            else:
                print(sender, ">", msg)
