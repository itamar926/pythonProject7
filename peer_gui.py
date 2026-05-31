# peer_gui.py
import tkinter as tk
from tkinter import scrolledtext, simpledialog, ttk
import socket
import threading
import random
import time
import json
import sys

# ייבוא מ-3 קבצי התשתית שפירקנו
from crypto_utils import Crypto
from packet import Packet
from net_protocol import send_data, recv_data


class OnionChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.server_ip = simpledialog.askstring("Login", "Directory Server IP:", parent=self.root)
        if not self.server_ip: sys.exit()
        self.client_ip = simpledialog.askstring("Login", "THIS computer's IP:", parent=self.root)
        if not self.client_ip: sys.exit()
        self.name = simpledialog.askstring("Login", "Your Name:", parent=self.root)
        if not self.name: sys.exit()

        self.server_port = 9000
        self.listen_port = random.randint(10000, 20000)
        self.key = random.randint(1, 255)

        self.root.deiconify()
        self.root.title(f"Onion Chat - {self.name}")
        self.root.geometry("600x600")
        self.root.configure(bg="#1e1e1e")

        # אזור הצ'אט
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg="#2b2b2b", fg="white",
                                                   font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state="disabled")

        # פאנל שליטה (בחירת יעד וסוג רשת)
        control_frame = tk.Frame(self.root, bg="#1e1e1e")
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(control_frame, text="Send To:", fg="white", bg="#1e1e1e", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT, padx=(0, 5))
        self.target_combo = ttk.Combobox(control_frame, values=[], state="readonly", width=15, font=("Arial", 10))
        self.target_combo.pack(side=tk.LEFT, padx=(0, 10))

        self.refresh_btn = tk.Button(control_frame, text="🔄 Refresh", command=self.refresh_online_peers, bg="#333333",
                                     fg="white", font=("Arial", 9))
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 20))

        self.net_mode = tk.StringVar(value="TOR")
        public_rb = tk.Radiobutton(control_frame, text="Public (Tracked)", variable=self.net_mode, value="PUBLIC",
                                   bg="#1e1e1e", fg="#ffcc00", selectcolor="#1e1e1e", font=("Arial", 10, "bold"))
        public_rb.pack(side=tk.LEFT, padx=(0, 15))

        tor_rb = tk.Radiobutton(control_frame, text="Tor (Anonymous)", variable=self.net_mode, value="TOR",
                                bg="#1e1e1e", fg="#00ff00", selectcolor="#1e1e1e", font=("Arial", 10, "bold"))
        tor_rb.pack(side=tk.LEFT)

        # אזור כתיבת ההודעה
        bottom_frame = tk.Frame(self.root, bg="#1e1e1e")
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.msg_entry = tk.Entry(bottom_frame, font=("Arial", 12), bg="#3c3c3c", fg="white", insertbackground="white")
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.handle_send)

        self.send_btn = tk.Button(bottom_frame, text="Send", command=self.handle_send, bg="#007acc", fg="white",
                                  font=("Arial", 10, "bold"))
        self.send_btn.pack(side=tk.RIGHT)

        threading.Thread(target=self.listen, daemon=True).start()
        time.sleep(0.5)
        self.register()

        threading.Thread(target=self.auto_refresh_loop, daemon=True).start()

        self.log_sys(f"Logged in successfully as '{self.name}'.", "#00aaff")

    def log_sys(self, msg, color="#888888"):
        self.root.after(0, self._append_text, f"[System] {msg}\n", color)

    def log_msg(self, sender, msg, is_me=False):
        color = "#ffcc00" if is_me else "#00ff00"
        prefix = "You" if is_me else sender
        self.root.after(0, self._append_text, f"[{prefix}]: {msg}\n", color)

    def _append_text(self, text, color):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, text, color)
        self.chat_area.tag_config(color, foreground=color)
        self.chat_area.see(tk.END)
        self.chat_area.config(state="disabled")

    def auto_refresh_loop(self):
        while True:
            self.refresh_online_peers(silent=True)
            time.sleep(3)

    def refresh_online_peers(self, silent=False):
        try:
            s = socket.socket()
            s.connect((self.server_ip, self.server_port))
            send_data(s, b"GET_ONLINE_PEERS")
            response = recv_data(s).decode()
            s.close()

            peers_dict = json.loads(response)
            peer_names = [peer_name for peer_name in peers_dict.keys() if peer_name != self.name]

            current_selection = self.target_combo.get()
            self.target_combo['values'] = peer_names

            if current_selection in peer_names:
                self.target_combo.set(current_selection)
            elif peer_names and not current_selection:
                self.target_combo.current(0)

            if not silent:
                self.log_sys("Online users list updated.", "#aaaaaa")
        except Exception:
            if not silent:
                self.log_sys("Failed to refresh online users list.", "#ff5555")

    def handle_send(self, event=None):
        msg = self.msg_entry.get().strip()
        target = self.target_combo.get()

        if not target:
            self.log_sys("Error: No target user selected. Connect other peers first.", "#ff5555")
            return
        if not msg: return

        self.msg_entry.delete(0, tk.END)
        self.log_msg(f"To {target}", msg, is_me=True)
        threading.Thread(target=self.send_message, args=(target, msg), daemon=True).start()

    def register(self):
        msg = f"REGISTER|{self.name}|{self.client_ip}|{self.listen_port}|{self.key}"
        self.send_raw(self.server_ip, self.server_port, msg.encode())

    def send_raw(self, ip, port, data):
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((ip, port))
            send_data(s, data)
            s.close()
        except Exception:
            self.log_sys(f"Network Error: Could not forward payload to {ip}:{port}", "#ff5555")

    def send_message(self, target_name, message):
        mode = self.net_mode.get()
        try:
            s = socket.socket()
            s.connect((self.server_ip, self.server_port))
            send_data(s, f"GET_ROUTE|{self.name}|{target_name}|{mode}".encode())
            route_data_raw = recv_data(s)
            s.close()

            route_data = route_data_raw.decode()
            if route_data.startswith("ERROR"):
                self.log_sys(f"Server: {route_data}", "#ff5555")
                return
            route = json.loads(route_data)
            self.log_sys(f"Route Chosen ({mode} Mode): {' -> '.join([n['name'] for n in route])}")
        except Exception:
            self.log_sys("Directory Server unreachable.", "#ff5555")
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
        self.log_sys(f"Sending first layer to {first_node['name']}...")
        self.send_raw(first_node['ip'], first_node['port'], data)

    def listen(self):
        server = socket.socket()
        server.bind(("0.0.0.0", self.listen_port))
        server.listen()
        while True:
            try:
                conn, _ = server.accept()
                payload = recv_data(conn)
                conn.close()
                if not payload: continue

                header_part, enc_data = payload.split(b"|", 1)
                header = header_part.decode()
                decrypted = Crypto.xor(enc_data, self.key)

                if header == "FINAL":
                    sender, target, msg = Packet.decode(decrypted)
                    self.log_msg(sender, msg, is_me=False)
                else:
                    next_ip, next_port = header.split(":")
                    self.log_sys(f"Relay: Forwarding to {next_ip}:{next_port}...")
                    self.send_raw(next_ip, int(next_port), decrypted)
            except:
                pass


if __name__ == "__main__":
    app = OnionChatGUI()
    app.root.mainloop()