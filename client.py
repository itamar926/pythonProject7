import socket
import threading
from crypto_utils import Crypto
from packet import Packet

class Client:
    def __init__(self, name, entry_ip, entry_port, listen_port, keys):
        self.name = name
        self.entry = (entry_ip, entry_port)
        self.listen_port = listen_port
        self.keys = keys

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()

        while True:
            conn, _ = server.accept()
            data = conn.recv(4096)
            conn.close()

            for k in self.keys:
                data = Crypto.xor(data, k)

            sender, msg = Packet.decode(data)
            print(f"\n{sender}> {msg}")

    def send(self, message, target_port):
        packet = Packet(self.name, message)
        data = packet.encode()

        for k in reversed(self.keys):
            data = Crypto.xor(data, k)

        data += f"|{target_port}".encode()

        s = socket.socket()
        s.connect(self.entry)
        s.send(data)
        s.close()
