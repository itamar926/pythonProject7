import socket
import threading
import random
import time
import sys
import json
from crypto_utils import Crypto
from packet import Packet


class Peer:
    def __init__(self, name, server_ip, my_ip):
        self.name = name
        self.server_ip = server_ip
        self.server_port = 9000
        self.client_ip = my_ip  # עכשיו ה-IP מוזן ידנית!
        self.listen_port = random.randint(10000, 20000)
        self.key = random.randint(1, 255)

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        time.sleep(0.5)
        self.register()

    def register(self):
        msg = f"REGISTER|{self.name}|{self.client_ip}|{self.listen_port}|{self.key}"
        self.send_raw(self.server_ip, self.server_port, msg.encode())
        print(f"[System] Registered successfully with MY IP: {self.client_ip}:{self.listen_port}")

    def send_raw(self, ip, port, data):
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((ip, port))
            s.send(data)
            s.close()
        except Exception as e:
            print(f"\n[!] Network Error: Could not send to {ip}:{port} - {e}")

    def send_message(self, target_name, message):
        try:
            s = socket.socket()
            s.connect((self.server_ip, self.server_port))
            s.send(f"GET_ROUTE|{self.name}|{target_name}".encode())
            route_data = s.recv(4096).decode()
            s.close()

            if route_data.startswith("ERROR"):
                print(f"\n[!] Server says: {route_data}")
                return
            route = json.loads(route_data)
            print(f"\n[Debug] Route received from server: {[n['name'] for n in route]}")
        except Exception as e:
            print(f"\n[!] Could not connect to directory server at {self.server_ip}: {e}")
            return

        packet = Packet(self.name, target_name, message)
        data = packet.encode()

        for i in range(len(route) - 1, -1, -1):
            node = route[i]
            data = Crypto.xor(data, node['key'])
            if i == len(route) - 1:
                header = b"FINAL"
            else:
                next_node = route[i + 1]
                header = f"{next_node['ip']}:{next_node['port']}".encode()

            data = header + b"|" + data

        first_node = route[0]
        print(
            f"[Debug] Sending Onion packet to first node: {first_node['name']} (IP: {first_node['ip']}:{first_node['port']})")
        self.send_raw(first_node['ip'], first_node['port'], data)

    def listen(self):
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()
        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(4096)
                conn.close()

                if not data: continue

                header_part, payload = data.split(b"|", 1)
                header = header_part.decode()
                decrypted = Crypto.xor(payload, self.key)

                if header == "FINAL":
                    sender, target, msg = Packet.decode(decrypted)
                    print(f"\n\n[New Message from {sender}]: {msg}")
                    print(f"{self.name}> ", end="", flush=True)
                else:
                    next_ip, next_port = header.split(":")
                    print(f"\n[Debug] I am a relay! Forwarding packet to {next_ip}:{next_port}...")
                    self.send_raw(next_ip, int(next_port), decrypted)
                    print(f"{self.name}> ", end="", flush=True)
            except Exception as e:
                pass


if __name__ == "__main__":
    server_ip = input("Enter Directory Server IP (e.g. 192.168.X.X): ")
    my_ip = input("Enter THIS computer's local IP (e.g. 192.168.X.X): ")
    name = input("Enter your name: ")

    p = Peer(name, server_ip, my_ip)
    p.start()
    print(f"Logged in as {name}. Format: TargetName|Message")
    while True:
        inp = input(f"{name}> ")
        if "|" in inp:
            target, msg = inp.split("|", 1)
            p.send_message(target, msg)