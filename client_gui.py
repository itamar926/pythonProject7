import socket
import threading
import tkinter as tk
from crypto_utils import Crypto
from config import NODES, KEYS

class GUIClient:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect(NODES[0])  # מתחבר ל-Node הראשון

        self.root = tk.Tk()
        self.root.title("Tor-like Chat")
        self.root.geometry("500x400")

        self.text_area = tk.Text(self.root, state='disabled', wrap='word')
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self.root)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        t = threading.Thread(target=self.receive_messages, daemon=True)
        t.start()

        self.root.mainloop()

    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg.strip():
            return
        data = Crypto.encode_message(msg)

        # שכבות XOR לפי Nodes
        for key in reversed(KEYS):
            data = Crypto.xor(data, key)

        self.sock.send(data)
        self.display_message(f"You: {msg}")
        self.entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    continue
                try:
                    message = Crypto.decode_message(data)
                except:
                    message = str(data)
                self.display_message(f"Other: {message}")
            except:
                pass

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state='disabled')
        self.text_area.see(tk.END)
