import tkinter as tk
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
        self.root.title("Directory Server - Network Radar")
        self.root.geometry("800x600")
        self.root.configure(bg="#121212")

        # לוח הציור (Canvas) שעליו נצייר את המחשבים
        self.canvas = tk.Canvas(self.root, bg="#121212", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.active_peers = {}
        self.nodes_coords = {}  # שומר את המיקומים (X,Y) של כל מחשב

        # הפעלת השרת ברקע
        threading.Thread(target=self.start_server, daemon=True).start()

    def update_nodes_display(self):
        """ מצייר מחדש את כל המחשבים המחוברים במעגל """
        self.canvas.delete("node")
        self.canvas.delete("text")

        num_nodes = len(self.active_peers)
        if num_nodes == 0: return

        center_x, center_y = 400, 300
        radius = 200
        angle_step = 2 * math.pi / num_nodes

        for i, name in enumerate(self.active_peers.keys()):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.nodes_coords[name] = (x, y)

            # ציור המחשב (כדור כחול) והשם שלו
            self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="#007acc", outline="white", width=2,
                                    tags="node")
            self.canvas.create_text(x, y + 40, text=name, fill="white", font=("Arial", 11, "bold"), tags="text")

    def draw_route(self, sender, route):
        """ מצייר את מסלול ההודעה בין המחשבים """
        self.canvas.delete("line")

        # הרכבת רשימת המחשבים שההודעה עוברת בהם
        path = [sender] + [n['name'] for n in route]

        for i in range(len(path) - 1):
            n1, n2 = path[i], path[i + 1]
            if n1 in self.nodes_coords and n2 in self.nodes_coords:
                x1, y1 = self.nodes_coords[n1]
                x2, y2 = self.nodes_coords[n2]

                # ציור חץ צהוב זוהר מנתיב לנתיב
                self.canvas.create_line(x1, y1, x2, y2, fill="#ffcc00", width=4, arrow=tk.LAST, tags="line")

        # מוחק את החיצים אחרי 4 שניות
        self.root.after(4000, lambda: self.canvas.delete("line"))

    def handle_client(self, conn):
        try:
            # שימוש בפרוטוקול החדש שלנו לקריאת נתונים!
            raw = recv_data(conn)
            if not raw: return
            data = raw.decode('utf-8')
            parts = data.split("|")
            command = parts[0]

            if command == "REGISTER":
                name, ip, port, key = parts[1], parts[2], int(parts[3]), int(parts[4])
                self.active_peers[name] = {"name": name, "ip": ip, "port": port, "key": key}
                # עדכון המסך הגרפי
                self.root.after(0, self.update_nodes_display)

            elif command == "GET_ROUTE":
                sender_name, target_name = parts[1], parts[2]
                if target_name not in self.active_peers:
                    send_data(conn, b"ERROR|Target not found")
                    return

                others = [info for peer_name, info in self.active_peers.items() if
                          peer_name != target_name and peer_name != sender_name]
                num_hops = min(len(others), 3)
                intermediates = random.sample(others, num_hops)

                route = intermediates + [self.active_peers[target_name]]

                # שליחת התשובה ללקוח עם הפרוטוקול
                send_data(conn, json.dumps(route).encode('utf-8'))

                # ציור החיצים על מסך השרת!
                self.root.after(0, self.draw_route, sender_name, route)

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
    app = ServerGUI()
    app.root.mainloop()