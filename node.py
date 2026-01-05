import socket
from crypto_utils import Crypto


class Node:
    def __init__(self, host: str, port: int, key: bytes, name: str):
        self.host = host
        self.port = port
        self.key = key
        self.name = name

    def start(self):
        server = socket.socket()
        # מאפשר שימוש חוזר בפורט ב‑Windows
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"{self.name} listening on {self.host}:{self.port}")

        while True:
            conn, addr = server.accept()
            data = conn.recv(4096)
            if not data:
                conn.close()
                continue

            decrypted = Crypto.xor_decrypt(data, self.key)

            try:
                next_ip, next_port, payload = decrypted.split(b"|", 2)
                next_ip = next_ip.decode()
                next_port = int(next_port.decode())

                print(f"{self.name} received message, forwarding to {next_ip}:{next_port}")

                s = socket.socket()
                s.connect((next_ip, next_port))
                s.send(payload)
                s.close()
            except ValueError:
                # זה השלב האחרון
                print(f"{self.name} reached final payload:", decrypted.decode())

            conn.close()
