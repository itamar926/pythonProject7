import socket
import threading
import json
import random

HOST = "0.0.0.0"
PORT = 9000

active_peers = {}  # מילון: {name: {"ip": ip, "port": port, "key": key}}


def handle_client(conn):
    try:
        data = conn.recv(4096).decode('utf-8')
        if not data: return
        parts = data.split("|")
        command = parts[0]

        if command == "REGISTER":
            name, ip, port, key = parts[1], parts[2], int(parts[3]), int(parts[4])
            active_peers[name] = {"ip": ip, "port": port, "key": key}
            print(f"[+] Registered: {name} ({ip}:{port})")

        elif command == "GET_ROUTE":
            sender_name, target_name = parts[1], parts[2]
            if target_name not in active_peers:
                conn.send(b"ERROR|Target not found")
                return

            # בחירת תחנות ביניים (כל מי שהוא לא השולח ולא היעד)
            others = [info for name, info in active_peers.items() if name != target_name and name != sender_name]
            # הגרלת 2 תחנות ביניים (או פחות אם אין מספיק אנשים)
            intermediates = random.sample(others, min(len(others), 2))

            # בניית המסלול: תחנות ביניים ובסוף היעד
            route = intermediates + [active_peers[target_name]]
            conn.send(json.dumps(route).encode('utf-8'))

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        conn.close()


def start_server():
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen()
    print(f"Directory Server running on port {PORT}...")
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    start_server()