import tkinter as tk
from client import Client

class ChatGUI:
    def __init__(self, name, entry_ip, entry_port, listen_port, keys, target_port):
        self.name = name
        self.target_port = target_port

        self.client = Client(
            name=name,
            entry_ip=entry_ip,
            entry_port=entry_port,
            listen_port=listen_port,
            keys=keys
        )

        self.root = tk.Tk()
        self.root.title(f"Tor Chat - {name}")

        self.chat_box = tk.Text(self.root, height=15, width=50, state="disabled")
        self.chat_box.pack(padx=10, pady=10)

        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT, padx=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=10)

        # חיבור הדפסות של Client ל-GUI
        self.client.on_message = self.display_message

        self.root.mainloop()

    def display_message(self, sender, message):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, f"{sender}: {message}\n")
        self.chat_box.config(state="disabled")

    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg:
            return

        self.entry.delete(0, tk.END)
        self.display_message(self.name, msg)
        self.client.send(msg, self.target_port)
