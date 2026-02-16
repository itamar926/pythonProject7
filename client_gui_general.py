import tkinter as tk
from tkinter import simpledialog
import queue
from client import Client
from packet import Packet

ENTRY_IP = "192.168.1.37"  # ה-IP של ה-Nodes
ENTRY_PORT = 9010
KEYS = [11, 22, 33]

# === התחברות משתמש ===
root_prompt = tk.Tk()
root_prompt.withdraw()
username = simpledialog.askstring("Username", "Enter username:")
listen_port = simpledialog.askinteger("Port", "Enter unique port (9100+):")
root_prompt.destroy()


class ChatGUI:
    def __init__(self, name):
        self.name = name
        self.msg_queue = queue.Queue()

        self.client = Client(name, ENTRY_IP, ENTRY_PORT, listen_port, KEYS)
        self.client.on_message = lambda s, m: self.msg_queue.put((s, m))

        # ==== חלון ראשי ====
        self.root = tk.Tk()
        self.root.title(f"Tor Chat - {name}")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")

        # ==== אזור צ'אט ====
        self.chat_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.chat_frame, bg="#1e1e1e", highlightthickness=0)
        self.scroll = tk.Scrollbar(self.chat_frame, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.messages_frame = tk.Frame(self.canvas, bg="#1e1e1e")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # ==== רשימת משתמשים ====
        self.users_frame = tk.Frame(self.root, bg="#252526", width=200)
        self.users_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.users_frame, text="Users", bg="#252526", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)

        self.users = tk.Listbox(self.users_frame, bg="#1e1e1e", fg="white", selectbackground="#007acc")
        self.users.pack(fill=tk.BOTH, expand=True, padx=10)

        # ==== אזור הקלדה ====
        bottom = tk.Frame(self.root, bg="#1e1e1e")
        bottom.pack(fill=tk.X, padx=10, pady=10)

        self.entry = tk.Entry(bottom, font=("Segoe UI", 12), bg="#2d2d30", fg="white", insertbackground="white")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.send_message)

        send_btn = tk.Button(bottom, text="Send", bg="#007acc", fg="white",
                             font=("Segoe UI", 10, "bold"), command=self.send_message)
        send_btn.pack(side=tk.RIGHT)

        self.root.after(100, self.process_queue)
        self.register()
        self.root.mainloop()

    # ==== הצגת הודעה כבועה ====
    def bubble(self, sender, message):
        frame = tk.Frame(self.messages_frame, bg="#1e1e1e")

        is_me = sender == self.name
        bg = "#007acc" if is_me else "#3c3c3c"
        anchor = "e" if is_me else "w"

        label = tk.Label(
            frame,
            text=f"{sender}: {message}",
            bg=bg,
            fg="white",
            wraplength=400,
            justify="left",
            font=("Segoe UI", 10),
            padx=10,
            pady=6
        )

        label.pack(anchor=anchor, pady=4)
        frame.pack(fill=tk.BOTH, expand=True)

        self.canvas.yview_moveto(1.0)

    # ==== Queue מה-client ====
    def process_queue(self):
        while not self.msg_queue.empty():
            s, m = self.msg_queue.get()
            self.bubble(s, m)
        self.root.after(100, self.process_queue)

    # ==== שליחה ====
    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg:
            return

        self.entry.delete(0, tk.END)

        target = "ALL"
        selection = self.users.curselection()
        if selection:
            target = self.users.get(selection[0])

        pkt = Packet(self.name, target, msg).encode()
        self.client.send(pkt)

    # ==== רישום למערכת ====
    def register(self):
        pkt = Packet(self.name, "ALL", f"REGISTER:{listen_port}").encode()
        data = pkt
        from crypto_utils import Crypto
        for k in reversed(KEYS):
            data = Crypto.xor(data, k)

        import socket
        s = socket.socket()
        s.connect((ENTRY_IP, ENTRY_PORT))
        s.send(data)
        s.close()


ChatGUI(username)
