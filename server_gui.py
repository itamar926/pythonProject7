import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import json
import random
import math
from net_protocol import send_data, recv_data

HOST = "0.0.0.0"
PORT = 9000


class ServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Directory Server - Network Radar & Logs")
        self.root.geometry("900x700")
        self.root.configure(bg="#121212")

        # לוח הציור (Canvas) - תופס את החלק העליון
        self.canvas = tk.Canvas(self.root, bg="#121212", highlightthickness=0, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # אזור הלוגים של האדמין - תופס את החלק התחתון
        log_frame = tk.Frame(self.root, bg="#121212")
        log_frame.pack(fill=tk.X, padx=10, pady=10)

        log_label = tk.Label(log_frame, text="Admin Activity Logs:", fg="white", bg="#121212",
                             font=("Arial", 10, "bold"))
        log_label.pack(anchor=tk.W)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=12, bg="#1e1e1e", fg="#00ff00",
                                                  font=("Consolas", 10))
        self.log_area.pack(fill=tk.X, pady=(5, 0))
        self.log_area.config(state="disabled")

        self.active_peers = {}
        self.nodes_coords = {}

        threading.Thread(target=self.start_server, daemon=True).start()

    def log_admin(self, msg):
        """ פונקציית עזר להוספת שורת לוג למסך האדמין """
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[LOG] {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def update_nodes_display(self):
        self.canvas.delete("node")
        self.canvas.delete("text")

        num_nodes = len(self.active_peers)
        if num_nodes == 0: return

        center_x, center_y = 450, 200
        radius = 140
        angle_step = 2 * math.pi / num_nodes

        for i, name in enumerate(self.active_peers.keys()):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.nodes_coords[name] = (x, y)

            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="#007acc", outline="white", width=2,
                                    tags="node")
            self.canvas.create_text(x, y + 35, text=name, fill="white", font=("Arial", 10, "bold"), tags="text")

    def draw_route(self, sender, route):
        self.canvas.delete("line")
        path = [sender] + [n['name'] for n in route]

        for i in range(len(path) - 1):
            n1, n2 = path[i], path[i + 1]
            if n1 in self.nodes_coords and n2 in self.nodes_coords:
                x1, y1 = self.nodes_coords[n1]
                x2, y2 = self.nodes_coords[n2]
                self.canvas.create_line(x1, y1, x2, y2, fill="#ffcc00", width=4, arrow=tk.LAST, tags="line")

        self.root.after(4000, lambda: self.canvas.delete("line"))

    def handle_client(self, conn):
        try:
            raw = recv_data(conn)
            if not raw: return
            data = raw.decode('utf-8')
            parts = data.split("|")
            command = parts[0]

            if command == "REGISTER":
                name, ip, port, key = parts[1], parts[2], int(parts[3]), int(parts[4])
                self.active_peers[name] = {"name": name, "ip": ip, "port": port, "key": key}
                self.root.after(0, self.update_nodes_display)
                self.root.after(0, self.log_admin, f"New Node Registered: {name} ({ip}:{port})")

            elif command == "GET_ROUTE":
                # הפורמט החדש: GET_ROUTE|Sender|Target|NetworkType
                sender_name, target_name, net_type = parts[1], parts[2], parts[3]

                if target_name not in self.active_peers:
                    send_data(conn, b"ERROR|Target not found")
                    return

                # הגרלת מסלול
                others = [info for peer_name, info in self.active_peers.items() if
                          peer_name != target_name and peer_name != sender_name]
                num_hops = min(len(others), 3)
                intermediates = random.sample(others, num_hops)
                route = intermediates + [self.active_peers[target_name]]

                # שליחת המסלול חזרה ללקוח
                send_data(conn, json.dumps(route).encode('utf-8'))

                # לוג קבוע של אדמין (השולח והיעד תמיד חשופים לשרת המרכזי)
                log_msg = f"Message Request -> Sender: {sender_name} | Target: {target_name} | Mode: {net_type}"
                self.root.after(0, self.log_admin, log_msg)

                # ויזואליזציה על המפה על פי בחירת הלקוח
                if net_type == "PUBLIC":
                    self.root.after(0, self.draw_route, sender_name, route)
                    self.root.after(0, self.log_admin,
                                    f"  [Public Route Tracked]: {sender_name} -> {' -> '.join([n['name'] for n in route])}")
                else:
                    self.root.after(0, self.log_admin, f"  [Tor Mode]: Route hidden from Admin Radar.")

        except Exception as e:
            pass
        finally:
            conn.close()

    def start_server(self):
        server = socket.socket()
        server.bind((HOST, PORT))
        server.listen()
        while True:
            conn, _ = server.accept()
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    print("[Server] Starting the Radar GUI with Admin Logs...")
    app = ServerGUI()
    app.root.mainloop()