import socket
from crypto_utils import Crypto

class Client:
    def __init__(self, nodes, keys):
        self.nodes = nodes
        self.keys = keys

    def send(self, message: str):
        data = message.encode()

        # בונים את ה‑Onion: מהאחרון לראשון
        for key in reversed(self.keys):
            data = Crypto.xor(data, key)

        ip, port = self.nodes[0]
        s = socket.socket()
        s.connect((ip, port))
        s.send(data)
        s.close()
