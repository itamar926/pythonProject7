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

            # Apply XOR layers
            for k in self.keys:
                data = Crypto.xor(data, k)

            try:
                from_client, msg = Packet.decode(data)
            except:
                from_client, msg = "Unknown", data.decode(errors="ignore")

            if hasattr(self, "on_message"):
                self.on_message(from_client, msg)
            else:
                print(f"{from_client}> {msg}")

    def send(self, message, target_port=None):
        data = Packet(self.name, message).encode()
        for k in reversed(self.keys):
            data = Crypto.xor(data, k)
        s = socket.socket()
        s.connect(self.entry)
        s.send(data)
        s.close()
