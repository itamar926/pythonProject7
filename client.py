import socket
from crypto_utils import Crypto
from config import NODES

class Client:
    def __init__(self, nodes: list, keys: list):
        self.nodes = nodes
        self.keys = keys

    def send_message(self, message: str):
        payload = message.encode()

        # בונים Onion layers
        for i in reversed(range(len(self.nodes))):
            ip, port = self.nodes[i]
            payload = Crypto.xor_encrypt(
                ip.encode() + b"|" + str(port).encode() + b"|" + payload,
                self.keys[i]
            )

        first_ip, first_port = self.nodes[0]
        print(f"Client sending message to first node {first_ip}:{first_port}")
        s = socket.socket()
        s.connect((first_ip, first_port))
        s.send(payload)
        s.close()
