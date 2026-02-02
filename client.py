import socket
import threading
from crypto_utils import Crypto
from packet import Packet


class Client:
    def __init__(self, name, entry_ip, entry_port, listen_port, keys):
        self.name = name
        self.entry_ip = entry_ip
        self.entry_port = entry_port
        self.listen_port = listen_port
        self.keys = keys

        threading.Thread(target=self.listen, daemon=True).start()

    def send(self, raw_packet_bytes: bytes):
        data = raw_packet_bytes

        # הצפנת onion
        for k in reversed(self.keys):
            data = Crypto.xor(data, k)

        s = socket.socket()
        s.connect((self.entry_ip, self.entry_port))
        s.send(data)
        s.close()

    def listen(self):
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()

        while True:
            conn, _ = server.accept()
            data = conn.recv(4096)
            conn.close()

            # פענוח כל השכבות
            for k in self.keys:
                data = Crypto.xor(data, k)

            sender, target, msg = Packet.decode(data)

            if hasattr(self, "on_message"):
                self.on_message(sender, msg)
            else:
                print(f"{sender}> {msg}")
