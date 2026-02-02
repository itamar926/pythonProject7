import tkinter as tk
from tkinter import simpledialog
from client import Client
from packet import Packet

ENTRY_IP = "127.0.0.1"
ENTRY_PORT = 9010
KEYS = [11, 22, 33]

# שם משתמש ופורט
root_prompt = tk.Tk()
root_prompt.withdraw()
username = simpledialog.askstring("Username", "Enter username:")
listen_port = simpledialog.askinteger("Port", "Enter unique port (9100+):")
root_prompt.destroy()

class ChatGUI:
    def __init__(self, name):
        self.name = name
        self.client = Client(name, ENTRY_IP, ENTRY_PORT, listen_port, KEYS)
        self.client.on_message = self.display_message

        self.root = tk.Tk()
        self.root.title(f"Tor Chat - {name}")

        self.chat = tk.Text(self.root, state="disabled", width=60, height=20)
        self.chat.pack(side=tk.LEFT)

        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self.users = tk.Listbox(right)
        self.users.pack()

        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack()
        self.entry.bind("<Return>", self.send_message)

        # REGISTER
        self.register()

        self.root.mainloop()

    def register(self):
        pkt = Packet(self.name, "ALL", f"REGISTER:{listen_port}").encode()
        data = pkt
        for k in reversed(KEYS):
            from crypto_utils import Crypto
            data = Crypto.xor(data, k)
        import socket
        s = socket.socket()
        s.connect((ENTRY_IP, ENTRY_PORT))
        s.send(data)
        s.close()

    def display_message(self, sender, message):
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"{sender}: {message}\n")
        self.chat.config(state="disabled")

    def send_message(self, event=None):
        msg = self.entry.get()
        self.entry.delete(0, tk.END)

        target = "ALL"
        selection = self.users.curselection()
        if selection:
            target = self.users.get(selection[0])

        self.client.send(Packet(self.name, target, msg).encode())

ChatGUI(username)
