import socket
import threading
import random
import time
import sys
import json
from crypto_utils import Crypto
from packet import Packet


class Peer:
    def __init__(self, name):
        self.name = name
        self.server_ip = "127.0.0.1"
        self.server_port = 9000
        self.listen_port = random.randint(10000, 20000)
        self.key = random.randint(1, 255)  # מפתח הצפנה פשוט לכל peer

    def start(self):
        # האזנה להודעות נכנסות
        threading.Thread(target=self.listen, daemon=True).start()
        time.sleep(0.5)
        # רישום בשרת
        self.register()

    def register(self):
        msg = f"REGISTER|{self.name}|127.0.0.1|{self.listen_port}|{self.key}"
        self.send_raw(self.server_ip, self.server_port, msg.encode())

    def send_raw(self, ip, port, data):
        try:
            s = socket.socket()
            s.connect((ip, port))
            s.send(data)
            s.close()
        except:
            pass

    def send_message(self, target_name, message):
        # 1. בקשת מסלול מהשרת
        try:
            s = socket.socket()
            s.connect((self.server_ip, self.server_port))
            s.send(f"GET_ROUTE|{self.name}|{target_name}".encode())
            route_data = s.recv(4096).decode()
            s.close()

            if route_data.startswith("ERROR"):
                print("[!] Target user not found.")
                return
            route = json.loads(route_data)
        except:
            print("[!] Could not connect to server.")
            return

        # 2. בניית ה"בצל" (Onion) מהסוף להתחלה
        # השכבה הפנימית ביותר: ההודעה עצמה
        packet = Packet(self.name, target_name, message)
        data = packet.encode()

        # עטיפה בשכבות לפי המסלול (בסדר הפוך)
        for i in range(len(route) - 1, -1, -1):
            node = route[i]
            # הצפנה עם המפתח של אותה תחנה
            data = Crypto.xor(data, node['key'])
            # הוספת "כתובת היעד הבא" עבור התחנה הזו
            if i == len(route) - 1:  # התחנה האחרונה
                header = b"FINAL"
            else:
                next_node = route[i + 1]
                header = f"{next_node['ip']}:{next_node['port']}".encode()

            data = header + b"|" + data

        # 3. שליחה לתחנה הראשונה במסלול
        first_node = route[0]
        self.send_raw(first_node['ip'], first_node['port'], data)

    def listen(self):
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()
        while True:
            conn, _ = server.accept()
            data = conn.recv(4096)
            conn.close()

            # "קילוף" השכבה שלי
            decrypted = Crypto.xor(data.split(b"|", 1)[1], self.key)
            header = data.split(b"|", 1)[0].decode()

            if header == "FINAL":
                # אני היעד הסופי!
                sender, _, msg = Packet.decode(decrypted)
                print(f"\n[New Message from {sender}]: {msg}")
                print(f"{self.name}> ", end="", flush=True)
            else:
                # אני תחנת ביניים - מעביר הלאה
                next_ip, next_port = header.split(":")
                self.send_raw(next_ip, int(next_port), decrypted)


if __name__ == "__main__":
    name = input("Enter your name: ")
    p = Peer(name)
    p.start()
    print(f"Logged in as {name}. Format: Name|Message")
    while True:
        inp = input(f"{name}> ")
        if "|" in inp:
            target, msg = inp.split("|", 1)
            p.send_message(target, msg)