import socket
import threading
from crypto_utils import Crypto

class Node:
    def __init__(self, host, port, key, next_node=None, name="Node"):
        self.host = host
        self.port = port
        self.key = key
        self.next_node = next_node
        self.name = name
        self.clients = []  # חיבורי Clients שמקבלים הודעות

    def start(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()
        print(f"{self.name} listening on {self.host}:{self.port}")

        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=self.handle_connection, args=(conn,), daemon=True)
            t.start()

    def handle_connection(self, conn):
        # Node האחרון – שומר Clients שמחוברים
        if not self.next_node:
            if conn not in self.clients:
                self.clients.append(conn)

        try:
            data = conn.recv(4096)
            if not data:
                conn.close()
                return

            decrypted = Crypto.xor(data, self.key)

            if self.next_node:
                next_ip, next_port = self.next_node
                s = socket.socket()
                s.connect((next_ip, next_port))
                s.send(decrypted)
                s.close()
                print(f"{self.name} forwarded message")
            else:
                try:
                    message = Crypto.decode_message(decrypted)
                except:
                    message = str(decrypted)
                print(f"{self.name} FINAL MESSAGE: {message}")

                # שליחה לכל ה-Clients
                for c in self.clients:
                    try:
                        c.send(decrypted)
                    except:
                        pass

        except:
            pass
        finally:
            if self.next_node is None:
                # אל תמחק את conn – צריך אותו כדי לקבל חיבורים נוספים
                pass
            else:
                conn.close()
