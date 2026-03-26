import socket
import threading
from crypto_utils import Crypto
from packet import Packet


class Client:
    def __init__(self, name, server_host, server_port, listen_port, client_ip="127.0.0.1", keys=None):
        self.name = name
        self.server_host = server_host
        self.server_port = server_port
        self.listen_port = listen_port
        self.client_ip = client_ip

        # סדר שכבות Onion: הפוך מסדר השרתים
        self.keys = keys if keys else [33, 22, 11]

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        self.register()

    def register(self):
        packet = Packet(self.name, "ALL", f"REGISTER:{self.listen_port}:{self.client_ip}")
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
        try:
            s.connect((self.server_host, self.server_port))
            s.send(data)
            s.close()
        except Exception as e:
            print(f"Failed to connect to entry node: {e}")

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
                continue

            if hasattr(self, "on_message"):
                self.on_message(sender, msg)
            else:
                # מדפיס את ההודעה ואז מחזיר את סמן ההקלדה
                print(f"\n[{sender}] > {msg}\n{self.name}> ", end="")