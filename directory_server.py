# directory_server.py
import socket
import threading
import json
import random
import tkinter as tk
from tkinter import scrolledtext
import math

# ייבוא פרוטוקול הרשת המשותף
from net_protocol import send_data, recv_data

HOST = "0.0.0.0"
PORT = 9000
active_peers = {}  # name -> dict


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Onion Routing - Directory Server & Radar")
        self.root.geometry("700x600")
        self.root.configure(bg="#121212")

        title = tk.Label(root, text="👁️ ONION NETWORK DIRECTORY & RADAR", font=("Courier", 16, "bold"), fg="#00FF00",
                         bg="#121212")
        title.pack(pady=10)

        self.canvas = tk.Canvas(root, width=400, height=350, bg="#050505", highlightbackground="#00FF00",
                                highlightthickness=1)
        self.canvas.pack(pady=5)
        self.draw_radar_background()

        self.log_area = scrolledtext.ScrolledText(root, width=80, height=10, bg="#1a1a1a", fg="#00FF00",
                                                  font=("Consolas", 10))
        self.log_area.pack(pady=10, padx=10)

        # תיקון באג ה-bitmap (שימוש ב-foreground)
        self.log_area.tag_config("info", foreground="#00FF00")
        self.log_area.tag_config("warning", foreground="#FF3333")
        self.log_area.tag_config("route", foreground="#FFFF00")

        self.log("[*] Directory Server GUI initialized. Protocol synced with clients.")

    def draw_radar_background(self):
        self.canvas.delete("all")
        cx, cy = 200, 175
        for r in [50, 100, 140]:
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#004400", width=1)
        self.canvas.create_line(cx - 160, cy, cx + 160, cy, fill="#004400", width=1)
        self.canvas.create_line(cx, cy - 150, cx, cy + 150, fill="#004400", width=1)
        self.canvas.create_text(cx, cy, text="+", fill="#00FF00", font=("Courier", 12))

    def log(self, text, tag="info"):
        self.log_area.insert(tk.END, text + "\n", tag)
        self.log_area.see(tk.END)

    def update_radar(self):
        self.draw_radar_background()
        for name, peer in active_peers.items():
            x, y = peer["x"], peer["y"]
            self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#00FF00", outline="#FFFFFF")
            self.canvas.create_text(x, y - 15, text=name, fill="#FFFFFF", font=("Courier", 9, "bold"))

    def draw_route_line(self, path_nodes):
        self.canvas.delete("route")
        for i in range(len(path_nodes) - 1):
            p1 = path_nodes[i]
            p2 = path_nodes[i + 1]
            self.canvas.create_line(p1["x"], p1["y"], p2["x"], p2["y"], fill="#FFFF00", width=2, arrow=tk.LAST,
                                    tags="route")
        self.root.after(4000, lambda: self.canvas.delete("route"))


def handle_client(conn, app):
    try:
        raw_data = recv_data(conn)
        if not raw_data: return

        data = raw_data.decode('utf-8', errors='ignore')
        parts = data.split("|")
        command = parts[0]

        if command == "REGISTER":
            name, ip, port, key = parts[1], parts[2], int(parts[3]), int(parts[4])

            angle = random.uniform(0, 2 * math.pi)
            radius = 120
            x = int(200 + radius * math.cos(angle))
            y = int(175 + radius * math.sin(angle))

            active_peers[name] = {"name": name, "ip": ip, "port": port, "key": key, "x": x, "y": y}
            app.log(f"[+] Registered Peer: '{name}' from {ip}:{port} [Key: {key}]")
            app.update_radar()

        elif command == "GET_ONLINE_PEERS":
            send_data(conn, json.dumps(active_peers).encode('utf-8'))

        elif command == "GET_ROUTE":
            sender_name, target_name, mode = parts[1], parts[2], parts[3]
            if target_name not in active_peers:
                send_data(conn, b"ERROR|Target not found")
                return

            others = [info for p_name, info in active_peers.items() if p_name != target_name and p_name != sender_name]
            num_hops = min(len(others), 3)
            intermediates = random.sample(others, num_hops)

            route = intermediates + [active_peers[target_name]]
            send_data(conn, json.dumps(route).encode('utf-8'))

            path_names = [sender_name] + [n["name"] for n in route]
            path_str = " -> ".join(path_names)

            if mode == "PUBLIC":
                app.log(f"[🌐 PUBLIC ROUTE] {path_str}", "route")
                full_nodes_path = [active_peers[sender_name]] + route
                app.draw_route_line(full_nodes_path)
            else:
                app.log(f"[🔒 TOR WARNING] Route obfuscated by client! Path hidden on Radar.", "warning")

    except Exception as e:
        print(f"Server Error: {e}")
    finally:
        conn.close()


def start_socket_server(app):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    app.log(f"[+] Core Network Engine listening on port {PORT}...")
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn, app), daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    threading.Thread(start_socket_server, args=(app,), daemon=True).start()
    root.mainloop()