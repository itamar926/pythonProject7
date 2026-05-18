import tkinter as tk
from tkinter import scrolledtext, simpledialog
import socket
import threading
import random
import time
import json
import sys
from crypto_utils import Crypto
from packet import Packet
from net_protocol import send_data, recv_data  # שימוש בפרוטוקול החדש


class OnionChatGUI:
    def __init__(self):
        # יצירת חלון מוסתר זמנית עבור חלוניות הקלט
        self.root = tk.Tk()
        self.root.withdraw()

        # חלוניות קופצות לאיסוף נתוני התחברות
        self.server_ip = simpledialog.askstring("Login", "Directory Server IP:", parent=self.root)
        if not self.server_ip: sys.exit()
        self.client_ip = simpledialog.askstring("Login", "THIS computer's IP:", parent=self.root)
        if not self.client_ip: sys.exit()
        self.name = simpledialog.askstring("Login", "Your Name:", parent=self.root)
        if not self.name: sys.exit()

        # הגדרות רשת ומפתח הצפנה אקראי
        self.server_port = 9000
        self.listen_port = random.randint(10000, 20000)
        self.key = random.randint(1, 255)

        # עיצוב החלון הראשי
        self.root.deiconify()
        self.root.title(f"Onion Chat - {self.name}")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e")

        # אזור תצוגת הצ'אט
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg="#2b2b2b", fg="white",
                                                   font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state="disabled")

        # אזור הקלדת הודעות
        bottom_frame = tk.Frame(self.root, bg="#1e1e1e")
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.msg_entry = tk.Entry(bottom_frame, font=("Arial", 12), bg="#3c3c3c", fg="white", insertbackground="white")
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.handle_send)

        self.send_btn = tk.Button(bottom_frame, text="Send", command=self.handle_send, bg="#007acc", fg="white",
                                  font=("Arial", 10, "bold"))
        self.send_btn.pack(side=tk.RIGHT)

        # הפעלת שרת ההאזנה המקומי ברקע ורישום בשרת המרכזי
        threading.Thread(target=self.listen, daemon=True).start()
        time.sleep(0.5)
        self.register()

        self.log_sys(f"Logged in successfully as '{self.name}'.", "#00aaff")

    def log_sys(self, msg, color="#888888"):
        """ הדפסת הודעות מערכת וניתובים באפור/תכלת """
        self.root.after(0, self._append_text, f"[System] {msg}\n", color)

    def log_msg(self, sender, msg, is_me=False):
        """ הדפסת הודעות צ'אט בצבעים בולטים """
        color = "#ffcc00" if is_me else "#00ff00"
        prefix = "You" if is_me else sender
        self.root.after(0, self._append_text, f"[{prefix}]: {msg}\n", color)

    def _append_text(self, text, color):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, text, color)
        self.chat_area.tag_config(color, foreground=color)
        self.chat_area.see(tk.END)
        self.chat_area.config(state="disabled")

    def handle_send(self, event=None):
        raw_text = self.msg_entry.get().strip()
        if not raw_text: return
        self.msg_entry.delete(0, tk.END)

        if "|" not in raw_text:
            self.log_sys("Format: TargetName|Message", "#ff5555")
            return

        target, msg = raw_text.split("|", 1)
        self.log_msg(f"To {target}", msg, is_me=True)
        threading.Thread(target=self.send_message, args=(target, msg), daemon=True).start()

    def register(self):
        """ רישום ראשוני מול השרת המרכזי """
        msg = f"REGISTER|{self.name}|{self.client_ip}|{self.listen_port}|{self.key}"
        self.send_raw(self.server_ip, self.server_port, msg.encode())

    def send_raw(self, ip, port, data):
        """ שליחת מידע גולמי לכתובת יעד באמצעות פרוטוקול אורך קבוע """
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((ip, port))
            send_data(s, data)  # שימוש ב-Length Prefix
            s.close()
        except Exception as e:
            self.log_sys(f"Network Error: Could not connect to {ip}:{port}", "#ff5555")

    def send_message(self, target_name, message):
        """ בקשת מסלול מהשרת, אריזת הבצל ושליחתו לתחנה הראשונה """
        try:
            s = socket.socket()
            s.connect((self.server_ip, self.server_port))
            send_data(s, f"GET_ROUTE|{self.name}|{target_name}".encode())
            route_data_raw = recv_data(s)
            s.close()

            route_data = route_data_raw.decode()
            if route_data.startswith("ERROR"):
                self.log_sys(f"Server: {route_data}", "#ff5555")
                return
            route = json.loads(route_data)
            self.log_sys(f"Route Chosen: {' -> '.join([n['name'] for n in route])}")
        except Exception as e:
            self.log_sys("Directory Server unreachable.", "#ff5555")
            return

        # יצירת חבילת המידע המקורית
        packet = Packet(self.name, target_name, message)
        data = packet.encode()

        # אריזת השכבות מהסוף להתחלה (בצל)
        for i in range(len(route) - 1, -1, -1):
            node = route[i]
            data = Crypto.xor(data, node['key'])
            if i == len(route) - 1:
                header = b"FINAL"
            else:
                next_node = route[i + 1]
                header = f"{next_node['ip']}:{next_node['port']}".encode()
            data = header + b"|" + data

        # שליחה לתחנה הראשונה במסלול
        first_node = route[0]
        self.log_sys(f"Sending first layer to {first_node['name']}...")
        self.send_raw(first_node['ip'], first_node['port'], data)

    def listen(self):
        """ שרת מקומי המאזין להודעות נכנסות (בין אם להעברה ובין אם כיעד סופי) """
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()
        while True:
            try:
                conn, _ = server.accept()
                payload = recv_data(conn)  # קריאה מאובטחת לפי אורך החבילה
                conn.close()
                if not payload: continue

                # פירוק הכותרת ופענוח השכבה החיצונית ביותר
                header_part, enc_data = payload.split(b"|", 1)
                header = header_part.decode()
                decrypted = Crypto.xor(enc_data, self.key)

                if header == "FINAL":
                    # הגענו ליעד הסופי - מציגים את ההודעה המקורית
                    sender, target, msg = Packet.decode(decrypted)
                    self.log_msg(sender, msg, is_me=False)
                else:
                    # תחנת ביניים - קילוף שכבה והעברה הלאה במסלול
                    next_ip, next_port = header.split(":")
                    self.log_sys(f"Relay: Forwarding to {next_ip}:{next_port}...")
                    self.send_raw(next_ip, int(next_port), decrypted)
            except:
                pass


if __name__ == "__main__":
    app = OnionChatGUI()
    app.root.mainloop()