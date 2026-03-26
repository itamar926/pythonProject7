import socket
import threading
import time
from crypto_utils import Crypto
from packet import Packet


class Client:
    def __init__(self, name, server_host, server_port, listen_port, client_ip="127.0.0.1", keys=None):
        self.name = name
        self.server_host = server_host
        self.server_port = server_port
        self.listen_port = listen_port
        self.client_ip = client_ip

        # סדר שכבות Onion
        self.keys = keys if keys else [33, 22, 11]

    def start(self):
        # 1. מפעילים את ההאזנה ברקע
        threading.Thread(target=self.listen, daemon=True).start()

        # 2. מחכים חצי שנייה כדי לוודא שהפורט באמת נפתח
        time.sleep(0.5)

        # 3. נרשמים בשרת
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
        except Exception as e:
            print(f"\n[Network Error] Failed to connect to entry node: {e}")
        finally:
            s.close()

    def listen(self):
        server = socket.socket()
        try:
            # שינוי קריטי: מאזינים ספציפית ל-127.0.0.1 כדי שווינדוס לא יחסום
            server.bind((self.client_ip, self.listen_port))
            server.listen()
            # הדפסה שתאשר לנו שהלקוח באמת מוכן לקבל הודעות
            print(f"\n[System] Client '{self.name}' is actively listening on port {self.listen_port}...")
        except Exception as e:
            print(f"\n[Fatal Error] Could not start listener on port {self.listen_port}: {e}")
            return

        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(4096)
                conn.close()

                if not data:
                    continue

                try:
                    sender, target, msg = Packet.decode(data)
                except Exception as e:
                    print(f"\n[Decode Error] Failed to read message: {e}")
                    continue

                if hasattr(self, "on_message"):
                    self.on_message(sender, msg)
                else:
                    # מסדר את ההדפסה בטרמינל כדי שלא תשבור את ההקלדה
                    print(f"\n[{sender}] > {msg}\n{self.name}> ", end="", flush=True)

            except Exception as e:
                print(f"\n[Listener Error] Something went wrong: {e}")